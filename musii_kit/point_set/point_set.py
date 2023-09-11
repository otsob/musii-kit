import uuid
from copy import deepcopy
from operator import itemgetter
from typing import List

import music21 as m21
import numpy as np


class Point2d:
    """
    Represents a point in a 2-dimensional point-set.
    """

    # The number of decimal places used in rounding onset times.
    # This allows matching even when using floating points for onsets.
    decimal_places = 4

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
                 measure_line_positions=None, score=None, points_to_notes=None, pitch_extractor=None,
                 point_set_id=None, has_expanded_repetitions=False, tie_continuations=None):
        """
        Constructs new instance.
        :param points: the points in the point set as a numpy array
        :param piece_name: the name of the piece of music the point set represents
        :param dtype: the data type of the point components
        :param quarter_length: the length of a quarter note in the time units used for measuring the onset time axis
        :param measure_line_positions: optional list or array of the positions of measure lines in time
        :param score: a music21 score object associated with this point-set
        :param points_to_notes: a dict mapping the points to lists of music21 note objects
        :param pitch_extractor: the pitch extractor used when creating point-set from music21 score
        :param point_set_id: the identifier of this point-set
        :param has_expanded_repetitions: set to true to indicate that this point-set has been created from a score
        :param tie_continuations: a dictionary of tie continuations for the points that denote onsets that are continued
        by tied notes. For each point this is a list of pairs (point, note) corresponding to tied notes continuing the
        onset.
        with repetitions included.
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

        if point_set_id:
            self._id = point_set_id
        else:
            self._id = str(uuid.uuid1())

        self.has_expanded_repetitions = has_expanded_repetitions
        self.__tie_continuations = tie_continuations

    @property
    def id(self):
        """ The string identifier or this point-set."""
        return self._id

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
    def from_score(score: m21.stream.Score, pitch_extractor=chromatic_pitch, expand_repetitions=False,
                   include_grace_notes=False):
        """
        Returns a point-set created from the given music21 score.

        :param score: a music21 score
        :param pitch_extractor: the function used to map a music21 pitch to a number
        :param expand_repetitions: repeat the sections marked with repeats in the score in the returned point-set
        :param include_grace_notes: set to true to include grace notes in the point-set, by default they are ignored
        :return: a point-set created from the given score
        """

        measure_line_positions = []
        first_staff = True
        points_and_notes = {}
        tie_continuations = {}

        if expand_repetitions:
            score = score.expandRepeats()

        for staff in score.parts:

            pickup_measure = staff.measure(0)
            measure_offset = -pickup_measure.quarterLength if pickup_measure else 0.0

            unresolved_ties = {}

            for measure in filter(lambda m: isinstance(m, m21.stream.base.Measure), staff):
                for elem in measure:
                    PointSet2d._read_elem_to_points(elem, measure_offset, points_and_notes, pitch_extractor,
                                                    unresolved_ties, tie_continuations, include_grace_notes)

                    if isinstance(elem, m21.stream.Voice):
                        for e in elem:
                            PointSet2d._read_elem_to_points(e, measure_offset, points_and_notes, pitch_extractor,
                                                            unresolved_ties, tie_continuations, include_grace_notes)

                if first_staff:
                    measure_line_positions.append(measure_offset)

                measure_offset += measure.quarterLength

            if first_staff:
                measure_line_positions.append(measure_offset)

            first_staff = False

        return PointSet2d(points_and_notes.keys(), PointSet2d._extract_piece_name(score), dtype=float,
                          quarter_length=1.0,
                          measure_line_positions=measure_line_positions, score=score, points_to_notes=points_and_notes,
                          pitch_extractor=pitch_extractor, has_expanded_repetitions=expand_repetitions,
                          tie_continuations=tie_continuations)

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
    def _is_note_onset(note, include_grace_notes):
        """ Returns true if the element represents a note onset (excluding grace notes). """
        if not include_grace_notes and isinstance(note.duration, m21.duration.GraceDuration):
            return False

        if note.tie:
            return note.tie.type != 'stop' and note.tie.type != 'continue'

        return True

    @staticmethod
    def _continues_unresolved_tie(note, unresolved_ties):
        if isinstance(note.duration, m21.duration.GraceDuration):
            return False

        if note.nameWithOctave not in unresolved_ties:
            return False

        return note.tie and note.tie.type != 'start'

    @staticmethod
    def _add_note_to_points(note, onset_time, points_and_notes, pitch_extractor, unresolved_ties,
                            tie_continuations, include_grace_notes):
        point = Point2d(onset_time, pitch_extractor(note.pitch))

        if PointSet2d._is_note_onset(note, include_grace_notes):
            if point not in points_and_notes:
                points_and_notes[point] = []
            points_and_notes[point].append(note)
            if note.tie and note.tie.type == 'start':
                unresolved_ties[note.nameWithOctave] = (point, [])
        elif PointSet2d._continues_unresolved_tie(note, unresolved_ties):
            tie_starting_point, continuations = unresolved_ties[note.nameWithOctave]
            continuations.append((point, note))
            if note.tie.type == 'stop':
                tie_continuations[tie_starting_point] = continuations
                unresolved_ties.pop(note.nameWithOctave)

    @staticmethod
    def _read_elem_to_points(elem, measure_offset, points_and_notes, pitch_extractor, unresolved_ties,
                             tie_continuations, include_grace_notes):

        if isinstance(elem, m21.note.Note):
            PointSet2d._add_note_to_points(elem, measure_offset + elem.offset, points_and_notes, pitch_extractor,
                                           unresolved_ties,
                                           tie_continuations, include_grace_notes)
        elif isinstance(elem, m21.chord.Chord) and not isinstance(elem, m21.harmony.ChordSymbol):
            for note in filter(lambda n: isinstance(n, m21.note.Note), elem):
                # Notes within chords do not have sites set for some reason in music21
                # This "hack" sets the sites for the notes to be the same as those of the chord,
                # so that accessing the information through the notes is possible.
                note.sites = elem.sites
                PointSet2d._add_note_to_points(note, measure_offset + elem.offset, points_and_notes, pitch_extractor,
                                               unresolved_ties,
                                               tie_continuations, include_grace_notes)

    @staticmethod
    def from_numpy(points_array, piece_name=None, pitch_type=None):
        points = []
        for i in range(len(points_array)):
            row = points_array[i, :]
            points.append(Point2d(row[0], row[1]))

        point_set = PointSet2d(points, piece_name, dtype=points_array.dtype)
        point_set._pitch_type = pitch_type
        return point_set

    @staticmethod
    def from_dict(input_dict):
        piece_name = input_dict['piece_name']
        quarter_length = input_dict['quarter_length']
        measure_lines = input_dict['measure_line_positions']

        point_set_id = input_dict['id'] if 'id' in input_dict else None

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

        has_expanded_repetitions = input_dict[
            'has_expanded_repetitions'] if 'has_expanded_repetitions' in input_dict else False

        return PointSet2d(points, piece_name, dtype, quarter_length, measure_lines, pitch_extractor=pitch_extractor,
                          point_set_id=point_set_id, has_expanded_repetitions=has_expanded_repetitions)

    def to_dict(self):
        return {'piece_name': self.piece_name,
                'dtype': self._dtype_to_str(),
                'representation': 'point_set',
                'pitch_type': self.pitch_type,
                'quarter_length': self.quarter_length,
                'measure_line_positions': self.measure_line_positions,
                'id': self.id,
                'has_expanded_repetitions': self.has_expanded_repetitions,
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

    def get_notes(self, point: Point2d):
        """
        Returns the note elements corresponding to the given point if this point-set was
        created from a score. Typically, there is only one note corresponding to a point, but in the case
        of unisons occurring in polyphonic music there may be multiple notes.

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

    def __or__(self, other):
        all_points = [p for p in self] + [p for p in other]
        return PointSet2d(all_points, self.piece_name, self._dtype)

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

    def get_measure(self, point):
        """ Returns the number of the measure in which the point is located.
         Requires this point-set to either have a score or the measure line positions.

         :param point: the point for which to return the measure number"""

        if self.score:
            note = self.get_notes(point)[0]
            if note.measureNumber:
                return note.measureNumber

        # Compute the measure number from the measure line positions if the score is missing
        # or for some reason the music21 note element does not have the measure number set (which
        # sometimes happens).
        return self.__get_measure_from_lines(point)

    def __get_measure_from_lines(self, point):
        for i in range(len(self.measure_line_positions) - 1):
            m_start = self.measure_line_positions[i]
            m_end = self.measure_line_positions[i + 1]

            if m_start <= point.onset_time < m_end:
                return i

        raise ValueError('No score or measure line positions, cannot return measure of point')

    def get_measure_range(self, pattern):
        """
        Returns the range of measures (inclusive) in the score associated with this point-set for the given pattern.
        The range of measures covers the whole pattern duration.
        :param pattern: the pattern for which to retrieve the measure range.
        :return: a pair (first, last) of measure numbers
        """

        first = self.get_measure(pattern[0])
        last = first
        for point in pattern:
            measure_numbers = [self.get_measure(point)]
            for p, n in self.__get_tie_continuations(point):
                if n.measureNumber:
                    measure_numbers.append(n.measureNumber)
                else:
                    measure_numbers.append(self.__get_measure_from_lines(p))

            last = max(measure_numbers)

        return first, last

    def get_pattern_span(self, pattern):
        """
        Returns the timespan of the pattern in the associated score (taking note durations into account).
        :param pattern: the pattern for which the span is computed
        :return: the timespan as (start, end) times, where start is the first onset time and end is
        ending time of the note that ends last in the pattern
        :raise ValueError: if this point-set doesn't have a score
        """
        if not self.score:
            raise ValueError('Cannot retrieve score region because score is None')

        pattern_start = pattern[0].onset_time
        pattern_end = pattern_start

        for point in pattern:
            pattern_end = max(
                round(point.onset_time + note.quarterLength, Point2d.decimal_places)
                for note in self.get_notes(point) + self.__get_tied_notes(point))

        return pattern_start, pattern_end

    def __eq__(self, other):
        """
        Returns true if this point-set is equal to other point-set in the contained points.
        Metadata is ignored.
        """
        return np.array_equal(self.as_numpy()[:, 0:2], other.as_numpy()[:, 0:2])

    def __hash__(self):
        """
        Returns the hash for this point-set based solely on the points contained (metadata is ignored).
        """
        return hash(str(self.as_numpy()[:, 0:2]))

    @staticmethod
    def __intersect(a_1, a_2, b_1, b_2):
        i_1 = max(a_1, b_1)
        i_2 = min(a_2, b_2)

        if i_1 >= i_2:
            return None

        return i_1, i_2

    @staticmethod
    def __get_part_id(note):

        voice = note.sites.getObjByClass('Voice')
        if voice:
            measure = voice.sites.getObjByClass('Measure')
        else:
            measure = note.sites.getObjByClass('Measure')

        if measure:
            part = measure.sites.getObjByClass('Part')
            if part:
                return part.id

        # Return None as the part id if it's not accessible through the note's sites.
        # Sites are not always set correctly for notes.
        return 'None'

    def __get_tie_continuations(self, point):
        if point in self.__tie_continuations:
            return self.__tie_continuations[point]

        return []

    def __get_tied_notes(self, point):
        return [n for p, n in self.__get_tie_continuations(point)]

    def get_pattern_notes(self, pattern, discard_unisons=True):
        """
        Returns the notes in the given pattern as a list.

        :param pattern: the pattern for which the notes are retrieved
        :param discard_unisons: set to true to discard unison notes by preferring notes from a part that is more common
        :return: the notes in the given pattern as a list
        """
        return [t[2] for t in self.__get_point_part_note_triples(pattern, discard_unisons)]

    def __get_point_part_note_triples(self, pattern, discard_unisons):
        triples = []

        if discard_unisons:
            part_counts = self.__part_counts(pattern)

            for point in pattern:
                notes = self.get_notes(point)
                if len(notes) == 1:
                    note = notes[0]
                    self.__add_ppn_triples(note, self.__get_part_id(note), point, triples)
                else:
                    note = max(((n, part_counts[self.__get_part_id(n)]) for n in notes), key=itemgetter(1))[0]
                    part_id = self.__get_part_id(note)
                    self.__add_ppn_triples(note, part_id, point, triples)
        else:
            for point in pattern:
                for note in self.get_notes(point):
                    part_id = self.__get_part_id(note)
                    self.__add_ppn_triples(note, part_id, point, triples)

        return triples

    def __add_ppn_triples(self, note, part_id, point, triples):
        triples.append((point, part_id, note))
        for p, n in self.__get_tie_continuations(point):
            if self.__get_part_id(n) == part_id:
                triples.append((p, self.__get_part_id(n), n))

    def __part_counts(self, pattern):
        part_counts = {}
        for point in pattern:
            notes = self.get_notes(point)
            for note in notes:
                part_id = self.__get_part_id(note)
                if part_id not in part_counts:
                    part_counts[part_id] = 0

                part_counts[part_id] += 1

        return part_counts

    def get_pattern_notation(self, pattern, discard_unisons=True):
        """
        Returns the music notation for the given pattern as a music21 stream.

        :param pattern: the pattern for which to return the notation
        :param discard_unisons: set to true to avoid getting multiple notes for a point produced from a union
        :return: the music notation for the given point pattern
        :raise ValueError: if this point-set doesn't have a score
        """
        if not self.score:
            raise ValueError('Cannot retrieve score region because score is None')

        first_measure, last_measure = self.get_measure_range(pattern)
        measures = self.score.measures(first_measure, last_measure)
        first_in_selection = measures.flatten().notes.first()

        global_offset = self.__compute_global_offset(first_in_selection)

        stream = deepcopy(measures)
        flattened_notes = stream.flatten().notes.stream()

        # As the equality and hash for music21 notes is not usable for this purpose,
        # use triples of onset time, part id, and notename with octave for checking membership in pattern.
        onset_part_pitch_triples = set((t[0].onset_time, t[1], t[2].nameWithOctave) for t in
                                       self.__get_point_part_note_triples(pattern, discard_unisons))

        for elem in flattened_notes:
            onset_time = round(elem.offset + global_offset, Point2d.decimal_places)

            if isinstance(elem, m21.note.Note):
                if (onset_time, self.__get_part_id(elem), elem.nameWithOctave) not in onset_part_pitch_triples:
                    flattened_notes.replace(elem, m21.note.Rest(elem.duration.quarterLength), allDerived=True)
            if isinstance(elem, m21.chord.Chord) and not isinstance(elem, m21.harmony.ChordSymbol):
                notes_to_remove = []

                for note in elem:
                    # Get the part id using the chord because notes in chords for not have the containing
                    # measure in their sites.
                    if (onset_time, self.__get_part_id(elem), note.nameWithOctave) not in onset_part_pitch_triples:
                        notes_to_remove.append(note)

                if len(notes_to_remove) == len(elem.notes):
                    flattened_notes.replace(elem, m21.note.Rest(elem.duration.quarterLength), allDerived=True)
                else:
                    for n in notes_to_remove:
                        elem.remove(n)

        return stream

    def get_score_region(self, pattern, boundaries='exclude'):
        """
        Returns the region (timespan) of the score where the pattern occurs as a music21 stream.

        :param pattern: the pattern for which to return the region of the score
        :param boundaries: defines how notes that cross the boundaries of the timespan are handled. 'exclude'
        excludes them, 'include' includes them unaffected, and 'truncate' truncates the notes so that only the
        part of the note that fits into the timespan is included.
        :return: the region (time-span) of the score where the pattern occurs
        :raise ValueError: if this point-set doesn't have a score
        """
        if not self.score:
            raise ValueError('Cannot retrieve score region because score is None')

        first_measure, last_measure = self.get_measure_range(pattern)
        measures = self.score.measures(first_measure, last_measure)
        first_in_selection = measures.flatten().notes.first()

        global_offset = self.__compute_global_offset(first_in_selection)

        pattern_start, pattern_end = self.get_pattern_span(pattern)

        stream = deepcopy(measures)
        flattened_notes = stream.flatten().notes.stream()

        for note in flattened_notes:
            onset_time = round(note.offset + global_offset, Point2d.decimal_places)
            end_time = round(onset_time + note.quarterLength, Point2d.decimal_places)

            intersection = self.__intersect(pattern_start, pattern_end, onset_time, end_time)
            replace_with_rest = False

            if not intersection:
                replace_with_rest = True

            if intersection:
                if onset_time < intersection[0]:
                    if boundaries == 'truncate':
                        # TODO: add rest before the truncated note
                        time_reduction = pattern_start - onset_time
                        note.offset += time_reduction
                        note.duration.quarterLength -= time_reduction
                    if boundaries == 'exclude':
                        replace_with_rest = True

                if intersection[1] < end_time:
                    if boundaries == 'truncate':
                        # TODO: add rest after the truncated note
                        note.duration.quarterLength -= end_time - pattern_end
                    if boundaries == 'exclude':
                        replace_with_rest = True

            if replace_with_rest:
                flattened_notes.replace(note, m21.note.Rest(note.duration.quarterLength), allDerived=True)

        return stream

    def __compute_global_offset(self, first_in_selection):
        """ Returns the offset from the beginning of the first full measure in a music21 score. """
        pickup_measure = self.score.measure(0)
        pickup_duration = pickup_measure.quarterLength if pickup_measure else 0.0
        global_offset = first_in_selection.getOffsetBySite(
            self.score.flatten()) - first_in_selection.offset - pickup_duration
        return global_offset


class Pattern2d(PointSet2d):
    """ Represents a pattern in a 2-dimensional point-set representation of music. """

    def __init__(self, points: List[Point2d], label: str, source: str, piece_name=None, dtype=float,
                 pitch_type='chromatic', pattern_id=None, additional_data=None):
        """
        Creates a new pattern.

        :param points: the points of the pattern
        :param label: a label associated with the pattern
        :param source: the source of the pattern, e.g, annotator or algorithm that produced the pattern
        :param piece_name: the name of the piece in which the pattern occurs
        :param dtype: the datatype of the point components
        :param pitch_type: the type of the pitch (chromatic or morphetic)
        :param pattern_id: the identifier of the pattern
        :param additional_data: an optional dictionary of additional data to add to this pattern
        """
        super().__init__(points, piece_name, dtype, point_set_id=pattern_id)
        self.label = label
        self.source = source
        self._pitch_type = pitch_type
        self.additional_data = additional_data

    @staticmethod
    def from_numpy(points_array, label: str, source: str, piece_name=None, pitch_type='chromatic'):
        points = []
        for i in range(len(points_array)):
            row = points_array[i, :]
            points.append(Point2d(row[0], row[1]))

        return Pattern2d(points, label, source, piece_name, dtype=points_array.dtype, pitch_type=pitch_type)

    def to_dict(self):
        return {'label': self.label,
                'source': self.source,
                'representation': 'point_set',
                'pitch_type': self.pitch_type,
                'dtype': self._dtype_to_str(),
                'id': self.id,
                'piece_name': self.piece_name,
                'data': self._points[:, 0:2].tolist(),
                'additional_data': self.additional_data}

    def __str__(self):
        return f'[{self.label}; {self.source}; {self._dtype}: {self._points}]'

    def __len__(self):
        return self._points.shape[0]

    @staticmethod
    def from_dict(input_dict):
        label = input_dict['label']
        source = input_dict['source']
        data_type = input_dict['dtype']
        pitch_type = input_dict['pitch_type']
        points = list(map(lambda row: Point2d(row[0], row[1]), input_dict['data']))
        pattern_id = input_dict['id'] if 'id' in input_dict else None
        piece_name = input_dict['piece_name'] if 'piece_name' in input_dict else None

        dtype = float
        if data_type == 'int':
            dtype = int

        additional_data = input_dict['additional_data'] if 'additional_data' in input_dict else None

        return Pattern2d(points, label, source, dtype=dtype, pitch_type=pitch_type, pattern_id=pattern_id,
                         additional_data=additional_data, piece_name=piece_name)

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
        pattern.piece_name = piece
        occurrences = []
        for occ_dict in input_dict['occurrences']:
            occ = Pattern2d.from_dict(occ_dict)
            if not occ.piece_name:
                occ.piece_name = piece

            occurrences.append(occ)

        return PatternOccurrences2d(piece, pattern, occurrences)
