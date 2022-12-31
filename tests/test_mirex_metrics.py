import numpy as np

import musii_kit.pattern_data.mirex_metrics as mirex
from musii_kit.point_set.point_set import Pattern2d, PatternOccurrences2d


class TestMirexMetrics:
    piece = 'Test piece'
    pattern_a = Pattern2d.from_numpy(np.array([[1.0, 2.0], [2.0, 2.0], [3.0, 4.0]]), 'A', 'Analyst')
    pattern_b = Pattern2d.from_numpy(np.array([[1.5, 2.0], [2.0, 2.0], [3.0, 4.0], [5.0, 6.0]]), 'B', 'Analyst')

    occ_a = PatternOccurrences2d(piece, pattern_a,
                                 [Pattern2d.from_numpy(pattern_a.as_numpy() + np.array([10.0, 2.0, 10.0]),
                                                       'A', 'Analyst'),
                                  Pattern2d.from_numpy(pattern_a.as_numpy() + np.array([20.0, 2.0, 20.0]),
                                                       'A', 'Analyst')])

    occ_b = PatternOccurrences2d(piece, pattern_b,
                                 [Pattern2d.from_numpy(pattern_b.as_numpy() + np.array([10.0, 2.0, 10.0]),
                                                       'B', 'Analyst'),
                                  Pattern2d.from_numpy(pattern_b.as_numpy() + np.array([20.0, 2.0, 20.0]),
                                                       'B', 'Analyst'),
                                  Pattern2d.from_numpy(pattern_b.as_numpy() + np.array([30.0, 2.0, 30.0]),
                                                       'B', 'Analyst')])

    def test_cardinality_score(self):
        cardinality_score = mirex.cardinality_score(self.pattern_a, self.pattern_b)

        assert 0.5 == cardinality_score

    def test_score_matrix(self):
        scores_with_self = mirex.score_matrix(self.occ_a, self.occ_a)
        assert np.array_equal(np.diag([1.0, 1.0, 1.0]), scores_with_self)

        scores_with_another = mirex.score_matrix(self.occ_a, self.occ_b)
        expected = np.zeros((3, 4))
        expected[0, 0] = 0.5
        expected[1, 1] = 0.5
        expected[2, 2] = 0.5
        assert np.array_equal(expected, scores_with_another)

    def test_establishment_matrix(self):
        patterns = [self.occ_a, self.occ_a]
        est_matrix = mirex.establishment_matrix(patterns, patterns)
        assert np.array_equal(np.ones((2, 2), dtype=float), est_matrix)

        ground_truth = [self.occ_a, self.occ_b, self.occ_b]
        est_matrix = mirex.establishment_matrix(ground_truth, patterns)
        expected = np.array([[1.0, 1.0],
                             [0.5, 0.5],
                             [0.5, 0.5]],
                            dtype=float)

        assert np.array_equal(expected, est_matrix)

    def test_establishment_recall_with_homogeneous_gt(self):
        patterns = [self.occ_a, self.occ_a]
        est_matrix = mirex.establishment_matrix(patterns, patterns)
        assert 1.0 == mirex.establishment_precision(est_matrix)

        ground_truth = [self.occ_b, self.occ_b, self.occ_b]
        est_matrix = mirex.establishment_matrix(ground_truth, patterns)
        assert 0.5 == mirex.establishment_precision(est_matrix)

    def test_establishment_recall_with_heterogeneous_gt(self):
        patterns = [self.occ_a, self.occ_a]
        est_matrix = mirex.establishment_matrix(patterns, patterns)
        assert 1.0 == mirex.establishment_recall(est_matrix)

        ground_truth = [self.occ_a, self.occ_b, self.occ_b]
        est_matrix = mirex.establishment_matrix(ground_truth, patterns)
        assert 2.0 / 3.0 == mirex.establishment_recall(est_matrix)

    def test_establishment_f1(self):
        patterns = [self.occ_a, self.occ_a]
        est_matrix = mirex.establishment_matrix(patterns, patterns)
        assert 1.0 == mirex.establishment_f1(est_matrix)

        ground_truth = [self.occ_a, self.occ_b, self.occ_b]
        est_matrix = mirex.establishment_matrix(ground_truth, patterns)
        assert 2 * 1.0 * (2.0 / 3.0) / (1.0 + (2.0 / 3.0)) == mirex.establishment_f1(est_matrix)

    def test_three_layer_metrics(self):
        patterns = [self.occ_a, self.occ_a]
        # Simple sanity check tests
        f_score_mat = mirex.layer_two_f_score_matrix(patterns, patterns)
        assert 1.0 == mirex.three_layer_precision(f_score_mat)
        assert 1.0 == mirex.three_layer_recall(f_score_mat)
        assert 1.0 == mirex.three_layer_f_score(f_score_mat)

    def test_occurrence_metrics(self):
        patterns = [self.occ_a, self.occ_a]
        # Simple sanity check tests
        occ_ind = mirex.occurrence_indices(patterns, patterns)
        assert 1.0 == mirex.occurrence_precision(patterns, patterns, occ_ind)
        assert 1.0 == mirex.occurrence_recall(patterns, patterns, occ_ind)
        assert 1.0 == mirex.occurrence_f_score(patterns, patterns, occ_ind)
