from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json
from django import forms

from matrix import Matrix, MatrixEncoder, as_matrix

class JSONField(models.TextField):
    """JSONField is a generic textfield that neatly serializes/unserializes
    JSON objects seamlessly"""

    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        try:
            self.object_hook=kwargs["object_hook"]
            del kwargs["object_hook"]
        except KeyError as e:
            self.object_hook=None

        try:
            self.cls = kwargs["cls"]
            del kwargs["cls"]
        except KeyError as e:
            self.cls = DjangoJSONEncoder

        super(JSONField, self).__init__(*args, **kwargs)


    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""

        if value == "" or value == None:
            return None

        try:
            if isinstance(value, basestring):
                return json.loads(value, object_hook=self.object_hook) if self.object_hook else json.loads(value)
        except ValueError as e:
            pass

        return value

    def get_db_prep_save(self, value):
        """Convert our JSON object to a string before we save"""

        if value == "":
            return None

        try:
            value = json.dumps(value, cls=self.cls, check_circular=False)
        except Exception as e:
            print e
        return super(JSONField, self).get_db_prep_save(value)



class MatrixSet(models.Model):
    name = models.CharField(max_length=250)
    temp = models.BooleanField(default=True)
    creation = models.DateTimeField(auto_now_add=True)
    ec_matrix = JSONField("EC Matrix", cls=MatrixEncoder, object_hook=as_matrix)
    cf_matrix = JSONField("CF Matrix", cls=MatrixEncoder, object_hook=as_matrix)
    cfp_matrix = JSONField("CFP Matrix", cls=MatrixEncoder, object_hook=as_matrix)
    ef_matrix = JSONField("EF Matrix", cls=MatrixEncoder, object_hook=as_matrix)
    c1_matrix = JSONField("C1 Matrix", cls=MatrixEncoder, object_hook=as_matrix)
    c2_matrix = JSONField("C2 Matrix", cls=MatrixEncoder, object_hook=as_matrix)
    l1_matrix = JSONField("L1 Matrix", cls=MatrixEncoder, object_hook=as_matrix)
    l2_matrix = JSONField("L2 Matrix", cls=MatrixEncoder, object_hook=as_matrix)

    def get_c1_matrix(self):
        if not(self.c1_matrix):
            self.c1_matrix = self.ec_matrix.c1(self.cfp_matrix)
            self.save()
        return self.c1_matrix

    def get_c2_matrix(self):
        if not(self.c1_matrix):
            self.c2_matrix = self.ec_matrix.c2(self.cfp_matrix)
            self.save()
        return self.c2_matrix

    def get_l1_matrix(self):
        if not(self.l1_matrix):
            self.l1_matrix = self.ef_matrix.l1()
            self.save()
        return self.l1_matrix

    def get_l2_matrix(self):
        pass

    def run_fever_chart(self, pd, functions):
        pds = {"hss": lambda: (self.get_c1_matrix(), self.get_l1_matrix()),
               "hs": lambda: (self.get_c1_matrix(), self.get_l2_matrix()),
               "uss": lambda: (self.get_c2_matrix(), self.get_l1_matrix()),
               "us": lambda: (self.get_c2_matrix(), self.get_l2_matrix())}
        c,l = pds[pd]()
        return Matrix.run_fever_chart(c, l, functions)

    def run_report(self, pd, functions):
        pds = {"hss": lambda: (self.get_c1_matrix(), self.get_l1_matrix()),
               "hs": lambda: (self.get_c1_matrix(), self.get_l2_matrix()),
               "uss": lambda: (self.get_c2_matrix(), self.get_l1_matrix()),
               "us": lambda: (self.get_c2_matrix(), self.get_l2_matrix())}
        c,l = pds[pd]()
        return Matrix.run_report(c, l, functions)

class MatrixUploadFileForm(forms.ModelForm):
    class Meta:
        model = MatrixSet
        fields = ('name',)
        
    ec_matrix = forms.FileField(label="EC Matrix")
    cf_matrix = forms.FileField(label="CF Matrix", required=False)
    cfp_matrix = forms.FileField(label="CF' Matrix")
    ef_matrix = forms.FileField(label="EF Matrix", required=False)

    
    def matrix_clean(self, matrix):
        cl = self.cleaned_data.get(matrix)
        if cl:
            try:
                return Matrix.from_excel_file(cl)
            except (Exception, ) as e:
                print e
                raise forms.ValidationError(e)
        return None
    
    def clean_ec_matrix(self):
        return self.matrix_clean("ec_matrix")

    def clean_cf_matrix(self):
        return self.matrix_clean("cf_matrix")

    def clean_cfp_matrix(self):
        return self.matrix_clean("cfp_matrix")

    def clean_ef_matrix(self):
        return self.matrix_clean("ef_matrix")

    def clean(self):
        if any(self.errors):
            return

        def check_dims(m1, d1, m2, d2):
            if self.cleaned_data.get(m1,'').__dict__[d1] != self.cleaned_data.get(m2, '').__dict__[d2]:
                raise forms.ValidationError(("%s of %s is not equal to %s of %s." %
                                              (d1, m1, d2, m2)).title())

        check_dims("ec_matrix", "width", "cfp_matrix", "height")

        if not(self.cleaned_data.get('cf_matrix')):
            """
            We better have the ef_matrix
            """
            if not(self.cleaned_data.get('ef_matrix')):
                raise forms.ValidationError("Need one of either CF Matrix or EF Matrix")
        else:
            check_dims("cf_matrix", "width", "cfp_matrix", "width")
            check_dims("cf_matrix", "height", "cfp_matrix", "height")
                
        if not(self.cleaned_data.get('ef_matrix')):
            """
            We are going to build the ef matrix
            """
            cf = self.cleaned_data.get('cf_matrix')
            ec = self.cleaned_data.get('ec_matrix')
            try:
                self.cleaned_data['ef_matrix'] =  ec.mult(cf)
            except Exception as e:
                raise forms.ValidationError(e)
        else:
            check_dims("ec_matrix", "height", "ef_matrix", "height")
            check_dims("cfp_matrix", "width", "ef_matrix", "width")

        return self.cleaned_data

    def save(self):
        matrix = MatrixSet(**self.cleaned_data)
        matrix.save()
        return matrix

def matrix_select_from_model(pk):
    matrix = MatrixSet.objects.get(pk=pk)
    func_choices = list(enumerate(matrix.ec_matrix.rows))

    class MatrixSelectFunctionsForm(forms.Form):
        choices = forms.MultipleChoiceField(choices=func_choices)

    return MatrixSelectFunctionsForm
        
            
