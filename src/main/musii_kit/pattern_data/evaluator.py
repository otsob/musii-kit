import musii_kit.pattern_data.mirex_metrics as mirex
from musii_kit.pattern_data.pattern_set import PatternSet


class Evaluator:
    """ Computes evaluation metrics for a pattern set against a ground truth pattern set.

    The datasets are expected to consist of triples following the convention used in
    the JkuPdd and PatternSet classes in this module.
     """

    EST_RECALL = 'establishment_recall'
    EST_PRECISION = 'establishment_precision'
    EST_F_ONE = 'establishment_F1'

    def __init__(self, ground_truth: PatternSet):
        """
        Creates a new evaluator.

        :param ground_truth: the ground truth against which the evaluator computes the metrics
        """
        self._ground_truth = ground_truth

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

        evaluation_result = {}

        for piece in common_pieces:
            gt_patterns = ground_truth[piece][1]
            output_patterns = evaluated_data[piece][1]

            piece_result = {}
            est_matrix = mirex.establishment_matrix(gt_patterns, output_patterns)
            r_est = mirex.establishment_recall(est_matrix)
            piece_result[Evaluator.EST_RECALL] = r_est
            p_est = mirex.establishment_precision(est_matrix)
            piece_result[Evaluator.EST_PRECISION] = p_est
            piece_result[Evaluator.EST_F_ONE] = mirex.basic_f1(p_est, r_est)

            evaluation_result[piece] = piece_result

        return evaluation_result
