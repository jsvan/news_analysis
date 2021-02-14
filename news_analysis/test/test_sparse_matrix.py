import unittest
from src.tools.sparse_matrix import jsv_dictmat

urdict = {(0, 100): [1, 1, 0], (1, 100): [3, 0, 1], (0, 15): [2, 2, 5], (2, 34): [0, 1, 2]}


def seed(m=1):
    return {(0,100):[1*m,1*m,0*m], (1,100):[3*m,0*m,1*m], (0,15):[2*m,2*m,5*m], (2,34):[0*m, 1*m,2*m]}

class MyTestCase(unittest.TestCase):
    def test_update(self):
        a = jsv_dictmat(seed())
        b = jsv_dictmat(seed())
        a.update(b)
        res = seed(2)
        for k, v in a.items():
            self.assertEqual(v, res[k], msg=f"key {k}, resv {res[k]}, jsvv {v}")

    def test_collapse(self):
        a = jsv_dictmat(seed(1)).collapse_into_day_vector()
        res = {(0, 100): [4, 1, 1], (0, 15): [2, 2, 5], (0, 34): [0, 1, 2]}
        for k, v in a.items():
            self.assertEqual(v, res[0, k[1]], msg=f"key {k}, resv {res[0, k[1]]}, jsvv {v}")

    def test_div(self):
        a = jsv_dictmat(seed(5))
        b = a/5
        for k, v in b.items():
            self.assertEqual(v, urdict[k], msg=f"key {k}, resv {urdict[k]}, jsvv {v}")

if __name__ == '__main__':
    unittest.main()
