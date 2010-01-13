from django.utils import simplejson as json

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


class MatrixEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Matrix):
            return {"__matrix__": True,
                    "cols": obj.cols,
                    "width": obj.width,
                    "rows": obj.rows,
                    "height":obj.height,
                    "matrix":obj.matrix.items()}
        return json.JSONEncoder.default(self, obj)

def as_matrix(dct):
    if '__matrix__' in dct:
        dct['matrix'] = dict(((tuple(k), v) for k,v in dct['matrix']))
        del dct['__matrix__']
        m =  Matrix(**dict((str(k),v) for k,v in dct.iteritems()))
        return m
    return dct
