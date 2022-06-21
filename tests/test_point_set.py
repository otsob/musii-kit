import numpy as np

from musii_kit.point_set.point_set import Pattern


class TestPointSet:

    def test_pattern(self):
        points = np.ones((6, 2))
        pattern = Pattern(points, 'A', 'Analyst')
        assert pattern.label == 'A'
        assert pattern.source == 'Analyst'
