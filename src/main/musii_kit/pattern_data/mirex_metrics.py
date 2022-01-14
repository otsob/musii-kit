from typing import List

import numpy as np

from musii_kit.point_set.point_set import Pattern, PatternOccurrences

"""
Defines metrics used in MIREX 2017 competition for repeated patterns 
(see https://www.music-ir.org/mirex/wiki/2017:Discovery_of_Repeated_Themes_%26_Sections#Evaluation_Procedure).
"""


def __intersection(ground_truth, pattern) -> set:
    a_set = set([tuple(x) for x in ground_truth.points()])
    b_set = set([tuple(x) for x in pattern.points()])
    return a_set & b_set


def cardinality_score(ground_truth: Pattern, pattern: Pattern):
    return len(__intersection(ground_truth, pattern)) / max(len(ground_truth), len(pattern))


# Establishment scores
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
    return f_score(p_est, r_est)


def f_score(precision, recall):
    if recall == 0.0:
        return 0.0

    if precision == 0.0:
        return 0.0

    return (2 * precision * recall) / (precision + recall)


# Three layer scores
def __layer_one_f1(gt_pattern, output_pattern):
    intersection_size = len(__intersection(gt_pattern, output_pattern))
    p_l1 = intersection_size / len(output_pattern)
    r_l1 = intersection_size / len(gt_pattern)

    return f_score(p_l1, r_l1)


def __layer_two_f_score(gt_occurrences: PatternOccurrences, output_occurrences: PatternOccurrences):
    layer_one_f1_matrix = score_matrix(gt_occurrences, output_occurrences, score=__layer_one_f1)
    layer_two_precision = np.mean(np.amax(layer_one_f1_matrix, axis=0))
    layer_two_recall = np.mean(np.amax(layer_one_f1_matrix, axis=1))

    return f_score(layer_two_precision, layer_two_recall)


def layer_two_f_score_matrix(ground_truth: List[PatternOccurrences], output_patterns: List[PatternOccurrences]):
    n_gt = len(ground_truth)
    n_pat = len(output_patterns)

    f1_matrix = np.zeros((n_gt, n_pat), dtype=float)

    for row in range(n_gt):
        for col in range(n_pat):
            f1_matrix[row, col] = __layer_two_f_score(ground_truth[row], output_patterns[col])

    return f1_matrix


def three_layer_precision(l2_f_score_matrix):
    return np.mean(np.amax(l2_f_score_matrix, axis=0))


def three_layer_recall(l2_f_score_matrix):
    return np.mean(np.amax(l2_f_score_matrix, axis=1))


def three_layer_f_score(l2_f_score_matrix):
    precision = three_layer_precision(l2_f_score_matrix)
    recall = three_layer_recall(l2_f_score_matrix)

    return f_score(precision, recall)
