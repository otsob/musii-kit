import random
import numpy as np

from point_set.point_set import PointSet


def create_point_set_of_random_patterns(n, min_pattern_size, max_pattern_size, max_reps, dimensionality=2,
                                        value_range=(0, 100000)):
    """
    Returns a point set of random translated patterns as a numpy array.
    The patterns are randomly generated and repeated a random number of times as translated copies.
    All points in the produces point set are distinct. The components are of floating point types, but only
    have integral values.
    The returned array contains the point coordinates as rows.

    :param n: the size of the point set
    :param min_pattern_size: minimum size of a randomly generated patterns
    :param max_pattern_size: maximum size of a randomly generated patterns
    :param max_reps: maximum number of translated repetitions of the pattern
    :param dimensionality: the dimensionality of the point set
    :param value_range: the allowed range for the point coordinates
    :return: a point set of random translated patterns
    """

    point_set = np.zeros((n, dimensionality), dtype=float)
    index = 0

    while index < n:
        pattern_size = random.randint(min_pattern_size, max_pattern_size)
        if pattern_size + index >= n:
            pattern_size = n - index

        pattern = np.random.randint(value_range[0], value_range[1], (pattern_size, dimensionality))
        repetitions = random.randint(1, max_reps)

        point_set[index:index+pattern_size] = pattern

        for _ in range(0, repetitions):
            index += pattern_size
            if index + pattern_size >= n:
                break

            components = np.random.randint(value_range[0], value_range[1], (1, dimensionality))
            translation = np.column_stack((np.repeat(components[0, 0], pattern_size), (np.repeat(components[0, 1], pattern_size))))
            point_set[index:index + pattern_size] = pattern + translation

    return PointSet(replace_duplicates(point_set, value_range))


def replace_duplicates(point_set, value_range):
    unique_points = np.unique(point_set, axis=0)
    if unique_points.size == point_set.size:
        return unique_points

    dim = point_set.size[1]
    while unique_points.size != point_set.size:
        missing_row_count = point_set.shape[0] - unique_points.shape[0]
        without_duplicates = np.stack(unique_points, np.random.randint(value_range[0], value_range[1], (missing_row_count, dim)))
        unique_points = np.unique(without_duplicates)

    return without_duplicates


def create_point_set_on_line(n, dimensionality=2):
    """
    Creates a point set where only one dimension is incremented, i.e., the
    points are placed equidistantly on a single line.

    The returned array contains the point coordinates as rows.

    :param n: the size of the point set
    :param dimensionality: the dimensionality of the point set
    :return: a point set on a line
    """

    point_set = np.zeros((n, dimensionality), dtype=float)
    point_set[:, 0] = np.arange(0, n, 1.0, dtype=float)
    return PointSet(point_set)


def create_point_set_with_no_repeated_patterns(n, dimensionality=2):
    """
    Returns a point set where there are no translatable patterns with size greater than 1.
    All difference vectors between any pair of points in the point set are distinct.
    The returned array contains the point coordinates as rows.

    :param n: the size of the point set
    :param dimensionality: the dimensionality of the point set
    :return: a point set where there are no translatable patterns with size greater than 1
    """

    point_set = np.zeros((n, dimensionality), dtype=float)

    y_incr = 0.01
    y = 0
    for x in range(0, n):
        y += x * y_incr
        point_set[x, 0] = x
        point_set[x, 1] = y

    return PointSet(point_set)

