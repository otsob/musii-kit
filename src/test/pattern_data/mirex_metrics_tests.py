import unittest

import numpy as np

import musii_kit.pattern_data.mirex_metrics as mirex
from musii_kit.point_set.point_set import Pattern, PatternOccurrences


class MirexMetricsTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(MirexMetricsTests, self).__init__(*args, **kwargs)
        piece = 'Test piece'
        self.pattern_a = Pattern(np.array([[1.0, 2.0], [2.0, 2.0], [3.0, 4.0]]), 'A', 'Analyst')
        self.pattern_b = Pattern(np.array([[1.5, 2.0], [2.0, 2.0], [3.0, 4.0], [5.0, 6.0]]), 'B', 'Analyst')

        self.occ_a = PatternOccurrences(piece, self.pattern_a,
                                        [Pattern(self.pattern_a.points() + np.array([10.0, 2.0]),
                                                 'A', 'Analyst'),
                                         Pattern(self.pattern_a.points() + np.array([20.0, 2.0]),
                                                 'A', 'Analyst')])

        self.occ_b = PatternOccurrences(piece, self.pattern_b,
                                        [Pattern(self.pattern_b.points() + np.array([10.0, 2.0]),
                                                 'B', 'Analyst'),
                                         Pattern(self.pattern_b.points() + np.array([20.0, 2.0]),
                                                 'B', 'Analyst'),
                                         Pattern(self.pattern_b.points() + np.array([30.0, 2.0]),
                                                 'B', 'Analyst')])

    def test_cardinality_score(self):
        cardinality_score = mirex.cardinality_score(self.pattern_a, self.pattern_b)

        self.assertEqual(0.5, cardinality_score)

    def test_score_matrix(self):
        scores_with_self = mirex.score_matrix(self.occ_a, self.occ_a)
        self.assertTrue(np.array_equal(np.diag([1.0, 1.0, 1.0]), scores_with_self))

        scores_with_another = mirex.score_matrix(self.occ_a, self.occ_b)
        expected = np.zeros((3, 4))
        expected[0, 0] = 0.5
        expected[1, 1] = 0.5
        expected[2, 2] = 0.5
        self.assertTrue(np.array_equal(expected, scores_with_another))

    def test_establishment_matrix(self):
        patterns = [self.occ_a, self.occ_a]
        est_matrix = mirex.establishment_matrix(patterns, patterns)
        self.assertTrue(np.array_equal(np.ones((2, 2), dtype=float), est_matrix))

        ground_truth = [self.occ_a, self.occ_b, self.occ_b]
        est_matrix = mirex.establishment_matrix(ground_truth, patterns)
        expected = np.array([[1.0, 1.0],
                             [0.5, 0.5],
                             [0.5, 0.5]],
                            dtype=float)

        self.assertTrue(np.array_equal(expected, est_matrix))

    def test_establishment_recall(self):
        patterns = [self.occ_a, self.occ_a]
        est_matrix = mirex.establishment_matrix(patterns, patterns)
        self.assertEqual(1.0, mirex.establishment_precision(est_matrix))

        ground_truth = [self.occ_b, self.occ_b, self.occ_b]
        est_matrix = mirex.establishment_matrix(ground_truth, patterns)
        self.assertEqual(0.5, mirex.establishment_precision(est_matrix))

    def test_establishment_recall(self):
        patterns = [self.occ_a, self.occ_a]
        est_matrix = mirex.establishment_matrix(patterns, patterns)
        self.assertEqual(1.0, mirex.establishment_recall(est_matrix))

        ground_truth = [self.occ_a, self.occ_b, self.occ_b]
        est_matrix = mirex.establishment_matrix(ground_truth, patterns)
        self.assertEqual(2.0 / 3.0, mirex.establishment_recall(est_matrix))

    def test_establishment_f1(self):
        patterns = [self.occ_a, self.occ_a]
        est_matrix = mirex.establishment_matrix(patterns, patterns)
        self.assertEqual(1.0, mirex.establishment_f1(est_matrix))

        ground_truth = [self.occ_a, self.occ_b, self.occ_b]
        est_matrix = mirex.establishment_matrix(ground_truth, patterns)
        self.assertEqual(2 * 1.0 * (2.0 / 3.0) / (1.0 + (2.0 / 3.0)), mirex.establishment_f1(est_matrix))

    def test_three_layer_metrics(self):
        patterns = [self.occ_a, self.occ_a]
        # Simple sanity check test
        f_score_mat = mirex.layer_two_f_score_matrix(patterns, patterns)
        self.assertEqual(1.0, mirex.three_layer_precision(f_score_mat))
        self.assertEqual(1.0, mirex.three_layer_recall(f_score_mat))
        self.assertEqual(1.0, mirex.three_layer_f_score(f_score_mat))
