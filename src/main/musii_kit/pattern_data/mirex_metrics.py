from typing import List

import numpy as np

from musii_kit.point_set.point_set import Pattern, PatternOccurrences

"""
Defines metrics used in MIREX 2017 competition for repeated patterns 
(see https://www.music-ir.org/mirex/wiki/2017:Discovery_of_Repeated_Themes_%26_Sections#Evaluation_Procedure).
"""


def __intersection(a, b) -> set:
    a_set = set([tuple(x) for x in a])
    b_set = set([tuple(x) for x in b])
    return a_set & b_set


def cardinality_score(ground_truth: Pattern, pattern: Pattern):
    points_a = ground_truth.points()
    points_b = pattern.points()

    return len(__intersection(points_a, points_b)) / max(points_a.shape[0], points_b.shape[0])


def score_matrix(ground_truth: PatternOccurrences, patterns: PatternOccurrences, score=cardinality_score):
    n_gt = len(ground_truth)
    n_pat = len(patterns)

    scores = np.zeros((n_gt, n_pat), dtype=float)

    for row in range(n_gt):
        for col in range(n_pat):
            scores[row, col] = score(ground_truth[row], patterns[col])

    return scores


def establishment_matrix(ground_truth: List[PatternOccurrences], patterns: List[PatternOccurrences]):
    n_gt = len(ground_truth)
    n_pat = len(patterns)

    establishment = np.zeros((n_gt, n_pat), dtype=float)

    for row in range(n_gt):
        for col in range(n_pat):
            summary = np.max(score_matrix(ground_truth[row], patterns[col]))
            establishment[row, col] = summary

    return establishment


def establishment_precision(est_matrix):
    return np.mean(np.amax(est_matrix, axis=0))


def establishment_recall(est_matrix):
    return np.mean(np.amax(est_matrix, axis=1))


def establishment_f1(est_matrix):
    p_est = establishment_precision(est_matrix)
    r_est = establishment_recall(est_matrix)
    return basic_f1(p_est, r_est)


def basic_f1(precision, recall):
    return (2 * precision * recall) / (precision + recall)
