from bdflib import reader

from .utils import _hex2rgb

_DEFAULT_FONT = 'fonts/4x6.bdf'
_LOADED_FONTS = []

def draw_dot(vmatrix, row, col, rgb):
    """
    Sets the color of one pixel in the virtual matrix
    """
    rgb = _hex2rgb(rgb)
    if 0 <= row < vmatrix.num_rows and 0 <= col < vmatrix.num_cols:
        vmatrix.pixel(row, col).setrgb(*rgb)
        

def draw_line(vmatrix, addr0, addr1, rgb):
    """
    Draws a line between two pixels in the virtual matrix
    (only straight horizontal/vertical, at least for now)
    """
    rgb = _hex2rgb(rgb)
    row0, col0 = addr0
    row1, col1 = addr1
    
    if row0 == row1:
        for col in range(max(col0, 0), min(col1 + 1, vmatrix.num_cols)):
            vmatrix.pixel(row0, col).setrgb(*rgb)
    
    elif col0 == col1:
        for row in range(max(row0, 0), min(row1 + 1, vmatrix.num_rows)):
            vmatrix.pixel(row, col0).setrgb(*rgb)
            
            
def draw_box(vmatrix, addr0, addr1, rgb):
    """
    Draws a shaded box in the virtual matrix between two
    kitty-corner pixels
    """
    rgb = _hex2rgb(rgb)
    row0, col0 = addr0
    row1, col1 = addr1
    
    rowA = max(min(row0, row1), 0)
    rowB = min(max(row0, row1), vmatrix.num_rows)
    colA = max(min(col0, col1), 0)
    colB = min(max(col0, col1), vmatrix.num_cols)
    
    for row in range(rowA, rowB + 1):
        for col in range(colA, colB + 1):
            vmatrix.pixel(row, col).setrgb(*rgb)


def draw_text(vmatrix, row0, col0, text_string, font=_DEFAULT_FONT,
              rgb=(255, 255, 255), align='left', spacing=0):
    """
    Draws text in the virtual matrix using a BDF font
    """
    rgb = _hex2rgb(rgb)
    
    bdf_font = _load_font(font, spacing)
    string_glyphs = [bdf_font['font_obj'][ord(c)] for c in text_string]
    
    # Calculate text width and offset col for center/right align
    text_width = (sum([g.bbW for g in string_glyphs]) +
                  spacing * (len(string_glyphs) - 1))
    if align == 'center':
        col0 -= int(round(text_width / 2.0))
    elif align == 'right':
        col0 -= text_width - 1
        
    for glyph in string_glyphs:
        
        # Start at origin, adjusting for bounding box offsets
        glyph_row0 = row0 - glyph.bbY
        glyph_col0 = col0 + glyph.bbX
        
        # Iterate through rows bottom to top
        for i in range(glyph.bbH):
            pips = format(glyph.data[i], '0{}b'.format(glyph.bbW))
            for j in range(glyph.bbW):
                if pips[j] == '1':
                    pip_row = glyph_row0 - i
                    pip_col = glyph_col0 + j
                    draw_dot(vmatrix, pip_row, pip_col, rgb)
                    
        # Move col0 to next character
        col0 += glyph.bbW + bdf_font['spacing']
        
        
def _load_font(font_path=_DEFAULT_FONT, spacing=0):
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