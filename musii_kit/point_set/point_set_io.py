import json
from typing import List

import music21 as m21
import numpy as np

from musii_kit.point_set.point_set import PointSet2d, PatternOccurrences2d, Point2d


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


def read_csv(path) -> PointSet2d:
    """
    Reads a point set from a csv file.

    :param path: path to csv file with two columns
    :return: a point set with the contents of the csv file
    """
    return PointSet2d.from_numpy(np.genfromtxt(path, delimiter=','))


def read_musicxml(path) -> PointSet2d:
    """
    Reads a point set from a MusicXML file.

    :param path: path to MusicXML file
    :return: a point set with the contents of the MusicXML file
    """
    measure_line_positions = []
    first_staff = True
    points = []

    score = m21.converter.parse(path)

    for staff in score.parts:

        measure_offset = 0.0

        for measure in filter(lambda m: isinstance(m, m21.stream.base.Measure), staff):
            for elem in measure:
                _read_elem_to_points(elem, measure_offset, points)

                if isinstance(elem, m21.stream.Voice):
                    for e in elem:
                        _read_elem_to_points(e, measure_offset, points)

            if first_staff:
                measure_line_positions.append(measure_offset)

            measure_offset += measure.quarterLength

        if first_staff:
            measure_line_positions.append(measure_offset)

        first_staff = False

    return PointSet2d(points, _extract_piece_name(score), dtype=float, quarter_length=1.0,
                      measure_line_positions=measure_line_positions)


def _extract_piece_name(score):
    piece_name = None
    name_elem = next(filter(lambda e: hasattr(e, 'movementName'), score.elements))
    if name_elem:
        piece_name = name_elem.movementName
    return piece_name


def _read_elem_to_points(elem, measure_offset, points):
    if isinstance(elem, m21.note.Note):
        points.append(Point2d(measure_offset + elem.offset, elem.pitch.ps))
    if isinstance(elem, m21.chord.Chord) and not isinstance(elem, m21.harmony.ChordSymbol):
        for note in elem:
            if isinstance(note, m21.note.Note):
                points.append(Point2d(measure_offset + elem.offset, note.pitch.ps))
