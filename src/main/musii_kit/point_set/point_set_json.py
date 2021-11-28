import json

from point_set import PatternOccurrences


def write_patterns_to_json(pattern_occurrences: PatternOccurrences, output_path):
    """
    Writes the given pattern occurrences to JSON.

    :param pattern_occurrences: the pattern occurrences that are written to JSON
    :param output_path: the path to which the JSON file is written
    """
    with open(output_path, 'w') as outfile:
        json.dump(pattern_occurrences.to_dict(), outfile, indent=2)


def read_patterns_from_json(input_path) -> PatternOccurrences:
    """
    Read pattern occurrences from the given input path.

    :param input_path: the path of the JSON file from which the pattern occurrences are read
    :return: the pattern occurrences
    """
    with open(input_path, 'r') as input_file:
        return PatternOccurrences.from_dict(json.loads(json.load(input_file)))
