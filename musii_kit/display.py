import tempfile
from copy import deepcopy

import music21 as m21
import verovio
from cairosvg import svg2pdf, svg2png
from pypdf import PdfMerger


def default_verovio_options():
    return {
        'breaks': 'encoded',
        'scale': 40,
        'condenseFirstPage': True,
        'adjustPageHeight': True,
        'adjustPageWidth': False,
        'header': 'auto',
        'footer': 'none',
        'condense': 'encoded',
        'svgCss': 'svg { background: white; }',
    }


class Notation:
    """A displayable type for notation. Can be displayed using IPython's display function.

    :param notation: the notation for which SVG is created
    :param verovio_options: options passed to verovio for rendering
    :param title: title to use in the visualization if not visualizing a full score"""

    def __init__(self, notation: m21.stream.Stream, verovio_options=default_verovio_options(), title=None):
        self.__svg_strings = self.__create_svg_pages(notation, verovio_options, title)

    @staticmethod
    def __clean_up_credits(notation, title):
        """Removes the text boxes for credits from the music21 stream if present.

        This is needed because the presence of the TextBox credits will lead to no
        title being rendered in the notation with verovio.
        """

        notation = deepcopy(notation)

        if title and hasattr(notation, 'metadata') and notation.metadata:
            if not notation.metadata:
                notation.metadata = m21.metadata.Metadata()

            notation.metadata.movementName = title

        text_boxes = notation.getElementsByClass('TextBox')

        if not text_boxes:
            return notation

        while text_boxes := notation.getElementsByClass('TextBox'):
            i = notation.index(text_boxes[0])
            notation.pop(i)

        return notation

    def __create_svg_pages(self, notation, options, title):
        tk = verovio.toolkit()

        with tempfile.NamedTemporaryFile(suffix='.musicxml') as tmp:
            name = tmp.name
            cleaned_up_notation = Notation.__clean_up_credits(notation, title)
            cleaned_up_notation.write('musicxml', fp=name)
            tk.loadFile(name)

        tk.setOptions(options)
        tk.redoLayout()

        # Workaround to fix an issue in cairosvg https://github.com/Kozea/CairoSVG/issues/300
        svg_strings = [
            tk.renderToSVG(i).replace('overflow="inherit"', 'overflow="visible"')
            for i in range(1, tk.getPageCount() + 1)
        ]

        return svg_strings

    def _repr_html_(self):
        return f'<div style="white-space: nowrap">{"".join(self.__svg_strings)}</div>'

    def to_pdf(self, file_path):
        """ Writes the notation visualization to a pdf file.

        All pages are written to a single file.

        :param file_path: path for the pdf file.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            pdf_page_files = []

            for i, svg_string in enumerate(self.__svg_strings):
                pdf_path = f'{tmp_dir}/{i}.pdf'
                pdf_page_files.append(pdf_path)
                svg2pdf(bytestring=svg_string, write_to=pdf_path)

            merger = PdfMerger()

            for pdf in pdf_page_files:
                merger.append(pdf)

            merger.write(file_path)
            merger.close()

    def to_png(self, file_path):
        """ Writes the notation visualization to a png file.

        If the notation takes multiple pages, writes multiple numbered png files.

        :param file_path: path for the png file(s)
        """

        if len(self.__svg_strings) == 1:
            svg_string = self.__svg_strings[0].replace("overflow=\"inherit\"", "overflow=\"visible\"")
            svg2png(bytestring=svg_string, dpi=300, scale=2.0, background_color='white',
                    write_to=file_path)

        for i, svg_string in enumerate(self.__svg_strings):
            svg_string = svg_string.replace("overflow=\"inherit\"", "overflow=\"visible\"")
            svg2png(bytestring=svg_string, dpi=300, scale=2.0, background_color='white',
                    write_to=f'{file_path[0:-4]}_{i + 1}.png')
