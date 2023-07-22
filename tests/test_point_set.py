import os
import tempfile
from pathlib import Path

import numpy as np

from musii_kit.point_set.point_set import Pattern2d, Point2d, PointSet2d
from musii_kit.point_set.point_set_io import read_musicxml, read_csv, write_point_set_to_json, read_point_set_from_json


class TestPointSet2d:
    test_path = Path(os.path.dirname(os.path.realpath(__file__)))
    test_points = [Point2d(1.0000001, 20.0), Point2d(1.0, 20.0), Point2d(0.0, 21.0), Point2d(2.0, 20.0),
                   Point2d(2.0, 21.0)]

    def test_given_float_points_then_correct_point_set_is_created(self):
        point_set = PointSet2d(self.test_points, piece_name='Test piece', dtype=float)

        assert 4 == len(point_set)
        assert Point2d(0.0, 21.0) == point_set[0]
        assert Point2d(1.0, 20.0) == point_set[1]
        assert Point2d(2.0, 20.0) == point_set[2]
        assert Point2d(2.0, 21.0) == point_set[3]

    def test_given_float_points_then_point_set_is_correctly_iterated(self):
        point_set = PointSet2d(self.test_points, piece_name='Test piece', dtype=float)

        i = 0
        for point in point_set:
            assert point == point_set[i]
            i += 1

        assert i == 4

    def test_given_int_points_then_correct_point_set_is_created(self):
        point_set = PointSet2d(self.test_points, piece_name='Test piece', dtype=int)

        assert 4 == len(point_set)
        assert Point2d(0.0, 21.0) == point_set[0]
        assert Point2d(1.0, 20.0) == point_set[1]
        assert Point2d(2.0, 20.0) == point_set[2]
        assert Point2d(2.0, 21.0) == point_set[3]

    def test_as_numpy(self):
        point_set = PointSet2d(self.test_points, piece_name='Test piece', dtype=float)

        assert np.array_equal(point_set.as_numpy(),
                              np.array([[0.0, 21.0, 0.0],
                                        [1.0, 20.0, 1.0000001],
                                        [2.0, 20.0, 2.0],
                                        [2.0, 21.0, 2.0]]))

    def test_given_point_sets_with_common_point_intersection_not_empty(self):
        point_set_a = PointSet2d(self.test_points, piece_name='Test piece', dtype=float)
        points_b = self.test_points[1:3]
        points_b.append(Point2d(30.0, 12.0))
        point_set_b = PointSet2d(points_b, piece_name='Test piece', dtype=float)

        intersection = point_set_a & point_set_b
        assert 2 == len(intersection)
        assert Point2d(0.0, 21.0) == intersection[0]
        assert Point2d(1.0, 20.0) == intersection[1]

    def test_given_range_within_point_set_then_point_are_returned(self):
        point_set = PointSet2d(self.test_points, piece_name='Test piece', dtype=float)
        points_in_range = point_set.get_range(1.0, 2.0)
        assert len(points_in_range) == 3
        assert Point2d(1.0, 20.0) == points_in_range[0]
        assert Point2d(2.0, 20.0) == points_in_range[1]
        assert Point2d(2.0, 21.0) == points_in_range[2]

    def test_given_time_scaling_factor_then_pattern_is_scaled(self):
        point_set = PointSet2d(self.test_points, piece_name='Test piece', dtype=float)
        expected = PointSet2d([Point2d(2.0, 20.0), Point2d(0.0, 21.0), Point2d(4.0, 20.0),
                               Point2d(4.0, 21.0)], piece_name='Test piece', dtype=float)

        scaled = point_set.time_scaled(2.0)
        assert expected.equals_in_points(scaled)
        assert expected.piece_name == scaled.piece_name
        assert expected.dtype == scaled.dtype

    def test_given_pattern_measure_range_is_correctly_retrieved(self):
        point_set = read_musicxml(self.test_path / 'resources/test-point-set.musicxml')
        pattern = Pattern2d([Point2d(2.0, 60),
                             Point2d(4.0, 72.0),
                             Point2d(4.33333333, 74.0),
                             Point2d(4.66666667, 76.0)], label='A', source='Manual query')

        measure_range = point_set.get_measure_range(pattern)
        assert measure_range[0] == 1
        assert measure_range[1] == 2

    def test_given_pattern_score_region_with_inclusion_is_correctly_retrieved(self):
        point_set = read_musicxml(self.test_path / 'resources/test-point-set.musicxml')
        pattern = Pattern2d([Point2d(2.0, 60),
                             Point2d(4.0, 72.0),
                             Point2d(4.33333333, 74.0),
                             Point2d(4.66666667, 76.0)], label='A', source='Manual query')

        region = point_set.get_score_region(pattern, boundaries='include')
        assert len(region.flatten().notes) == 8

    def test_given_pattern_score_region_with_truncation_is_correctly_retrieved(self):
        point_set = read_musicxml(self.test_path / 'resources/test-point-set.musicxml')
        pattern = Pattern2d([Point2d(2.0, 60),
                             Point2d(4.0, 72.0),
                             Point2d(4.33333333, 74.0),
                             Point2d(4.66666667, 76.0)], label='A', source='Manual query')

        region = point_set.get_score_region(pattern, boundaries='truncate')
        assert len(region.flatten().notes) == 8

    def test_given_pattern_score_region_with_exclusion_is_correctly_retrieved(self):
        point_set = read_musicxml(self.test_path / 'resources/test-point-set.musicxml')
        pattern = Pattern2d([Point2d(2.0, 60),
                             Point2d(4.0, 72.0),
                             Point2d(4.33333333, 74.0),
                             Point2d(4.66666667, 76.0)], label='A', source='Manual query')

        region = point_set.get_score_region(pattern, boundaries='exclude')
        assert len(region.flatten().notes) == 6


class TestPointPattern2d:
    test_points = [Point2d(1.0000001, 20.0), Point2d(1.0, 20.0), Point2d(0.0, 21.0)]

    def test_given_float_points_pattern_is_created(self):
        pattern = Pattern2d(self.test_points, 'A', 'Analyst', dtype=float)
        assert pattern.label == 'A'
        assert pattern.source == 'Analyst'
        assert pattern.dtype == float

    def test_given_dict_pattern_is_created(self):
        pattern_data = dict()
        pattern_data['label'] = 'Test pattern'
        pattern_data['source'] = 'Test analyst'
        pattern_data['dtype'] = 'int'
        pattern_data['data'] = np.array([[0.0, 21.0, 0.0],
                                         [1.0, 20.0, 1.0]]).tolist()
        pattern_data['pitch_type'] = 'chromatic'

        pattern = Pattern2d.from_dict(pattern_data)
        assert pattern.label == 'Test pattern'
        assert pattern.source == 'Test analyst'
        assert pattern.dtype == int
        assert 2 == len(pattern)
        assert pattern[0] == Point2d(0, 21)
        assert pattern[1] == Point2d(1, 20)

    def test_given_equal_patterns_equals_returns_true(self):
        pattern_a = Pattern2d(self.test_points, 'A', 'Analyst', dtype=float)
        pattern_b = Pattern2d([Point2d(1.0, 20.0), Point2d(1.00000001, 20.0), Point2d(0.0, 21.0)], 'B', 'Analyst',
                              dtype=float)

        assert pattern_a.equals_in_points(pattern_a)
        assert pattern_a.equals_in_points(pattern_b)

    def test_given_unequal_patterns_equals_returns_false(self):
        pattern_a = Pattern2d(self.test_points, 'A', 'Analyst', dtype=float)
        pattern_b = Pattern2d([Point2d(1.0000001, 20.0), Point2d(1.0, 21.0), Point2d(0.0, 21.0)], 'B', 'Analyst',
                              dtype=float)

        assert not pattern_a.equals_in_points(pattern_b)

    def test_given_time_scaling_factor_then_pattern_is_scaled(self):
        pattern = Pattern2d(self.test_points, 'A', 'Analyst', dtype=float)
        expected = Pattern2d([Point2d(2.0, 20.0), Point2d(0.0, 21.0)], 'A', 'Analyst', dtype=float)

        scaled = pattern.time_scaled(2.0)
        assert expected.equals_in_points(scaled)
        assert expected.label == scaled.label
        assert expected.source == scaled.source
        assert expected.dtype == scaled.dtype


class TestPoint2d:
    def test_given_equal_points_equals_is_true(self):
        a = Point2d(1.0, 54.0)
        b = Point2d(1.0, 54.0)

        assert a == a
        assert a == b
        assert b == a

        a = Point2d(1.00000000001, 54.0)
        b = Point2d(1.0, 54.0)

        assert a == a
        assert a == b
        assert b == a

    def test_given_inequal_points_equals_is_false(self):
        a = Point2d(1.0, 54.0)
        b = Point2d(1.0, 55.0)
        assert a != b
        assert b != a

        a = Point2d(1.0, 55.0)
        b = Point2d(1.125, 55.0)
        assert a != b
        assert b != a

    def test_given_equal_points_hashs_are_equal(self):
        a = Point2d(1.0, 54.0)
        b = Point2d(1.0, 54.0)

        assert hash(a) == hash(b)

        a = Point2d(1.00000000001, 54.0)
        b = Point2d(1.0, 54.0)
        assert hash(a) == hash(b)

    def test_given_equal_point_ordering_is_same(self):
        a = Point2d(1.0, 54.0)
        b = Point2d(1.0, 54.0)

        assert not a < a
        assert not a < b
        assert not a > b

        assert a <= a
        assert a <= b
        assert a >= b

    def test_given_inequal_point_ordering_is_not_same(self):
        a = Point2d(1.0, 54.0)
        b = Point2d(1.0, 55.0)
        assert a < b
        assert b > a

        a = Point2d(1.0, 55.0)
        b = Point2d(1.125, 55.0)
        assert a < b
        assert b > a


class TestPointSetIO:
    test_path = Path(os.path.dirname(os.path.realpath(__file__)))

    expected_chromatic = PointSet2d([
        Point2d(0.0, 60.0),
        Point2d(2.0, 60.0),

        Point2d(4.0, 59.0),
        Point2d(4.0, 72.0),
        Point2d(4.33333333, 74.0),
        Point2d(4.66666666, 76.0),

        Point2d(0.0, 60.0),
        Point2d(2.0, 62.0),
        Point2d(2.0, 55.0),

        Point2d(4.0, 48.0),
        Point2d(4.0, 52.0),
        Point2d(4.0, 55.0)],
        piece_name='Point-set test',
        quarter_length=1.0,
        measure_line_positions=[0.0, 4.0, 8.0])

    def test_read_chromatic_point_set_from_musicxml(self):
        point_set = read_musicxml(self.test_path / 'resources/test-point-set.musicxml')

        assert np.array_equal(self.expected_chromatic.as_numpy()[:, 0], point_set.as_numpy()[:, 0])
        assert np.array_equal(self.expected_chromatic.as_numpy()[:, 1], point_set.as_numpy()[:, 1])

        assert point_set.piece_name == self.expected_chromatic.piece_name
        assert point_set.measure_line_positions == self.expected_chromatic.measure_line_positions
        assert point_set.quarter_length == self.expected_chromatic.quarter_length
        assert 'chromatic' == point_set.pitch_type

    def test_read_chromatic_point_set_from_csv(self):
        point_set = read_csv(self.test_path / 'resources/test-point-set.csv', onset_column=0, pitch_column=1)

        assert np.array_equal(self.expected_chromatic.as_numpy()[:, 0], point_set.as_numpy()[:, 0])
        assert np.array_equal(self.expected_chromatic.as_numpy()[:, 1], point_set.as_numpy()[:, 1])

    expected_morphetic = PointSet2d([
        Point2d(0.0, 60.0),
        Point2d(2.0, 60.0),

        Point2d(4.0, 59.0),
        Point2d(4.0, 67.0),
        Point2d(4.33333333, 68.0),
        Point2d(4.66666666, 69.0),

        Point2d(0.0, 60.0),
        Point2d(2.0, 61.0),

        Point2d(2.0, 57.0),
        Point2d(4.0, 53.0),
        Point2d(4.0, 55.0),
        Point2d(4.0, 57.0)],
        piece_name='Point-set test',
        quarter_length=1.0,
        measure_line_positions=[0.0, 4.0, 8.0])

    def test_read_morphetic_point_set_from_musicxml(self):
        point_set = read_musicxml(self.test_path / 'resources/test-point-set.musicxml',
                                  pitch_extractor=PointSet2d.morphetic_pitch)

        assert np.array_equal(self.expected_morphetic.as_numpy()[:, 0], point_set.as_numpy()[:, 0])
        assert np.array_equal(self.expected_morphetic.as_numpy()[:, 1], point_set.as_numpy()[:, 1])

        assert point_set.piece_name == self.expected_morphetic.piece_name
        assert point_set.measure_line_positions == self.expected_morphetic.measure_line_positions
        assert point_set.quarter_length == self.expected_morphetic.quarter_length
        assert 'morphetic' == point_set.pitch_type

    def test_read_morphetic_point_set_from_csv(self):
        point_set = read_csv(self.test_path / 'resources/test-point-set.csv', onset_column=0, pitch_column=2)

        assert np.array_equal(self.expected_morphetic.as_numpy()[:, 0], point_set.as_numpy()[:, 0])
        assert np.array_equal(self.expected_morphetic.as_numpy()[:, 1], point_set.as_numpy()[:, 1])

    def test_json_serialization_deserialization(self):
        original = read_musicxml(self.test_path / 'resources/test-point-set.musicxml',
                                 pitch_extractor=PointSet2d.chromatic_pitch)

        with tempfile.NamedTemporaryFile() as tmp:
            path = tmp.name
            write_point_set_to_json(original, path)
            read_ps = read_point_set_from_json(path)

        assert original.piece_name == read_ps.piece_name
        assert original.quarter_length == read_ps.quarter_length
        assert original.measure_line_positions == read_ps.measure_line_positions
        assert original.pitch_type == read_ps.pitch_type
        assert np.allclose(original.as_numpy(), read_ps.as_numpy())
