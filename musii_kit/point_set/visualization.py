import math
from copy import deepcopy

import numpy as np
from matplotlib import pyplot as plt

from musii_kit.point_set.point_set import PointSet2d, Pattern2d, PatternOccurrences2d


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


class ScoreVisualization:
    """ Visualizes point-set pattern on a music21 score instance. The point-set given in the constructor must
    have been created from a music21 score. """

    def __init__(self, point_set: PointSet2d):
        if not point_set.score:
            raise ValueError("Cannot create a score visualization for a point-set with no score associated")

        self._point_set = PointSet2d.from_score(deepcopy(point_set.score), point_set.pitch_extractor)
        self._point_set.measure_line_positions = point_set.measure_line_positions
        self._point_set.quarter_length = point_set.quarter_length
        self._point_set.piece_name = point_set.piece_name
        self._first_measure = math.inf
        self._last_measure = -1
        self._marked_notes = []

    def mark_pattern(self, pattern: Pattern2d, color='red', discard_unisons=True):
        """
        Marks a pattern with the given color in the score.
        :param pattern: the pattern that is marked
        :param color: the color to use for the pattern
        :param discard_unisons: set to true to avoid getting multiple notes for a point produced from a union
        """

        for note in self._point_set.get_pattern_notes(pattern, discard_unisons=discard_unisons):
            note.style.color = color
            self._marked_notes.append(note)

        first, last = self._point_set.get_measure_range(pattern)
        self._first_measure = min(self._first_measure, first)
        self._last_measure = max(self._last_measure, last)

    def mark_occurrences(self, pattern_occurrences: PatternOccurrences2d, pattern_color='red',
                         occurrence_colors=['red'], discard_unisons=True):
        """
        Mark pattern occurrences with the given colors. The colors are rotated from one occurrence to the next.
        :param pattern_occurrences: the pattern occurrences to mark
        :param pattern_color: the color used to mark the main pattern of the occurrences
        :param occurrence_colors: the colors used for marking the pattern occurrences
        :param discard_unisons: set to true to avoid getting multiple notes for a point produced from a union
        """
        self.mark_pattern(pattern_occurrences.pattern, pattern_color, discard_unisons=discard_unisons)

        for i in range(len(pattern_occurrences.occurrences)):
            self.mark_pattern(pattern_occurrences.occurrences[i], occurrence_colors[i % len(occurrence_colors)],
                              discard_unisons=discard_unisons)

    def __is_range_defined(self):
        return self._first_measure < math.inf and self._last_measure >= 0

    def get_selection(self):
        """ Returns a selection from the score that only contains a range of measures that contains
        marked patterns. """
        if self.__is_range_defined():
            selection = self._point_set.score.measures(self._first_measure, self._last_measure)
            metadata = deepcopy(self._point_set.score.metadata)
            metadata.movementName = f'{self._point_set.piece_name} measures {self._first_measure}-{self._last_measure}'
            selection.metadata = metadata
            return selection

        return self._point_set.score

    def get_measure_range(self):
        """
        Returns the range of measures the markings affect or None if no markings set.
        :return: the range of measures the markings affect or None if no markings set
        """
        if self.__is_range_defined():
            return self._first_measure, self._last_measure

        return None

    def reset(self):
        """ Reset all markings from this score. """
        for note in self._marked_notes:
            note.style.color = None

        self._marked_notes = []

    @property
    def score(self):
        """  The music21 score instance containing the markings. """
        return self._point_set.score
