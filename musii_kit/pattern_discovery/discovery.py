from typing import List

import posemirpy.posemirpy as posemir
from musii_kit.point_set.point_set import Pattern2d, PatternOccurrences2d, PointSet2d


def run_siatec_c(pointset: PointSet2d, max_ioi) -> List[PatternOccurrences2d]:
    """
    Run pattern discovery using the SIATEC-C algorithm.

    :param pointset: the pointset on which to run the pattern discovery.
    :param max_ioi: maximum inter-onset-interval gap between two adjacent note events in a pattern
    :return: a list of all pattern occurrences the algorithm finds.
    """
    raw_output = posemir.run_siatec_c(pointset.as_numpy(), max_ioi)
    pattern_occurrences = []

    for arrays in raw_output:
        pattern = Pattern2d.from_numpy(arrays[0], label="", source=f'SIATEC-C ({max_ioi})')
        occurrences = []
        for occ_array in arrays[1]:
            occurrences.append(Pattern2d.from_numpy(occ_array, label="", source=f'SIATEC-C ({max_ioi})'))

        pattern_occurrences.append(PatternOccurrences2d('piece', pattern, occurrences))

    return pattern_occurrences
