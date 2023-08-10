import os
import tempfile
from pathlib import Path

from musii_kit.pattern_data.pattern_set import PatternSet
from musii_kit.point_set.point_set import PatternOccurrences2d, Pattern2d, Point2d


class TestPatternSet:

    @staticmethod
    def _assert_pattern_set_is_expected(pattern_set):
        assert 1 == len(pattern_set)
        piece_name = 'test-piece'
        assert 11 == pattern_set.get_composition_size(piece_name)
        assert 5 == pattern_set.get_pattern_count(piece_name)
        point_set = pattern_set[0][0]
        assert point_set.piece_name == piece_name
        patterns = pattern_set[0][1]
        assert 5 == len(patterns)

    def test_loading_pattern_set_from_csv(self):
        pattern_set_path = Path(os.path.dirname(os.path.realpath(__file__))) / 'resources/pattern_set_csv'
        pattern_set = PatternSet.from_path(pattern_set_path)
        self._assert_pattern_set_is_expected(pattern_set)

    def test_loading_pattern_set_from_musicxml(self):
        pattern_set_path = Path(os.path.dirname(os.path.realpath(__file__))) / 'resources/pattern_set_musicxml'
        pattern_set = PatternSet.from_path(pattern_set_path)
        self._assert_pattern_set_is_expected(pattern_set)

    def test_json_serialization_deserialization(self):
        pattern_set_path = Path(os.path.dirname(os.path.realpath(__file__))) / 'resources/pattern_set_csv'
        original = PatternSet.from_path(pattern_set_path)

        with tempfile.NamedTemporaryFile() as tmp:
            path = tmp.name
            PatternSet.write_to_json(original, path)
            read_pattern_set = PatternSet.read_from_json(path)
            self._assert_pattern_set_is_expected(read_pattern_set)

    def test_adding_patterns_to_set_by_piece_name(self):
        pattern_set_path = Path(os.path.dirname(os.path.realpath(__file__))) / 'resources/pattern_set_musicxml'
        pattern_set = PatternSet.from_path(pattern_set_path)

        piece_name = 'test-piece'
        pattern = Pattern2d([Point2d(1.0, 1.0), Point2d(2.0, 2.0)], 'A', 'source', piece_name)
        pattern_occs = PatternOccurrences2d(piece_name, pattern, [])

        pattern_set.add_patterns(pattern_occs)

        assert 1 == len(pattern_set)
        assert 11 == pattern_set.get_composition_size(piece_name)
        assert 6 == pattern_set.get_pattern_count(piece_name)
        point_set = pattern_set[0][0]
        assert point_set.piece_name == piece_name
        patterns = pattern_set[0][1]
        assert 6 == len(patterns)

    def test_adding_patterns_to_set_by_point_set_id(self):
        pattern_set_path = Path(os.path.dirname(os.path.realpath(__file__))) / 'resources/pattern_set_musicxml'
        pattern_set = PatternSet.from_path(pattern_set_path)

        piece_name = 'test-piece'
        pattern = Pattern2d([Point2d(1.0, 1.0), Point2d(2.0, 2.0)], 'A', 'source', piece_name)
        pattern_occs = PatternOccurrences2d(piece_name, pattern, [])

        pattern_set.add_patterns(pattern_occs, point_set_id=pattern_set[0][0].id)

        assert 1 == len(pattern_set)
        assert 11 == pattern_set.get_composition_size(piece_name)
        assert 6 == pattern_set.get_pattern_count(piece_name)
        point_set = pattern_set[0][0]
        assert point_set.piece_name == piece_name
        patterns = pattern_set[0][1]
        assert 6 == len(patterns)
