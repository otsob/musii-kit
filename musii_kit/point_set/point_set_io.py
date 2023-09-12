import json
from typing import List

import music21 as m21
import numpy as np

from musii_kit.point_set.point_set import PointSet2d, PatternOccurrences2d


def read_point_set_from_json(input_path) -> PointSet2d:
    """
    Reads a point-set from a JSON file.
    :param input_path: the path to the JSON file containing a point-set.
    :return: a point-set with contents from the input JSON
    """
    with open(input_path, 'r') as input_file:
        return PointSet2d.from_dict(json.loads(input_file.read()))


def write_point_set_to_json(point_set: PointSet2d, output_path):
    """
    Writes the given point-set to a JSON file in the specified path.

    :param point_set: the point-set to write to JSON
    :param output_path: the path to which the JSON output is written
    """
    with open(output_path, 'w') as outfile:
        json.dump(point_set.to_dict(), outfile, indent=2)


def write_patterns_to_json(pattern_occurrences: PatternOccurrences2d, output_path):
    """
    Writes the given pattern occurrences to JSON.

    :param pattern_occurrences: the pattern occurrences that are written to JSON
    :param output_path: the path to which the JSON file is written
    """
    with open(output_path, 'w') as outfile:
        json.dump(pattern_occurrences.to_dict(), outfile, indent=2)


def read_patterns_from_json(input_path) -> List[PatternOccurrences2d]:
    """
    Read pattern occurrences from the given input path.

    :param input_path: the path of the JSON file from which the pattern occurrences are read
    :return: the pattern occurrences
    """
    with open(input_path, 'r') as input_file:
        json_content = json.loads(input_file.read())
        if isinstance(json_content, list):
            return [PatternOccurrences2d.from_dict(elem) for elem in json_content]
        else:
            return [PatternOccurrences2d.from_dict(json_content)]


def save_to_csv(point_set: PointSet2d, path, decimal_places=2):
    """
     Saves the point set array to a CSV file

    :param point_set: the point set to save
    :param path: the path to which the csv file is saved
    :param decimal_places: how many decimal places are used for the values
    """
    np.savetxt(path, point_set.as_numpy(), delimiter=', ', fmt=f'%.{decimal_places}f', header="x, y")


def read_csv(path, onset_column=0, pitch_column=1, skip_header=0, delimiter=',') -> PointSet2d:
    """
    Reads a point set from a csv file.

    :param path: path to csv file with two columns
    :param onset_column: index of column used for onset values
    :param pitch_column: index of column used for pitch value
    :param skip_header: skip_header paramater for numpy
    :param delimiter: delimiter param for numpy
    :return: a point set with the contents of the csv file
    """
    array = np.genfromtxt(path, delimiter=delimiter, skip_header=skip_header)
    return PointSet2d.from_numpy(np.column_stack((array[:, onset_column], array[:, pitch_column])))


def read_musicxml(path, pitch_extractor=PointSet2d.chromatic_pitch, expand_repetitions=False,
                  include_grace_notes=False) -> PointSet2d:
    """
    Reads a point set from a MusicXML file.

    :param path: path to MusicXML file
    :param pitch_extractor: the function used to map a music21 pitch to a number
    :param expand_repetitions: flag that sets whether repeated sections in the score are repeated in the point-set
    :param include_grace_notes: set to true to include grace notes in the point-set, by default they are ignored
    :return: a point set with the contents of the MusicXML file
    """
    return PointSet2d.from_score(m21.converter.parse(path), pitch_extractor, expand_repetitions, include_grace_notes)
