import numpy as np
import unittest

from musii_kit.point_set.point_set import Pattern


class PointSetTests(unittest.TestCase):

    def test_pattern(self):
        points = np.ones((6, 2))
        pattern = Pattern(points, 'A', 'Analyst')
        self.assertEqual(pattern.label, 'A')
        self.assertEqual(pattern.source, 'Analyst')
