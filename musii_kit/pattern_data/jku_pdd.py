import os
from pathlib import Path

import numpy as np
import pandas as pd

from musii_kit.pattern_data.pattern_set import PatternSet
from musii_kit.point_set.point_set import PatternOccurrences2d, PointSet2d, Pattern2d


class JkuPdd(PatternSet):
    """ JKU-PDD as a PatternSet.

    In order to use this class, you need to download JKU-PDD and extract it to some path.
    The path is given as an argument when creating an instance of JkuPdd.
    """

    def __init__(self, path, corpus=['polyphonic', 'monophonic'], pitch_type='chromatic'):
        """
        Creates a data set of JKU-PDD.

        :param path: the path to JKU-PDD directory
        :param corpus: list that defines which parts of JKU-PDD to load (polyphonic, monophonic, or both)
        :param pitch_type: the type of pitch enconding to use (chromatic or morphetic)
        """
        self._pitch_type = pitch_type
        if self._pitch_type == 'chromatic':
            self._pitch_col = 1
        elif self._pitch_type == 'morphetic':
            self._pitch_col = 2
        else:
            raise ValueError(f'pitch_type must be one of [chromatic, morphetic], was {pitch_type}')

        self._base_path = Path(path)
        self._corpus = corpus
        data = self.__collect_dataset()
        super().__init__(data)

    def __list_data_paths(self):
        paths = []

        for root, directories, files in os.walk(self._base_path):
            for directory in directories:
                if directory in self._corpus:
                    paths.append(os.path.join(root, directory))

        return paths

    @staticmethod
    def __chromatic_to_morphetic_points(pattern_array, composition_array):
        p_i = 0
        c_i = 0

        # Assuming points are in ascending lexicographic order in patterns and compositions,
        # a single scan of both should be sufficient for finding intersection based on chromatic
        # pitch numbers.
        morphetic_points = []
        while p_i < len(pattern_array) and c_i < len(composition_array):
            p = pattern_array[p_i, :]
            c = composition_array[c_i, :]

            if p[0] == c[0] and p[1] == c[1]:
                morphetic_points.append([c[0], c[2]])
                p_i += 1
                c_i += 1
            elif p[0] < c[0] or (p[0] == c[0] and p[1] < c[1]):
                p_i += 1
            else:
                c_i += 1

        return np.array(morphetic_points)

    def __collect_patterns(self, base_path, labels, composition, analyst, composition_array):
        patterns = []

        for label in labels:
            pattern_path = os.path.join(base_path, label)
            occurrences_csv_path = os.path.join(pattern_path, 'occurrences', 'csv')
            occ_files = filter(lambda file: file.endswith('csv'), next(os.walk(occurrences_csv_path))[2])
            occurrences = []
            for occ_file in occ_files:
                occ_csv_path = os.path.join(occurrences_csv_path, occ_file)
                pattern_array = self.__read_pattern_array(occ_csv_path)
                if self._pitch_type == 'morphetic':
                    # Match the chromatic pattern points to the whole point-set to find the
                    # morphetic pitch numbers.
                    pattern_array = self.__chromatic_to_morphetic_points(pattern_array, composition_array)

                occurrences.append(
                    Pattern2d.from_numpy(pattern_array, label, analyst, pitch_type=self._pitch_type))

            # The first occurrence in the 'occurrences' directory corresponds to the prototypical version
            # of the pattern in JKU-PDD.
            patterns.append(PatternOccurrences2d(composition, occurrences[0], occurrences[1:]))

        return patterns

    def __read_pattern_array(self, pattern_csv_path):
        points_pd = pd.read_csv(pattern_csv_path, header=None)
        return points_pd.to_numpy()

    def __get_composition_array(self, data_path):
        csv_path = list(filter(lambda path: path.endswith('csv'), next(os.walk(os.path.join(data_path, 'csv')))[2]))[0]
        df = pd.read_csv(os.path.join(data_path, 'csv', csv_path), header=None)
        return df.to_numpy()

    def __collect_dataset(self):
        data_paths = self.__list_data_paths()
        data_set = []

        for data_path in data_paths:
            patterns_path = os.path.join(data_path, 'repeatedPatterns')
            composition_array = self.__get_composition_array(data_path)
            analysts = next(os.walk(patterns_path))[1]

            composition = data_path.split('/')[-2] + '_' + data_path.split('/')[-1]
            pattern_occurrences = []

            # For polyphonic corpus barlowAndMorgenstern should be
            # excluded.
            if 'polyphonic' in data_path and 'barlowAndMorgenstern' in analysts:
                analysts.remove('barlowAndMorgenstern')

            for analyst in analysts:
                analyst_path = os.path.join(patterns_path, analyst)
                pattern_labels = next(os.walk(analyst_path))[1]
                pattern_occurrences.extend(
                    self.__collect_patterns(analyst_path, pattern_labels, composition, analyst, composition_array))

            data_set.append((PointSet2d.from_numpy(composition_array[:, [0, self._pitch_col]], piece_name=composition,
                                                   pitch_type=self._pitch_type),
                             pattern_occurrences))

        return data_set
