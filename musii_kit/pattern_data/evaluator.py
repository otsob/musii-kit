from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

import pandas as pd

import musii_kit.pattern_data.mirex_metrics as mirex
from musii_kit.pattern_data.pattern_set import PatternSet


class Evaluator:
    """ Computes evaluation metrics for a pattern set against a ground truth pattern set.

    The datasets are expected to consist of triples following the convention used in
    the JkuPdd and PatternSet classes in this module.
     """

    PIECE = 'piece'

    EST_RECALL = 'R_est'
    EST_PRECISION = 'P_est'
    EST_F_SCORE = 'F1_est'
    TL_PRECISION = 'P_3L'
    TL_RECALL = 'R_3L'
    TL_F_SCORE = 'F1_3L'
    OCC_PRECISION = 'P_occ'
    OCC_RECALL = 'R_occ'
    OCC_F_SCORE = 'F1_occ'

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
            grouping[dataset[i][0].piece_name] = dataset[i]

        return grouping

    def evaluate(self, dataset: PatternSet):
        """
        Returns a pandas data frame of the results with a row for each evaluated piece and a column for each metric.

        If there are pieces that are not present in both the ground truth and the given dataset,
        they are ignored.

        :param dataset: the data set that is evaluated
        :return: a pandas data frame of the results with a row for each evaluated piece and a column for each metric
        """

        common_pieces = self._ground_truth.get_piece_names() & dataset.get_piece_names()

        Evaluator.print_excluded_pieces(common_pieces, self._ground_truth.get_piece_names(), dataset.get_piece_names())

        evaluation_result = {}

        with ProcessPoolExecutor(max_workers=self._process_count) as executor:
            piece_result_futures = {}
            for piece in common_pieces:
                gt_patterns = self._ground_truth.get_item_by_piece_name(piece)[1]
                output_patterns = dataset.get_item_by_piece_name(piece)[1]

                piece_result_futures[piece] = dispatch_piece_result_computations(executor, gt_patterns, output_patterns)

            for piece in piece_result_futures:
                evaluation_result[piece] = {Evaluator.PIECE: piece}

                evaluation_result[piece].update({
                    'N_points': dataset.get_composition_size(piece),
                    'N_pattern': dataset.get_pattern_count(piece),
                    'N_gt': self._ground_truth.get_pattern_count(piece)
                })

                for piece_future in piece_result_futures[piece]:
                    evaluation_result[piece].update(piece_future.result())

        return Evaluator.__results_to_pandas(evaluation_result)

    @staticmethod
    def __results_to_pandas(evaluation_result):
        """ Returns a pandas dataframe created from the dict of evaluation results """

        sorted_pieces = sorted(evaluation_result.keys())
        dict_dataframe = defaultdict(list)

        for piece in sorted_pieces:
            piece_dict = evaluation_result[piece]
            for key in piece_dict:
                dict_dataframe[key].append(piece_dict[key])

        df = pd.DataFrame.from_dict(dict_dataframe)
        df.loc['Mean'] = df.mean(numeric_only=True)

        return df

    @staticmethod
    def print_excluded_pieces(common_pieces, evaluated_data, ground_truth):
        excluded_gt_pieces = sorted(set(ground_truth).difference(common_pieces))
        excluded_evaluation_pieces = sorted(set(evaluated_data).difference(common_pieces))
        if excluded_gt_pieces:
            listing = '\n\t'.join(excluded_gt_pieces)
            print(f'Ground truth pieces not found in given dataset:\n\t{listing}')
        if excluded_evaluation_pieces:
            listing = '\n\t'.join(excluded_evaluation_pieces)
            print(f'Pieces in given dataset not found in ground truth:\n\t{listing}')


def dispatch_piece_result_computations(executor, gt_patterns, output_patterns):
    result_futures = [executor.submit(compute_establishment_scores, gt_patterns, output_patterns),
                      executor.submit(compute_three_layer_scores, gt_patterns, output_patterns),
                      executor.submit(compute_occurrence_scores, gt_patterns, output_patterns, 0.75),
                      executor.submit(compute_occurrence_scores, gt_patterns, output_patterns, 0.5)]

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


def compute_occurrence_scores(gt_patterns, output_patterns, threshold=0.75):
    occ_scores = {}
    occ_ind = mirex.occurrence_indices(gt_patterns, output_patterns, threshold=threshold)
    p_occ = mirex.occurrence_precision(gt_patterns, output_patterns, occ_ind)
    occ_scores[f'{Evaluator.OCC_PRECISION} (c={threshold})'] = p_occ
    r_occ = mirex.occurrence_recall(gt_patterns, output_patterns, occ_ind)
    occ_scores[f'{Evaluator.OCC_RECALL} (c={threshold})'] = r_occ
    occ_scores[f'{Evaluator.OCC_F_SCORE} (c={threshold})'] = mirex.f_score(p_occ, r_occ)

    return occ_scores
