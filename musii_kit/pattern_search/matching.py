import posemirpy.posemirpy as posemirpy
from musii_kit.point_set.point_set import Pattern2d, PointSet2d, PatternOccurrences2d


def find_occurrences(query: Pattern2d, point_set: PointSet2d) -> PatternOccurrences2d:
    """
    Returns all translationally equivalent occurrences of the query pattern from the
    given point-set.

    :param query: the query that is searched for
    :param point_set: the point-set from which occurrences of query are searched for
    :return: all translationally equivalent occurrences of the query pattern from the
    given point-set
    """
    raw_output = posemirpy.find_occurrences(query.as_numpy(), point_set.as_numpy())
    occurrences = []
    for array in raw_output:
        occurrences.append(Pattern2d.from_numpy(array, label="", source='GeometricMathing'))

    return PatternOccurrences2d(point_set.piece_name, query, occurrences)
