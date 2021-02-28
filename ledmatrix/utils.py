def _clean_hex(hex_str):
    """
    Returns 6-character hex without '0x' or '#' (or None if invalid)
    """
    try:
        if hex_str[:2] == '0x':
            hex_str = hex_str[2:]
        elif hex_str[0] == '#':
            hex_str = hex_str[1:]
        if len(hex_str) != 6:
            return None
        
        for char in hex_str:
            if char.lower() not in '0123456789abcdef':
                return None
        return hex_str
    except:
        return None
    

def _hex2rgb(color):
    """
    Checks rgb input, and if it's hex code, converts it to tuple (R, G, B)
    """
    default_color = 0, 0, 0
    
    if type(color) == tuple and len(color) == 3:
        return color
    elif type(color) == str:
        color = _clean_hex(color)
        if color is None:
            return default_color
        
        r = int(color[:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:], 16)
        return r, g, b
    else:
        return default_color