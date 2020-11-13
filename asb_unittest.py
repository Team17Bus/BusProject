import unittest
import asb
from math import sqrt

class TestASBmethods(unittest.TestCase):
    def setUp(self):
        self.A = [(0, 0), (0, 0), (0, 0), (0, 0), (1, 2), (0, 0), (0, 0)]
        self.B = [(1, 1), (3, 2), (4, -1), (1, -2), (2, 4), (0, 2), (3, -1)]
        self.S = [(2, 0), (2, 0), (2, 0), (2, 0), (3, 3), (2, 0), (4, 3)]
        self.line_AS = [(0, 2, 0), (0, 2, 0), (0, 2, 0), (0, 2, 0), (-1, 2, -3), (0, 2, 0), (-3, 4, 0)]
        self.line_BS = [(1, 1, -2), (2, -1, -4), (-1, -2, 2), (-2, 1, 4), (1, 1, -6), (2, 2, -4), (-4, 1, 13)]
        self.bisector = [(), (), (), (), (), (), ()]

    def test_make_line(self):
        for i in range(len(self.A)):
            line_AS = asb.make_line(self.A[i], self.S[i])
            line_BS = asb.make_line(self.B[i], self.S[i])
            self.assertEqual(self.line_AS[i], line_AS)
            self.assertEqual(self.line_BS[i], line_BS)

    def test_lines_intersection(self):
        pass
        for i in range(len(self.A)):
            self.assertEqual(self.S[i], asb.lines_intersection(self.line_AS[i], self.line_BS[i]))

    def test_get_angle_bisector(self):
        pass

    def test_is_past_angle_bisector(self):
        pass



if __name__ == '__main__':
    unittest.main()
