from typing import List

import numpy as np


class PointSet:
    """ A point set representation of a piece of music. """

    def __init__(self, points):
        self._points = points


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

    def __str__(self):
        return f'[{self.label}; {self.source}; {self._data_type}: {self._pattern}]'

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
