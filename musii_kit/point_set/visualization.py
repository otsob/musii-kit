import numpy as np
from matplotlib import pyplot as plt

from point_set.point_set import PointSet2d, Pattern2d


class Plot:
    """ Defines a plot of a point-set and optionally patterns.

    Attributes:
    point_colors - the colors of the points in matploblib scatter-plot format.
    point_size - the size of the points
    measure_lines - where to plot vertical measure lines
    """

    def __init__(self, point_set: PointSet2d):
        """
        Creates a new plot
        :param point_set: the point set to plot
        """
        self._point_set = point_set
        self.point_colors = 'k'
        self.point_size = 1.0
        self.measure_lines = []
        self._patterns = []

    def add_pattern(self, pattern: Pattern2d, color='b'):
        """
        Add pattern to visualize.
        :param pattern: the point pattern to visualize
        :param color: the color used to visualize the pattern
        """
        self._patterns.append((pattern, color))

    def show(self):
        """
        Show the given point set as a scatter plot.
        """
        points = self._point_set.as_numpy()
        plt.title(self._point_set.piece_name)
        plt.scatter(points[:, 0], points[:, 1], s=self.point_size, c=self.point_colors)
        plt.xlabel('Onset time')
        plt.ylabel('Pitch number')

        if self.measure_lines:
            max_pitch = np.max(points[:, 1])
            min_pitch = np.min(points[:, 1])

            if min_pitch == max_pitch:
                max_pitch += 1.0
                min_pitch -= 1.0

            plt.vlines(self.measure_lines, min_pitch, max_pitch, colors='k', linestyles='dotted', alpha=0.25)

        for pattern_with_color in self._patterns:
            pattern = pattern_with_color[0]
            color = pattern_with_color[1]
            plt.scatter(pattern.as_numpy()[:, 0], pattern.as_numpy()[:, 1], s=self.point_size * 2.0, c=color)

        plt.show()
