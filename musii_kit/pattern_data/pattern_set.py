import os

import pandas as pd

from musii_kit.point_set.point_set import PointSet2d
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

    @staticmethod
    def from_path(path, pitch_extractor=PointSet2d.chromatic_pitch):
        """
        Creates a new pattern dataset from the files in the directory at the given path.
        All JSON files are considered to contain pattern occurrences and all CSV and MusicXml (.musicxml/.mxl)
        files are assumed to be pieces in point-set format or as scores.
        The JSON files must reference the compositions/pieces by the exact filenames of the csv files or
        titles of the MusicXML scores.

        :param path: the path from which the pattern JSON and score/pointset files are read
        :param pitch_extractor: the pitch extractor to use when reading point-sets from MusicXML
        """
        return PatternSet(PatternSet.__collect_data(path, pitch_extractor))

    @staticmethod
    def __collect_data(path, pitch_extractor):
        data = []

        compositions, patterns = PatternSet.__collect_compositions_and_patterns(path, pitch_extractor)
        for composition in compositions:

            if composition in patterns:
                data.append((compositions[composition], patterns[composition]))
            else:
                print(f'No patterns for composition {composition} found! Excluded the composition.')

        return data

    @staticmethod
    def __collect_compositions_and_patterns(path, pitch_extractor):
        compositions = {}
        patterns = {}

        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.csv'):
                    df = pd.read_csv(os.path.join(root, file), header=None)
                    piece = file[0:-4]
                    compositions[piece] = PointSet2d.from_numpy(df.to_numpy()[:, 0:2], piece_name=piece)
                if file.endswith('.musicxml') or file.endswith('.mxl'):
                    point_set = read_musicxml(os.path.join(root, file), pitch_extractor)
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
