import json
import os

import pandas as pd

from musii_kit.point_set.point_set import PointSet2d, PatternOccurrences2d
from musii_kit.point_set.point_set_io import read_patterns_from_json, read_musicxml


class PatternSet:
    """
    A dataset of point-set patterns and their occurrences.

    The data is handled as pairs:
    0: A 2-dimensional point set of the composition (onset, pitch)
    1: List of PatternOccurrences of all patterns annotated for the composition

    The input directory is expected to contain the pieces/compositions as csv or MusicXML (.musicxml/.mxl) files
    and the patterns as JSON files. The input directory is expected to only contain
    patterns from a single source (i.e. algorithm or annotator). The same input directory
    can contain multiple pieces and pattern JSON files for those pieces.
    The piece .csv file names must match exactly the piece names denoted in the JSON
    files in order for the patterns to be associated with the correct piece.
    """

    def __init__(self, data):
        """
        Creates a new pattern dataset with the given data.
        The data is handled as pairs:
        0: A 2-dimensional point set of the composition (onset, pitch)
        1: List of PatternOccurrences of all patterns annotated for the composition

        :param data: the pattern data for point-sets as a list of pairs (point-set, [pattern occurrences])
        """
        self._data = data
        self._point_sets = {}
        self._patterns = {}
        self._contents_set = set()
        for item in self._data:
            point_set = item[0]
            self._contents_set.add(point_set)
            self._point_sets[point_set.id] = point_set
            pattern_occurrences = item[1]
            for occurrences in pattern_occurrences:
                for pattern in occurrences:
                    pattern.piece_name = point_set.piece_name
                    self._patterns[pattern.id] = pattern
                    self._contents_set.add(pattern)

    def __contains__(self, item):
        """ Returns true if this pattern set contains the given point-set or pattern """
        return item in self._contents_set

    def get_pattern(self, pattern_id):
        """
        Returns the pattern with the given id from this pattern set.
        :param pattern_id: the id of the pattern to return
        :return: the pattern with the given id from this pattern set
        """
        return self._patterns[pattern_id]

    def get_point_set(self, point_set_id):
        """
        Returns the point-set with the given id from this pattern set.
        :param point_set_id: the id of the point-set to return
        :return: the point-set with the given id from this pattern set
        """
        return self._point_sets[point_set_id]

    def get_point_set_by_name(self, piece_name):
        """
        Returns the point-set with the given piece name.

        :param piece_name: the piece name of the point-set to return
        :return: the point-set with the given piece name
        """
        return self.__get_elem_by_piece_name(piece_name)[0]

    def add_patterns(self, patterns: PatternOccurrences2d, point_set_id=None, set_piece_name=False):
        """
        Adds the given pattern occurrences to the corresponding piece in this pattern set.
        The patterns are added to the point-set with the matching piece name, or if point_set_id is given,
        then the patterns are associated with the point-set with matching id.

        :param patterns: the patterns to add as a pattern occurrences object
        :param point_set_id: (optional) the id of the point-set with which to associate the added patterns
        :param set_piece_name: set the piece_name of the patterns to match the piece with which they are associated
        """
        if point_set_id:
            elem = self.__get_elem_by_point_set_id(point_set_id)
        else:
            piece_name = patterns.pattern.piece_name
            elem = self.__get_elem_by_piece_name(piece_name)

        if set_piece_name:
            for p in patterns:
                p.piece_name = elem[0].piece_name

        elem[1].append(patterns)

    def __get_elem_by_piece_name(self, piece_name):
        for elem in self:
            if elem[0].piece_name == piece_name:
                return elem

        raise ValueError(f'No piece with name {piece_name}')

    def __get_elem_by_point_set_id(self, ps_id):
        for elem in self:
            if elem[0].id == ps_id:
                return elem

        raise ValueError(f'No piece with point-set-id {ps_id}')

    @staticmethod
    def from_path(path, pitch_extractor=PointSet2d.chromatic_pitch, expand_repetitions=False):
        """
        Creates a new pattern dataset from the files in the directory at the given path.
        All JSON files are considered to contain pattern occurrences and all CSV and MusicXml (.musicxml/.mxl)
        files are assumed to be pieces in point-set format or as scores.
        The JSON files must reference the compositions/pieces by the exact filenames of the csv files or
        titles of the MusicXML scores.

        :param path: the path from which the pattern JSON and score/pointset files are read
        :param pitch_extractor: the pitch extractor to use when reading point-sets from MusicXML
        :param expand_repetitions: set to true to expand repetitions in scores when creating the point-sets
        """
        return PatternSet(PatternSet.__collect_data(path, pitch_extractor, expand_repetitions))

    @staticmethod
    def __collect_data(path, pitch_extractor, expand_repetitions):
        data = []

        compositions, patterns = PatternSet.__collect_compositions_and_patterns(path, pitch_extractor,
                                                                                expand_repetitions)
        for composition in compositions:
            if composition in patterns:
                data.append((compositions[composition], patterns[composition]))
            else:
                print(f'No patterns for composition {composition} found! Excluded the composition.')

        return data

    @staticmethod
    def __collect_compositions_and_patterns(path, pitch_extractor, expand_repetitions):
        compositions = {}
        patterns = {}

        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.csv'):
                    df = pd.read_csv(os.path.join(root, file), header=None)
                    piece = file[0:-4]
                    compositions[piece] = PointSet2d.from_numpy(df.to_numpy()[:, 0:2], piece_name=piece)
                if file.endswith('.musicxml') or file.endswith('.mxl'):
                    point_set = read_musicxml(os.path.join(root, file), pitch_extractor, expand_repetitions)
                    piece = point_set.piece_name
                    compositions[piece] = point_set
                if file.endswith('.json'):
                    pat_occurrences = read_patterns_from_json(os.path.join(root, file))
                    for pat_occ in pat_occurrences:
                        piece = pat_occ.piece
                        if piece not in patterns:
                            patterns[piece] = []

                        patterns[piece].append(pat_occ)

        return compositions, patterns

    def get_composition_size(self, piece_name):
        for pair in self._data:
            if pair[0].piece_name == piece_name:
                return len(pair[0])

        return None

    def get_pattern_count(self, piece_name):
        for pair in self._data:
            if pair[0].piece_name == piece_name:
                return len(pair[1])

        return None

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data[item]

    def to_dict(self):
        """
        Returns a dictionary of this pattern set with the piece/composition names as keys,
        and for each composition its point-set and all pattern occurrences.

        :return: a dictionary of this pattern set
        """
        pattern_set_dict = {}
        for i in range(len(self)):
            point_set = self[i][0]
            patterns = self[i][1]
            pattern_set_dict[point_set.piece_name] = {
                'point-set': point_set.to_dict(),
                'patterns': [occs.to_dict() for occs in patterns]
            }

        return pattern_set_dict

    @staticmethod
    def from_dict(input_dict):
        data = []

        for piece_name in input_dict:
            point_set = PointSet2d.from_dict(input_dict[piece_name]['point-set'])
            pattern_contents = input_dict[piece_name]['patterns']

            if isinstance(pattern_contents, list):
                patterns = [PatternOccurrences2d.from_dict(elem) for elem in pattern_contents]
            else:
                patterns = [PatternOccurrences2d.from_dict(pattern_contents)]

            data.append((point_set, patterns))

        return PatternSet(data)

    @staticmethod
    def write_to_json(pattern_set, output_path):
        """
        Writes the given pattern set into json to the output path.
        :param pattern_set: the pattern set to write
        :param output_path: the path where the json is stored
        """
        with open(output_path, 'w') as outfile:
            json.dump(pattern_set.to_dict(), outfile, indent=2)

    @staticmethod
    def read_from_json(input_path):
        """
        Returns a pattern set read from a JSON file in the given path.
        :param input_path: the path from which the JSON is read
        :return: a pattern set read from a JSON file
        """
        with open(input_path, 'r') as input_file:
            return PatternSet.from_dict(json.loads(input_file.read()))
