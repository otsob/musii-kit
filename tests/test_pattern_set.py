import os
from pathlib import Path

from musii_kit.pattern_data.pattern_set import PatternSet


class TestPatternSet:

    def test_loading_pattern_set_from_csv(self):
        pattern_set_path = Path(os.path.dirname(os.path.realpath(__file__))) / 'resources/pattern_set_csv'
        pattern_set = PatternSet(pattern_set_path)
        assert 1 == len(pattern_set)

        piece_name = 'test-piece'
        assert 11 == pattern_set.get_composition_size(piece_name)
        assert 5 == pattern_set.get_pattern_count(piece_name)

        point_set = pattern_set[0][0]
        assert point_set.piece_name == piece_name

        patterns = pattern_set[0][1]
        assert 5 == len(patterns)
