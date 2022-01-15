from concurrent.futures import ProcessPoolExecutor

import musii_kit.pattern_data.mirex_metrics as mirex
from musii_kit.pattern_data.pattern_set import PatternSet


class Evaluator:
    """ Computes evaluation metrics for a pattern set against a ground truth pattern set.

    The datasets are expected to consist of triples following the convention used in
    the JkuPdd and PatternSet classes in this module.
     """

    EST_RECALL = 'establishment_recall'
    EST_PRECISION = 'establishment_precision'
    EST_F_SCORE = 'establishment_F1'
    TL_PRECISION = 'three-layer_precision'
    TL_RECALL = 'three-layer_recall'
    TL_F_SCORE = 'three-layer_F1'

    def __init__(self, ground_truth: PatternSet, process_count=8):
        """
        Creates a new evaluator.

        :param ground_truth: the ground truth against which the evaluator computes the metrics
        """
        self._ground_truth = ground_truth
        self._process_count = process_count

    @staticmethod
    def __group_by_composition(dataset: PatternSet):
        grouping = {}
        for i in range(len(dataset)):
            grouping[dataset[i][0]] = (dataset[i][1], dataset[i][2])

        return grouping

    def evaluate(self, dataset: PatternSet):
        """
        Returns a dictionary where each piece in the ground truth data set is a key and the
        value for that key is a dictionary of results.

        If there are pieces that are not present in both the ground truth and the given dataset,
        they are ignored.

        :param dataset: the data set that is evaluated
        :return: a dictionary of results grouped by piece in the ground truth.
        """

        ground_truth = Evaluator.__group_by_composition(self._ground_truth)
        evaluated_data = Evaluator.__group_by_composition(dataset)
        common_pieces = ground_truth.keys() & evaluated_data.keys()

        Evaluator.print_excluded_pieces(common_pieces, evaluated_data, ground_truth)

        evaluation_result = {}

        with ProcessPoolExecutor(max_workers=self._process_count) as executor:
            piece_result_futures = {}
            for piece in common_pieces:
                gt_patterns = ground_truth[piece][1]
                output_patterns = evaluated_data[piece][1]

                piece_result_futures[piece] = dispatch_piece_result_computations(executor, gt_patterns, output_patterns)

            for piece in piece_result_futures:
                evaluation_result[piece] = {}

                for piece_future in piece_result_futures[piece]:
                    evaluation_result[piece].update(piece_future.result())

        return evaluation_result

    @staticmethod
    def print_excluded_pieces(common_pieces, evaluated_data, ground_truth):
        excluded_gt_pieces = set(ground_truth.keys()).difference(common_pieces)
        excluded_evaluation_pieces = set(evaluated_data.keys()).difference(common_pieces)
        if excluded_gt_pieces:
            print(f'Ground truth pieces not found in given dataset {excluded_gt_pieces}')
        if excluded_evaluation_pieces:
            print(f'Pieces in given dataset not found in ground truth {excluded_evaluation_pieces}')


def dispatch_piece_result_computations(executor, gt_patterns, output_patterns):
    result_futures = [executor.submit(compute_establishment_scores, gt_patterns, output_patterns),
                      executor.submit(compute_three_layer_scores, gt_patterns, output_patterns)]
    return result_futures


def compute_establishment_scores(gt_patterns, output_patterns):
    est_scores = {}
    est_matrix = mirex.establishment_matrix(gt_patterns, output_patterns)
    p_est = mirex.establishment_precision(est_matrix)
    est_scores[Evaluator.EST_PRECISION] = p_est
    r_est = mirex.establishment_recall(est_matrix)
    est_scores[Evaluator.EST_RECALL] = r_est
    est_scores[Evaluator.EST_F_SCORE] = mirex.f_score(p_est, r_est)
    return est_scores


def compute_three_layer_scores(gt_patterns, output_patterns):
    tl_scores = {}
    tl_matrix = mirex.layer_two_f_score_matrix(gt_patterns, output_patterns)
    p_tl = mirex.three_layer_precision(tl_matrix)
    tl_scores[Evaluator.TL_PRECISION] = p_tl
    r_tl = mirex.three_layer_recall(tl_matrix)
    tl_scores[Evaluator.TL_RECALL] = r_tl
    tl_scores[Evaluator.TL_F_SCORE] = mirex.f_score(p_tl, r_tl)
    return tl_scores
