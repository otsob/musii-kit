from typing import List

import numpy as np
from matplotlib import pyplot as plt


class PointSet:
    """ A point set representation of a piece of music. """

    def __init__(self, points, piece_name=None) -> object:
        """
        Constructs new instance.
        :param points: the points in the point set as a numpy array
        :param piece_name: the name of the piece of music the point set represents
        """
        self._points = points
        self.piece_name = piece_name

    def points_array(self):
        """
        Returns the points as a numpy array where each point occupies a single
        line.

        :return: the points as a numpy array
        """
        return self._points


class Pattern:
    """ Represents a point pattern """

    def __init__(self, pattern_points, label: str, source: str, data_type='point_set'):
        self._pattern = pattern_points
        self.label = label
        self.source = source
        self._data_type = data_type

    def to_dict(self):
        as_dict = {'label': self.label,
                   'source': self.source,
                   'data_type': self._data_type,
                   'data': self._pattern.tolist()}
        return as_dict

    def points(self):
        return self._pattern

    def __str__(self):
        return f'[{self.label}; {self.source}; {self._data_type}: {self._pattern}]'

    def __len__(self):
        return self._pattern.shape[0]

    @staticmethod
    def from_dict(input_dict):
        label = input_dict['label']
        source = input_dict['source']
        data_type = input_dict['data_type']
        if data_type == 'point_set':
            points = np.array(input_dict['data'])

        return Pattern(points, label, source, data_type)


class PatternOccurrences:
    """ Represents a point pattern along with all of its occurrences """

    def __init__(self, piece: str, pattern: Pattern, occurrences: List[Pattern]):
        self.piece = piece
        self.pattern = pattern
        self.occurrences = occurrences

    def to_dict(self):
        as_dict = {'piece': self.piece,
                   'pattern': self.pattern.to_dict(),
                   'occurrences': list(map(lambda p: p.to_dict(), self.occurrences))}
        return as_dict

    def tolist(self):
        """ Returns the pattern and all of its occurrences as a list """
        pattern_list = [self.pattern]
        pattern_list.extend(self.occurrences)
        return pattern_list

    def __len__(self):
        return len(self.occurrences) + 1

    def __getitem__(self, item):
        if item == 0:
            return self.pattern

        return self.occurrences[item - 1]

    def __str__(self):
        string_components = ['Piece:', self.piece, '\npattern: ', str(self.pattern), '\n', 'occurrences:\n']
        for occ in self.occurrences:
            string_components.append(str(occ))
            string_components.append('\n')

        return ''.join(string_components)

    @staticmethod
    def from_dict(input_dict):
        piece = input_dict['piece']
        pattern = Pattern.from_dict(input_dict['pattern'])
        occurrences = []
        for occ_dict in input_dict['occurrences']:
            occurrences.append(Pattern.from_dict(occ_dict))

        return PatternOccurrences(piece, pattern, occurrences)


class Plot:
    """ Defines a plot of a point-set and optionally patterns.

    Attributes:
    point_colors - the colors of the points in matploblib scatter-plot format.
    point_size - the size of the points
    measure_lines - where to plot vertical measure lines
    """

    def __init__(self, point_set: PointSet):
        """
        Creates a new plot
        :param point_set: the point set to plot
        """
        self._point_set = point_set
        self.point_colors = 'k'
        self.point_size = 1.0
        self.measure_lines = []
        self._patterns = []

    def add_pattern(self, pattern: Pattern, color='b'):
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
        points = self._point_set.points_array()
        plt.title(self._point_set.piece_name)
        plt.scatter(points[:, 0], points[:, 1], s=self.point_size, c=self.point_colors)
        plt.xlabel('Onset time')
        plt.ylabel('Pitch number')

        if self.measure_lines:
            max_pitch = np.max(points[:, 1])
            min_pitch = np.min(points[:, 1])
            plt.vlines(self.measure_lines, min_pitch, max_pitch, colors='k', linestyles='dotted', alpha=0.25)

        for pattern_with_color in self._patterns:
            pattern = pattern_with_color[0]
            color = pattern_with_color[1]
            plt.scatter(pattern.points()[:, 0], pattern.points()[:, 1], s=self.point_size * 2.0, c=color)

        plt.show()
