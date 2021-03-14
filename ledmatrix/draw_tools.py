from bdflib import reader
import os
import random

from .utils import _hex2rgb

_DEFAULT_FONT = 'fonts/4x6.bdf'
_FONTS_PATH = os.path.split(os.path.abspath(__file__))[0]
_DEFAULT_FONT_PATH = os.path.join(_FONTS_PATH, _DEFAULT_FONT)
_LOADED_FONTS = []

def draw_dot(vmatrix, row, col, rgb):
    """
    Sets the color of one pixel in the virtual matrix
    """
    rgb = _hex2rgb(rgb)
    if 0 <= row < vmatrix.num_rows and 0 <= col < vmatrix.num_cols:
        vmatrix.pixel(row, col).setrgb(rgb)
        

def draw_line(vmatrix, row0=None, col0=None, row1=None, col1=None, rgb=(0, 0, 0)):
    """
    Draws a line between two pixels in the virtual matrix
    (only straight horizontal/vertical, at least for now)
    """
    rgb = _hex2rgb(rgb)
    if None in [row0, col0, row1, col1]:
        return
    
    if row0 == row1:
        for col in range(max(col0, 0), min(col1 + 1, vmatrix.num_cols)):
            vmatrix.pixel(row0, col).setrgb(rgb)
    
    elif col0 == col1:
        for row in range(max(row0, 0), min(row1 + 1, vmatrix.num_rows)):
            vmatrix.pixel(row, col0).setrgb(rgb)
            
            
def draw_box(vmatrix, row0=None, col0=None, row1=None, col1=None, rgb=(0, 0, 0)):

    """
    Draws a shaded box in the virtual matrix between two
    kitty-corner pixels
    """
    rgb = _hex2rgb(rgb)
    if None in [row0, col0, row1, col1]:
        return
    
    rowA = max(min(row0, row1), 0)
    rowB = min(max(row0, row1), vmatrix.num_rows)
    colA = max(min(col0, col1), 0)
    colB = min(max(col0, col1), vmatrix.num_cols)
    
    for row in range(rowA, rowB + 1):
        for col in range(colA, colB + 1):
            vmatrix.pixel(row, col).setrgb(rgb)
            
            
def draw_diamond(vmatrix, row0=None, col0=None, width=0, rgb=(0, 0, 0)):
    """
    Draws a diamond with center point row0, col0
    (width must be an odd integer, at least for now)
    """
    if None in [row0, col0]:
        return
    if width % 2 != 1:
        return
    
    radius = int((width - 1) / 2)
    for row in range(row0 - radius, row0 + radius + 1):
        for col in range(col0 - radius, col0 + radius + 1):
            offset = abs(row - row0) + abs(col - col0)
            if (offset <= radius
                and row <= vmatrix.num_rows and col <= vmatrix.num_cols):
                vmatrix.pixel(row, col).setrgb(rgb)


class draw_text:
    """
    Draws text in the virtual matrix using a BDF font
    This is a class rather than a function so that its attributes (such as text_width) can
    be referenced when drawing other shapes.
    """
    def __init__(self, vmatrix, row0, col0, text_string, font=_DEFAULT_FONT_PATH,
                 rgb=(255, 255, 255), align='left', spacing=1, background=None):
        self.row0 = row0
        self.col0 = col0
        self.text_string = text_string
        self.align = align
        
        self.rgb = _hex2rgb(rgb)
        if background is None:
            self.background = None
        else:
            self.background = _hex2rgb(background)
        
        bdf_font = _load_font(font, spacing)
        string_glyphs = [bdf_font['font_obj'][ord(c)] for c in text_string]
        
        # Calculate text width and offset col for center/right align
        self.text_width = (sum([g.bbW for g in string_glyphs]) +
                           spacing * (len(string_glyphs) - 1))
        if self.align == 'center':
            self.left_col = self.col0 - int(round(self.text_width / 2.0))
        elif self.align == 'right':
            self.left_col = self.col0 - self.text_width + 1
        else:
            self.left_col = self.col0
            
        cursor_col = self.left_col
            
        # Draw each glyph
        for glyph in string_glyphs:
            
            # Start at origin, adjusting for bounding box offsets
            glyph_row0 = self.row0 - glyph.bbY
            glyph_col0 = cursor_col + glyph.bbX
            
            # Iterate through rows bottom to top
            for i in range(glyph.bbH):
                pips = format(glyph.data[i], '0{}b'.format(glyph.bbW))
                for j in range(glyph.bbW):
                    if pips[j] == '1':
                        draw_dot(vmatrix, glyph_row0 - i, glyph_col0 + j, self.rgb)
                    
                    # Background color, if given
                    elif self.background is not None:
                        draw_dot(vmatrix, glyph_row0 - i, glyph_col0 + j, self.background)
                        
            # Move cursor to next character
            cursor_col += glyph.bbW + bdf_font['spacing']
        
        
def _load_font(font_path=_DEFAULT_FONT_PATH, spacing=0):
    """
    Returns font from LOADED_FONTS by name; if not loaded, loads it from file
    """
    global _LOADED_FONTS
    match_font = [font for font in _LOADED_FONTS if font['font_path'] == font_path]
    if match_font:
        return match_font[0]
    else:
        try:
            with open(font_path, 'rb') as handle:
                bdf_font = reader.read_bdf(handle)
                
            new_font = {
                'font_path': font_path,
                'font_obj': bdf_font,
                'spacing': spacing
            }
            _LOADED_FONTS.append(new_font)
            return new_font
        except:
            print('Font {} failed to load.'.format(font_path))
            if _LOADED_FONTS:
                return _LOADED_FONTS[0]
            else:
                return None