import os
import tempfile
from copy import deepcopy

import music21 as m21
import verovio
from IPython.display import SVG, display
from cairosvg import svg2pdf, svg2png
from music21.environment import UserSettingsException

# The visualizer is set by modifying music21 global settings, therefore
# this unfortunately is implemented as modification of global state.
VISUALIZER = ''


def set_muse_score_visualizer(mscore_path=os.getenv('MUSE_SCORE_PATH')):
    """
    Sets MuseScore globally as the visualizer for music notation.

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

    global VISUALIZER
    VISUALIZER = 'musescore'


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
    Sets Lilypond globally as the visualizer for music notation.
    It is preferred to use the MuseScore visualizer as it produces better results.

    :param lilypond_path: the path to the LilyPond executable.
                            Defaults to the value of the environment variable LILYPOND_PATH.
    """
    us = __get_m21_user_settings()
    us['lilypondPath'] = lilypond_path
    us['lilypondFormat'] = 'png'

    global VISUALIZER
    VISUALIZER = 'lilypond'


def default_verovio_options():
    return {'breaks': 'encoded',
            'scale': 40,
            'condenseFirstPage': True,
            'adjustPageHeight': True,
            'adjustPageWidth': False,
            'header': 'auto',
            'footer': 'none',
            'condense': 'encoded'}


VEROVIO_OPTIONS = default_verovio_options()


def set_verovio_visualizer(options=default_verovio_options()):
    """
    Sets verovio as the visualizer to use.

    Verovio is the default option as it does not require having additional
    software installed

    :param options: the options passed to the verovio renderer
    """
    global VEROVIO_OPTIONS
    VEROVIO_OPTIONS = options

    global VISUALIZER
    VISUALIZER = 'verovio'


def __clean_up_credits(notation):
    """ Removes the text boxes for credits from the music21 stream if present.

    This is needed because the presence of the TextBox credits will lead to no
    title being rendered in the notation with verovio.
    """
    text_boxes = notation.getElementsByClass('TextBox')

    if not text_boxes:
        return notation

    notation = deepcopy(notation)

    while text_boxes := notation.getElementsByClass('TextBox'):
        i = notation.index(text_boxes[0])
        notation.pop(i)

    return notation


def __visualize_with_verovio(notation, options, file_path, show_notebook_output):
    with tempfile.NamedTemporaryFile(suffix='.musicxml') as tmp:
        name = tmp.name
        cleaned_up_notation = __clean_up_credits(notation)

        cleaned_up_notation.write('musicxml', fp=name)

        tk = verovio.toolkit()
        tk.loadFile(name)
        tk.setOptions(options)
        tk.redoLayout()
        page_count = tk.getPageCount()

        for i in range(1, page_count + 1):
            svg_string = tk.renderToSVG(i)

            if file_path:
                # Workaround to fix an issue in cairosvg https://github.com/Kozea/CairoSVG/issues/300
                svg_string = svg_string.replace("overflow=\"inherit\"", "overflow=\"visible\"")
                if file_path.endswith('.png'):
                    svg2png(bytestring=svg_string, dpi=300, scale=2.0, background_color='white',
                            write_to=f'{file_path[0:-4]}_{i}.png')
                elif file_path.endswith('.pdf'):
                    svg2pdf(bytestring=svg_string, write_to=f'{file_path[0:-4]}_{i}.pdf')
                else:
                    print('Unsupported file type for saving music notation visualization to file'
                          '(needs to be .png .pdf)')

            if show_notebook_output:
                display(SVG(svg_string))


def visualize(notation, file_path=None, show_notebook_output=True):
    """
    Visualizes the given music21 notation with the visualization backend that has been set.
    Uses verovio by default. For other visualizers they need to have been set with either
    `set_muse_score_visualizer` or `set_lilypond_visualizer`.

    Writing to file is only supported with verovio visualizer and each page is written to a separate file.

    :param notation: a music21 notation type that supports visualization
    :param file_path: optional file path where to save the music notation as png or pdf depending on the suffix
    :param show_notebook_output: set to true to hide the notation in the cell output. Can be used to only
     save the visualizations to file without showing them in a notebook. """
    global VISUALIZER
    if VISUALIZER == 'musescore':
        notation.show('ipython.musicxml.png')
    elif VISUALIZER == 'lilypond':
        notation.show('ipython.lily.png')
    else:
        global VEROVIO_OPTIONS
        __visualize_with_verovio(notation, VEROVIO_OPTIONS, file_path, show_notebook_output)
