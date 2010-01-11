from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json

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
    name = models.CharField(max_length=100)
    ec_matrix = JSONField()
    cf_matrix = JSONField()
    cfp_matrix = JSONField()

    @staticmethod
    def process_excel_file(filename):
        try:
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

        except:
            return {"cols":[], "rows":[], "matrix":[], "width":0, "height":0}

