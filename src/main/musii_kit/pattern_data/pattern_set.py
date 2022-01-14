import os
from pathlib import Path

import pandas as pd
from torch.utils.data import Dataset

from musii_kit.point_set.point_set_io import read_patterns_from_json


class PatternSet(Dataset):
    """
    A PyTorch compatible dataset of patterns and their occurrences read from JSON.

    The data is handled as triples:
    0: The composition name as defined in csv-filenames
    1: A 2-dimensional point set of the composition (onset, pitch)
    2: List of PatternOccurrences of all patterns annotated for the composition

    The input directory is expected to have the following structure:
    - composition_a
        - composition_a.csv
        - patterns1.json
        - ...
        - patternsN.json
    - composition_b
        - composition_b.csv
        - patterns1.json
        - ...
        - patternsN.json

    where the CSV file and all patterns for the same composition are under the same directory.
    Each JSON file is expected to contain all occurrences of a single pattern. The composition.csv name
    must match the directory name exactly.
    """

    def __init__(self, path):
        """
        Creates a new pattern dataset from the files in the directory at the given path.
        All JSON files are considered to contain pattern occurrences and all CSV files are
        assumed to be pieces in point set format. The JSON files must reference the compositions/pieces
        by the exact filenames of the csv files.

        :param path: the path from which the pattern JSON files are read
        """
        self._path = Path(path)
        self._data = self.__collect_data()

    def __collect_data(self):
        data = []

        compositions, patterns = self.__collect_compositions_and_patterns()
        for composition in compositions:
            data.append((composition, compositions[composition], patterns[composition]))

        return data

    def __collect_compositions_and_patterns(self):
        compositions = {}
        patterns = {}

        for root, _, files in os.walk(self._path):
            for file in files:
                if file.endswith('.csv'):
                    df = pd.read_csv(os.path.join(root, file), header=None)
                    compositions[file[0:-4]] = df.to_numpy()[:, 0:2]
                if file.endswith('.json'):
                    pat_occ = read_patterns_from_json(os.path.join(root, file))
                    piece = pat_occ.piece
                    if piece not in patterns:
                        patterns[piece] = []

                    patterns[piece].append(pat_occ)

        return compositions, patterns

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data[item]
