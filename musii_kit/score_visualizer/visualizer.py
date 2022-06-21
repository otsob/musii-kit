import music21 as m21
from music21.environment import UserSettingsException
import os


def set_muse_score_visualizer(mscore_path=os.getenv('MUSE_SCORE_PATH')):
    """
    Sets the path for using MuseScore as a visualizer.

    :param mscore_path: the path to the MuseScore executable.
                        Defaults to the value of the environment variable MUSE_SCORE_PATH.
                        For macOS typically: '/Applications/MuseScore 3.app/Contents/MacOS/mscore'
                        For Linux the path is typically: /usr/bin/mscore
                        For Windows the path is typically: r'C:\\Program Files (x86)\\MuseScore 3\\bin\\MuseScore.exe'
                        (with single backslashes)
    """
    us = __get_m21_user_settings()
    us['musescoreDirectPNGPath'] = mscore_path
    us['musicxmlPath'] = mscore_path


def __get_m21_user_settings():
    us = m21.environment.UserSettings()
    try:
        us.create()
    except UserSettingsException:
        # If path already exists, an exception is raised. The exception is ignored.
        pass
    return us


def set_lilypond_visualizer(lilypond_path=os.getenv('LILYPOND_PATH')):
    """
    Sets the path for using LilyPond as a visualizer.

    :param lilypond_path: the path to the LilyPond executable.
                            Defaults to the value of the environment variable LILYPOND_PATH.
    """
    us = __get_m21_user_settings()
    us['lilypondPath'] = lilypond_path
    us['musicxmlPath'] = lilypond_path


def visualize(notation):
    """ Visualizes the given music21 notation with the visualization backend that has been set. """
    notation.show('ipython.musicxml.png')
