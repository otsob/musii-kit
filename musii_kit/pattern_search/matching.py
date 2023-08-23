import posemirpy.posemirpy as posemirpy

from musii_kit.point_set.point_set import Pattern2d, PointSet2d, PatternOccurrences2d


def find_occurrences(query: Pattern2d, point_set: PointSet2d, min_match_size: int = None) -> PatternOccurrences2d:
    """
    Returns all translationally equivalent occurrences of the query pattern from the
    given point-set. The returned pattern occurrences contains the query as the pattern
    and the found matches as the occurrences.

    Only exact translated matches are returned unless the `min_match_size` threshold is given.
    The `min_match_size` threshold is the minimum number of points that must match in partial matching
    for a match to be returned.

    :param query: the query that is searched for
    :param point_set: the point-set from which occurrences of query are searched for
    :param min_match_size: the minimum number of points that must match in partial matching
    :return: all translationally equivalent occurrences of the query pattern from the
    given point-set
    """
    if len(query) > len(point_set):
        raise ValueError("Query cannot be longer than the point_set")

    if not min_match_size:
        min_match_size = -1

    raw_output = posemirpy.find_occurrences(query.as_numpy(), point_set.as_numpy(), min_match_size)
    occurrences = []
    for array in raw_output:
        occurrences.append(Pattern2d.from_numpy(array, label="", source='GeometricMathing'))

    return PatternOccurrences2d(point_set.piece_name, query, occurrences)
