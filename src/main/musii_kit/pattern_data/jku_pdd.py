import os
from pathlib import Path

import pandas as pd

from musii_kit.pattern_data.pattern_set import PatternSet
from musii_kit.point_set.point_set import Pattern, PatternOccurrences


class JkuPdd(PatternSet):
    """ JKU-PDD as a PyTorch compatible data set.

    In order to use this class, you need to download JKU-PDD and extract it to some path.
    The path is given as an argument when creating an instance of JkuPdd.

    The data is stored as triples:
    0: The composition name as defined in JKU-PDD directory structure combined with _polyphonic or _monophonic
    1: A 2-dimensional point set of the composition (onset, chromatic pitch)
    2: List of PatternOccurrences of all patterns annotated for the composition

    The sectionalRepetitions data is omitted from this data set.
    """

    def __init__(self, path, corpus=['polyphonic', 'monophonic']):
        """
        Creates a data set of JKU-PDD.

        :param path: the path to JKU-PDD directory
        :param corpus: list that defines which parts of JKU-PDD to load (polyphonic, monophonic, or both)
        """

        self._base_path = Path(path)
        self._corpus = corpus
        self._data = self.__collect_dataset()

    def __list_data_paths(self):
        paths = []

        for root, directories, files in os.walk(self._base_path):
            for directory in directories:
                if directory in self._corpus:
                    paths.append(os.path.join(root, directory))

        return paths

    def __collect_patterns(self, base_path, labels, composition, analyst):
        patterns = []

        for label in labels:
            pattern_path = os.path.join(base_path, label)
            occurrences_csv_path = os.path.join(pattern_path, 'occurrences', 'csv')
            occ_files = filter(lambda file: file.endswith('csv'), next(os.walk(occurrences_csv_path))[2])
            occurrences = []
            for occ_file in occ_files:
                occ_csv_path = os.path.join(occurrences_csv_path, occ_file)
                occurrences.append(self.__read_pattern(occ_csv_path, label, analyst))

            patterns.append(PatternOccurrences(composition, occurrences[0], occurrences[1:]))

        return patterns

    def __read_pattern(self, pattern_csv_path, label, analyst):
        points_pd = pd.read_csv(pattern_csv_path, header=None)
        points = points_pd.to_numpy()

        return Pattern(points, label=label, source=analyst)

    def __get_composition_point_set(self, data_path):
        csv_path = list(filter(lambda path: path.endswith('csv'), next(os.walk(os.path.join(data_path, 'csv')))[2]))[0]
        df = pd.read_csv(os.path.join(data_path, 'csv', csv_path), header=None)
        return df.to_numpy()[:, 0:2]

    def __collect_dataset(self):
        data_paths = self.__list_data_paths()
        data_set = []

        for data_path in data_paths:
            patterns_path = os.path.join(data_path, 'repeatedPatterns')
            analysts = next(os.walk(patterns_path))[1]
            if 'sectionalRepetitions' in analysts:
                analysts.remove('sectionalRepetitions')

            composition = data_path.split('/')[-2] + '_' + data_path.split('/')[-1]
            pattern_occurrences = []

            for analyst in analysts:
                analyst_path = os.path.join(patterns_path, analyst)
                pattern_labels = next(os.walk(analyst_path))[1]
                pattern_occurrences.extend(self.__collect_patterns(analyst_path, pattern_labels, composition, analyst))

            data_set.append((composition, self.__get_composition_point_set(data_path), pattern_occurrences))

        return data_set

    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data[item]
