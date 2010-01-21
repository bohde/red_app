import numpy
from scipy import sparse, int8
from rbco.msexcel import xls_to_excelerator_dict as xls
from itertools import count, takewhile
from django.utils import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder

import re
def titlecase(s):
    return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                  lambda mo: mo.group(0)[0].upper() +
                  mo.group(0)[1:].lower(),
                  s)

class Matrix(object):
    """
    Matrix with Column and Row Headers
    Empty cells default to 0.
    """
    def __init__(self, cols, rows, matrix, width=None, height=None):
        self.cols = cols
        self.width = width if width else len(cols)
        self.rows = rows
        self.height = height if height else len(rows)
        self.matrix = matrix

    def to_sparse_matrix(self):
        """
        Convert the JSON formatted matrix to a numpy sparse matrix
        """
        d = sparse.dok_matrix((self.height, self.width), int8)
        for (x,y),v in self.matrix.iteritems():
            # Have to reverse coords, because scipy puts them in (y,x) format
            d[y,x] = v
        return d.tocsc()

    def mult(self, other):
        rows = self.rows
        height = self.height
        cols = other.cols
        width = other.width
        a = self.to_sparse_matrix()
        b = other.to_sparse_matrix()
        matrix = Matrix.from_sparse_matrix(a * b)
        return Matrix(cols, rows, matrix, width, height)

    @staticmethod
    def from_sparse_matrix(sp):
        """
        Have to reverse coords, because scipy puts them in (y,x) format
        """
        return dict(((int(x), int(y)), int(v)) for (y,x), v in sparse.dok_matrix(sp).iteritems())

    @staticmethod
    def from_excel_file(filename):
        parsed = xls(filename)[0][1]
        def iter_over_key(f):
            return [titlecase(parsed[f(n)].strip()) for n in 
                    takewhile(lambda n: parsed.has_key(f(n)), count(1))]

        cols = iter_over_key(lambda n: (0,n))
        width = len(cols)

        rows = iter_over_key(lambda n: (n,0))
        height = len(rows)

        def check(r,c):
            return 0 < r <= height and 0 < c <= width

        matrix = dict(((y-1, x-1),v) for (x,y),v in parsed.iteritems() if check(x,y) and v != 0 )
        return Matrix(cols=cols, rows=rows, matrix=matrix, width=width, height=height)



class MatrixEncoder(DjangoJSONEncoder):
    def default(self, obj):
        print type(obj)
        if isinstance(obj, Matrix):
            return {"__matrix__": True,
                    "cols": obj.cols,
                    "width": obj.width,
                    "rows": obj.rows,
                    "height":obj.height,
                    "matrix":obj.matrix.items()}
        return DjangoJSONEncoder.default(self, obj)

def as_matrix(dct):
    if '__matrix__' in dct:
        dct['matrix'] = dict(((tuple(k), v) for k,v in dct['matrix']))
        del dct['__matrix__']
        m =  Matrix(**dict((str(k),v) for k,v in dct.iteritems()))
        return m
    return dct


