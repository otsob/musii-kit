import os

import music21 as m21
from music21.environment import UserSettingsException


def set_muse_score_visualizer(mscore_path='/Applications/MuseScore 3.app/Contents/MacOS/mscore'):
    """
    Sets the path for using MuseScore as a visualizer.

    :param mscore_path: the path to the MuseScore executable. Defaults to macOS path for MuseScore 3.
                        For Linux the path is typically: /usr/bin/mscore
                        For Windows the path is typically: r'C:\\Program Files (x86)\\MuseScore 3\\bin\\MuseScore.exe'
                        (with single backslashes)
    """
    us = m21.environment.UserSettings()
    try:
        us.create()
    except UserSettingsException:
        # If path already exists, an exception is raised. The exception is ignored.
        pass

    us['musescoreDirectPNGPath'] = mscore_path
    us['musicxmlPath'] = mscore_path


def visualize(notation):
    """ Visualizes the given music21 notation with the visualization backend that has been set. """
    notation.show('ipython.musicxml.png')
