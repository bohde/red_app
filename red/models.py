from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json
from django import forms

from rbco.msexcel import xls_to_excelerator_dict as xls
from itertools import count, takewhile

class JSONField(models.TextField):
    """JSONField is a generic textfield that neatly serializes/unserializes
    JSON objects seamlessly"""

    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""

        if value == "":
            return None

        try:
            if isinstance(value, basestring):
                return json.loads(value)
        except ValueError:
            pass

        return value

    def get_db_prep_save(self, value):
        """Convert our JSON object to a string before we save"""

        if value == "":
            return None

        if isinstance(value, dict):
            value = json.dumps(value, cls=DjangoJSONEncoder)

        return super(JSONField, self).get_db_prep_save(value)


class MatrixSet(models.Model):
    name = models.CharField(max_length=250)
    ec_matrix = JSONField("EC Matrix")
    cf_matrix = JSONField("CF Matrix")
    cfp_matrix = JSONField("CFP Matrix")

    @staticmethod
    def process_excel_file(filename):
        parsed = xls(filename)[0][1]
        def iter_over_key(f):
            return [parsed[f(n)].strip().title() for n in 
                    takewhile(lambda n: parsed.has_key(f(n)), count(1))]

        cols = iter_over_key(lambda n: (0,n))
        width = len(cols)

        rows = iter_over_key(lambda n: (n,0))
        height = len(rows)

        def check(r,c):
            return 0 < r <= height and 0 < c <= width

        matrix = [(k,v) for k,v in parsed.iteritems() if check(*k)]
        return {"cols": cols, "rows":rows, "matrix":matrix, "width":width, "height":height}


class MatrixUploadFileForm(forms.ModelForm):
    class Meta:
        model = MatrixSet
        fields = ('name',)
        
    ec_matrix = forms.FileField()
    cf_matrix = forms.FileField()
    cfp_matrix = forms.FileField()
    
    def matrix_clean(self, matrix):
        cl = self.cleaned_data.get(matrix, '')
        try:
            return MatrixSet.process_excel_file(cl)
        except (Exception, ) as e:
            raise forms.ValidationError(e)
        
    def clean_ec_matrix(self):
        return self.matrix_clean("ec_matrix")

    def clean_cf_matrix(self):
        return self.matrix_clean("cf_matrix")

    def clean_cfp_matrix(self):
        return self.matrix_clean("cfp_matrix")

    def clean(self):
        if any(self.errors):
            return
        def check_dims(m1, d1, m2, d2):
            if self.cleaned_data.get(m1,'')[d1] != self.cleaned_data.get(m2, '')[d2]:
                raise forms.ValidationError(("%s of %s is not equal to %s of %s." % (d1, m1, d2, m2)).title())
        check_dims("ec_matrix", "width", "cf_matrix", "height")
        check_dims("cf_matrix", "width", "cfp_matrix", "width")
        check_dims("cf_matrix", "height", "cfp_matrix", "height")
        return self.cleaned_data

    def save(self):
        matrix = MatrixSet(**self.cleaned_data)
        matrix.save()
        return matrix

def matrix_select_from_model(pk):
    matrix = MatrixSet.objects.get(pk=pk)
    func_choices = list(enumerate(matrix.ec_matrix['rows']))

    class MatrixSelectFunctionsForm(forms.Form):
        choices = forms.MultipleChoiceField(choices=func_choices)

    return MatrixSelectFunctionsForm
        
            
