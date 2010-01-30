"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils import simplejson as json
from matrix import Matrix, MatrixEncoder, as_matrix


class TestModels(TestCase):
    fixtures = ['test/test_lean_fixture.json']

class TestMatrixConversions(TestCase):
    def setUp(self):
        self.matrix = Matrix(["1"], ["a","b"], {(0,0):1})
        self.as_dict = {"rows": ["a", "b"], "matrix": [[[0, 0], 1]], "width": 1, "cols": ["1"], "height": 2, "__matrix__": True}
        
    def test_matrix_sanity(self):
        self.assertTrue(self.matrix.width==1)
        self.assertTrue(self.matrix.height==2)

    def test_matrix_to_json(self):
        j = json.dumps(self.matrix, cls=MatrixEncoder)
        self.assertEquals(json.loads(j),self.as_dict)

    def test_json_to_matrix(self):
        j = json.dumps(self.matrix, cls=MatrixEncoder)
        self.assertEquals(json.loads(j, object_hook=as_matrix).__dict__, self.matrix.__dict__)


def lol_to_dict(m):
    d = {}
    for y, j in enumerate(m):
        for x, i in enumerate(j):
            if i:
                d[(x,y)] = i
    return d
    
class TestMatrixMath(TestCase):
    def setUp(self):
        self.am = [[0, -1, 2],[4, 11, 2]]
        self.a = Matrix(["a", "b", "c"], ["foo", "bar"], lol_to_dict(self.am))

        self.bm = [[3,-1],[1,2],[6,1]]
        self.b = Matrix(["baz", "batz"], ["l", "o", "l"], lol_to_dict(self.bm))
    
        self.cm = [[11,0],[35,20]]
        self.c = Matrix(["baz", "batz"], ["foo", "bar"], lol_to_dict(self.cm))

    
    def testMatrixMult(self):
        self.assertEquals(self.a.mult(self.b).__dict__, self.c.__dict__)


    def testMatrixMax(self):
        self.assertEquals(self.a.max, 11)
        self.assertEquals(self.b.max, 6)
        self.assertEquals(self.c.max, 35)

class TestREDMath(TestCase):
    def setUp(self):
        self.ecm = [[1, 1],[1, 0]]
        self.ec = Matrix(["Bearing", "Belt"], ["Import Mechanical", "Export Mechanical"]
                         , lol_to_dict(self.ecm))

        self.cfm = [[0,3],[1,0]]
        self.cf = Matrix(["Creep", "Fatigue"], ["Bearing", "Belt"], lol_to_dict(self.cfm))

        self.cfpm = [[1,2],[5,0]]
        self.cfp = Matrix(["Creep", "Fatigue"], ["Bearing", "Belt"], lol_to_dict(self.cfpm))

        self.efm = [[1,3],[0,3]]
        self.ef = Matrix(["Creep", "Fatigue"], ["Import Mechanical", "Export Mechanical"],
                         lol_to_dict(self.efm))

        self.l1m = [[2,5],[0,5]]
        self.l1 = Matrix(["Creep", "Fatigue"], ["Import Mechanical", "Export Mechanical"],
                          lol_to_dict(self.l1m))

        self.l2m = [[1,1],[0,1]]
        self.l2 = Matrix(["Creep", "Fatigue"], ["Import Mechanical", "Export Mechanical"],
                          lol_to_dict(self.l2m))

        self.c1m = [[5,2],[1,2]]
        self.c1 = Matrix(["Creep", "Fatigue"], ["Import Mechanical", "Export Mechanical"],
                          lol_to_dict(self.c1m))

        self.c2m = [[3,2],[1,2]]
        self.c2 = Matrix(["Creep", "Fatigue"], ["Import Mechanical", "Export Mechanical"],
                          lol_to_dict(self.c2m))


    def testMatrixMath(self):
        self.assertEquals(self.ec.mult(self.cf).matrix, self.ef.matrix)
    
    def testMatrixL1(self):
        self.assertEquals(self.ef.l1([0,1]).matrix, self.l1.matrix)

    def testMatrixAgg(self):
        self.assertEquals(self.ef.max, 3)

    def testMatrixL2(self):
        self.ef._max = 15
        self.assertEquals(self.ef.l2().matrix, self.l2.matrix)

    def testMatrixC1(self):
        self.assertEquals(self.ec.c1(self.cfp).matrix, self.c1.matrix)

    def testMatrixC2(self):
        self.assertEquals(self.ec.c2(self.cfp).matrix, self.c2.matrix)

    def testMaskRows(self):
        m = self.ef.mask([0])
        mat = [[1,3]]
        self.assertEquals(m.rows, ["Import Mechanical"])
        self.assertEquals(m.matrix, lol_to_dict(mat))

        m = self.ef.mask([1])
        mat = [[0,3]]
        self.assertEquals(m.rows, ["Export Mechanical"])
        self.assertEquals(m.matrix, lol_to_dict(mat))
