from typing import List

import numpy as np
from matplotlib import pyplot as plt


class Point2d:
    """
    Represents a point in a 2-dimensional point-set.
    """

    decimal_places = 5

    def __init__(self, raw_onset_time, pitch_number, rounded_onset_time=None):
        """
        Constructor
        :param raw_onset_time: the raw (not rounded) onset time of the note event represented by this point
        :param pitch_number: the pitch number of the note this point represents
        :param rounded_onset_time: the rounded onset time of the note event represented by this point
        (should not be set in normal use, this is computed automatically when not set).
        """
        self._raw_onset_time = raw_onset_time
        self._pitch_number = pitch_number
        if rounded_onset_time is None:
            self._onset_time = round(raw_onset_time, self.decimal_places)
        else:
            self._onset_time = rounded_onset_time

    @property
    def onset_time(self):
        """
        Returns the onset time of the note event this point represents.
        The onset time is rounded.
        """
        return self._onset_time

    @property
    def pitch_number(self):
        """
        Returns the pitch number of the note event this point represents.
        """
        return self._pitch_number

    @property
    def raw_onset_time(self):
        return self._raw_onset_time

    def __eq__(self, other):
        return self._onset_time == other.onset_time and self._pitch_number == other.pitch_number

    def __hash__(self):
        return hash(self._onset_time) + hash(self._pitch_number)

    def __str__(self):
        return f'({self._onset_time}, {self._pitch_number})'

    def __repr__(self):
        return f'({self._onset_time} [{self._raw_onset_time}], {self._pitch_number})'

    def __lt__(self, other):
        if self._onset_time < other.onset_time:
            return True

        if self._onset_time > other.onset_time:
            return False

        return self._pitch_number < other.pitch_number

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        if self._onset_time > other.onset_time:
            return True

        if self._onset_time < other.onset_time:
            return False

        return self._pitch_number > other.pitch_number

    def __ge__(self, other):
        return self == other or self > other


class PointSet2d:
    """ A 2-dimensional point set representation of a piece of music. """

    def __init__(self, points: List[Point2d], piece_name=None, dtype=float):
        """
        Constructs new instance.
        :param points: the points in the point set as a numpy array
        :param piece_name: the name of the piece of music the point set represents
        :param dtype: the data type of the point components
        """

        self.piece_name = piece_name
        self._dtype = dtype

        if self._dtype != float and self._dtype != int:
            raise ValueError('Unsupported point component data type, must be float or int')

        sorted_point_set = sorted(set(points))
        self._points = np.empty((len(sorted_point_set), 3), dtype=self._dtype)
        for i, point in enumerate(sorted_point_set):
            self._points[i, 0] = point.onset_time
            self._points[i, 1] = point.pitch_number
            self._points[i, 2] = point.raw_onset_time

    @staticmethod
    def from_numpy(points_array, piece_name=None):
        points = []
        for i in range(len(points_array)):
            row = points_array[i, :]
            points.append(Point2d(row[0], row[1]))

        return PointSet2d(points, piece_name, dtype=points_array.dtype)

    @property
    def dtype(self):
        """
        The data type of the point's components.
        """
        return self._dtype

    def as_numpy(self):
        """
        Returns the points as a numpy array where each point occupies a single
        line.

        Returns a reference to the internal representation used for storing the points.
        The first column is the (rounded) onset time, the second column is the pitch number,
        and the third column is the raw onset time only used for internal purposes.

        :return: the points as a numpy array
        """
        return self._points

    def __getitem__(self, index):
        """ Returns the point at the given index in the point set.
         Point sets are lexicographically ordered. """
        row = self._points[index, :]
        return Point2d(row[2], row[1], rounded_onset_time=row[0])

    def __len__(self):
        return len(self._points)

    def __iter__(self):
        class PointsIter2d:
            def __init__(self, point_set):
                self._i = 0
                self._point_set = point_set

            def __next__(self):
                if self._i >= len(self._point_set):
                    raise StopIteration

                point = self._point_set[self._i]
                self._i += 1
                return point

        return PointsIter2d(self)

    def __and__(self, other):
        i = 0
        j = 0

        common_points = []

        while i < len(self) and j < len(other):
            this = self[i]
            that = other[j]

            if this == that:
                common_points.append(this)
                i += 1
                j += 1
            elif this < that:
                i += 1
            else:
                j += 1

        return PointSet2d(common_points, self.piece_name, self._dtype)


class Pattern2d(PointSet2d):
    """ Represents a pattern in a 2-dimensional point-set representation of music. """

    def __init__(self, points: List[Point2d], label: str, source: str, piece_name=None, dtype=float):
        super().__init__(points, piece_name, dtype)
        self.label = label
        self.source = source

    @staticmethod
    def from_numpy(points_array, label: str, source: str, piece_name=None):
        points = []
        for i in range(len(points_array)):
            row = points_array[i, :]
            points.append(Point2d(row[0], row[1]))

        return Pattern2d(points, label, source, piece_name, dtype=points_array.dtype)

    def to_dict(self):
        dtype_str = 'None'
        if self.dtype == int:
            dtype_str = 'int'
        elif self.dtype == float:
            dtype_str = 'float'

        return {'label': self.label,
                'source': self.source,
                'pattern_type': 'point_set',
                'dtype': dtype_str,
                'data': self._points.tolist()}

    def __str__(self):
        return f'[{self.label}; {self.source}; {self._dtype}: {self._points}]'

    def __len__(self):
        return self._points.shape[0]

    @staticmethod
    def from_dict(input_dict):
        label = input_dict['label']
        source = input_dict['source']
        data_type = input_dict['dtype']
        points = list(map(lambda row: Point2d(row[0], row[1]), input_dict['data']))

        dtype = float
        if data_type == 'int':
            dtype = int

        return Pattern2d(points, label, source, dtype=dtype)


class PatternOccurrences2d:
    """ Represents a 2-dimensional point pattern along with all of its occurrences """

    def __init__(self, piece: str, pattern: Pattern2d, occurrences: List[Pattern2d]):
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
        pattern = Pattern2d.from_dict(input_dict['pattern'])
        occurrences = []
        for occ_dict in input_dict['occurrences']:
            occurrences.append(Pattern2d.from_dict(occ_dict))

        return PatternOccurrences2d(piece, pattern, occurrences)


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
            plt.vlines(self.measure_lines, min_pitch, max_pitch, colors='k', linestyles='dotted', alpha=0.25)

        for pattern_with_color in self._patterns:
            pattern = pattern_with_color[0]
            color = pattern_with_color[1]
            plt.scatter(pattern.as_numpy()[:, 0], pattern.as_numpy()[:, 1], s=self.point_size * 2.0, c=color)

        plt.show()
