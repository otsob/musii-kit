from typing import List

import music21 as m21
import numpy as np


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

    def __init__(self, points: List[Point2d], piece_name=None, dtype=float, quarter_length=1.0,
                 measure_line_positions=None, score=None, points_to_notes=None, pitch_extractor=None):
        """
        Constructs new instance.
        :param points: the points in the point set as a numpy array
        :param piece_name: the name of the piece of music the point set represents
        :param dtype: the data type of the point components
        :param quarter_length: the length of a quarter note in the time units used for measuring the onset time axis
        :param measure_line_positions: optional list or array of the positions of measure lines in time
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

        self.quarter_length = quarter_length
        self.measure_line_positions = measure_line_positions
        self._point_to_notes = points_to_notes
        self._score = score
        self._pitch_extractor = pitch_extractor

        if pitch_extractor is PointSet2d.chromatic_pitch:
            self._pitch_type = 'chromatic'
        elif pitch_extractor is PointSet2d.morphetic_pitch:
            self._pitch_type = 'morphetic'
        else:
            self._pitch_type = None

    @staticmethod
    def chromatic_pitch(m21_pitch):
        return m21_pitch.ps

    __steps = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}

    @staticmethod
    def morphetic_pitch(m21_pitch):
        """ Returns the morphetic pitch number of the given pitch so that the morphetic
        pitch is aligned with MIDI pitch numbers at C4 (60). This convention is used to match
        the morphetic numbering used in the JKU-PDD dataset. """

        oct = m21_pitch.octave * 7
        step = PointSet2d.__steps[m21_pitch.step]

        # Shift is used to get the morphetic pitch aligned so that C4 in morphetic
        # equals C4 in MIDI (60).
        shift = 32

        return oct + step + shift

    @staticmethod
    def from_score(score: m21.stream.Score, pitch_extractor=chromatic_pitch):
        """
        Returns a point-set created from the given music21 score.

        :param score: a music21 score
        :param pitch_extractor: the function used to map a music21 pitch to a number
        :return: a point-set created from the given score
        """

        measure_line_positions = []
        first_staff = True
        points_and_notes = {}

        for staff in score.parts:

            measure_offset = 0.0

            for measure in filter(lambda m: isinstance(m, m21.stream.base.Measure), staff):
                for elem in measure:
                    PointSet2d._read_elem_to_points(elem, measure_offset, points_and_notes, pitch_extractor)

                    if isinstance(elem, m21.stream.Voice):
                        for e in elem:
                            PointSet2d._read_elem_to_points(e, measure_offset, points_and_notes, pitch_extractor)

                if first_staff:
                    measure_line_positions.append(measure_offset)

                measure_offset += measure.quarterLength

            if first_staff:
                measure_line_positions.append(measure_offset)

            first_staff = False

        return PointSet2d(points_and_notes.keys(), PointSet2d._extract_piece_name(score), dtype=float,
                          quarter_length=1.0,
                          measure_line_positions=measure_line_positions, score=score, points_to_notes=points_and_notes,
                          pitch_extractor=pitch_extractor)

    @staticmethod
    def _extract_piece_name(score):
        piece_name = None

        if hasattr(score, 'metadata'):
            metadata = score.metadata
            if hasattr(metadata, 'title') and metadata.title:
                piece_name = metadata.title
            elif hasattr(metadata, 'movementName') and metadata.movementName:
                piece_name = metadata.movementName

        return piece_name

    @staticmethod
    def _is_note_onset(elem):
        if not isinstance(elem, m21.note.Note):
            return False

        if elem.tie:
            return elem.tie.type != 'stop' and elem.tie.type != 'continue'

        return True

    @staticmethod
    def _read_elem_to_points(elem, measure_offset, points, pitch_extractor):
        if PointSet2d._is_note_onset(elem):
            point = Point2d(measure_offset + elem.offset, pitch_extractor(elem.pitch))
            points[point] = elem
        if isinstance(elem, m21.chord.Chord) and not isinstance(elem, m21.harmony.ChordSymbol):
            for note in elem:
                if PointSet2d._is_note_onset(note):
                    point = Point2d(measure_offset + elem.offset, pitch_extractor(note.pitch))
                    points[point] = note

    @staticmethod
    def from_numpy(points_array, piece_name=None):
        points = []
        for i in range(len(points_array)):
            row = points_array[i, :]
            points.append(Point2d(row[0], row[1]))

        return PointSet2d(points, piece_name, dtype=points_array.dtype)

    @staticmethod
    def from_dict(input_dict):
        piece_name = input_dict['piece_name']
        quarter_length = input_dict['quarter_length']
        measure_lines = input_dict['measure_line_positions']

        points = list(map(lambda row: Point2d(row[0], row[1]), input_dict['data']))

        data_type = input_dict['dtype']
        dtype = float
        if data_type == 'int':
            dtype = int

        pitch_extractor = None
        pitch_type = input_dict['pitch_type']
        if pitch_type == 'chromatic':
            pitch_extractor = PointSet2d.chromatic_pitch
        if pitch_type == 'morphetic':
            pitch_extractor = PointSet2d.morphetic_pitch

        return PointSet2d(points, piece_name, dtype, quarter_length, measure_lines, pitch_extractor=pitch_extractor)

    def to_dict(self):
        return {'piece_name': self.piece_name,
                'dtype': self._dtype_to_str(),
                'representation': 'point_set',
                'pitch_type': self.pitch_type,
                'quarter_length': self.quarter_length,
                'measure_line_positions': self.measure_line_positions,
                'data': self._points[:, 0:2].tolist()}

    def _dtype_to_str(self):
        dtype_str = 'None'
        if self.dtype == int:
            dtype_str = 'int'
        elif self.dtype == float:
            dtype_str = 'float'
        return dtype_str

    @property
    def pitch_extractor(self):
        return self._pitch_extractor

    @property
    def pitch_type(self):
        return self._pitch_type

    @property
    def score(self):
        """ The score from which this point-set was created. If this point-set was not created
        from a score, this is None."""
        return self._score

    def get_note(self, point: Point2d):
        """
        Returns the note element corresponding to the given point if this point-set was
        created from a score.
        :param point: the point for which the corresponding note element is returned
        :return: the note element corresponding to the given point if this point-set was
        created from a score
        """
        return self._point_to_notes[point]

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

    def equals_in_points(self, other):
        """
        Returns true if this point-set is equal to other in terms of the points it contains.
        Other fields are ignored.


        :param other: the point-set with which this is compared
        :return: true if this point-set is equal to other in terms of the points it contains
        """

        onsets_match = np.array_equal(self._points[:, 0], other.as_numpy()[:, 0])
        pitches_match = np.array_equal(self._points[:, 1], other.as_numpy()[:, 1])

        return onsets_match and pitches_match

    def get_range(self, start, end) -> List[Point2d]:
        """
        Returns the points in the given time-range (inclusive) in ascending lexicographic order.
        :param start: the earliest onset time to include in the range
        :param end: the latest onset time to include in the range
        :return: the points in the given time-range (inclusive)
        """

        onsets = self._points[:, 0]
        indices = np.where((start <= onsets) & (onsets <= end))[0]

        points = []
        for i in indices:
            points.append(self[i])

        return points

    def time_scaled(self, factor):
        """
        Returns a time-scaled copy of this point-set. The onset times are multiplied by the given factor.
        Other fields are copied from this point-set.

        :param factor: the factor by which the time axis is scaled
        :return: a time-scaled copy of this pattern
        """
        scaled_point_array = np.empty(self._points.shape)
        scaled_point_array[:, 0] = self._points[:, 2] * factor
        scaled_point_array[:, 1] = self._points[:, 1]

        scaled = PointSet2d.from_numpy(scaled_point_array, self.piece_name)
        scaled.quarter_length = self.quarter_length
        scaled.measure_line_positions = self.measure_line_positions
        scaled._score = self.score
        scaled._point_to_notes = self._point_to_notes
        scaled._pitch_extractor = self._pitch_extractor
        scaled._pitch_type = self._pitch_type

        return scaled


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
        return {'label': self.label,
                'source': self.source,
                'representation': 'point_set',
                'dtype': self._dtype_to_str(),
                'data': self._points[:, 0:2].tolist()}

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

    def time_scaled(self, factor):
        """
        Returns a time-scaled copy of this point-set. The onset times are multiplied by the given factor.
        Other fields are copied from this point-set.

        :param factor: the factor by which the time axis is scaled
        :return: a time-scaled copy of this pattern
        """
        scaled_point_array = np.empty(self._points.shape)
        scaled_point_array[:, 0] = self._points[:, 2] * factor
        scaled_point_array[:, 1] = self._points[:, 1]

        return Pattern2d.from_numpy(scaled_point_array, self.label, self.source, self.piece_name)


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
