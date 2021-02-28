from .utils import _hex2rgb

class vmatrix:
    """
    Defines 'virtual matrix' object containing a structured list of pixels and
    the colors to be set for each
    """
    
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.dimensions = (num_rows, num_cols)
        self.pixels = [_pixel(idx, num_rows, num_cols) for idx in range(num_rows * num_cols)]
        
    def pixel(self, row, col):
        """
        Returns a pixel in vmatrix by address; row 0 is top, col 0 is left
        """
        if row < 0 or row >= self.num_rows:
            return None
        if col < 0 or col >= self.num_cols:
            return None
        return self.pixels[row * self.num_cols + col]
    
    def set_pixels(self, pixel_list):
        """
        Sets pixels based on the indices and colors of the pixels in inputted list
        """
        for px in pixel_list:
            try:
                self.pixels[px.idx].setrgb(*px.rgb())
            except:
                pass
    
    def compare_to_cache(self, vm_cache):
        """
        Compares vmatrix to cached vmatrix and returns list of changed pixels
        """
        if self.dimensions != vm_cache.dimensions:
            return None
        
        changed_pixels = []
        for new_pixel in self.pixels:
            old_pixel = vm_cache.pixels[new_pixel.idx]
            if new_pixel.rgb() != old_pixel.rgb():
                changed_pixels.append(new_pixel)
                
        return changed_pixels
    
    def clear(self):
        """
        Clears all pixels in vmatrix (sets to black)
        """
        for pixel in self.pixels:
            pixel.setrgb(0, 0, 0)
            
    def print_matrix(self):
        """
        Prints matrix in the command line ('-' = black, '#' = other)
        """
        for row in range(self.num_rows):
            print_row = ''
            for col in range(self.num_cols):
                print_pixel = self.pixel(row, col)
                if print_pixel.rgb() == (0, 0, 0):
                    print_row += '-'
                else:
                    print_row += '#'
            
            print(print_row)
            
            
class _pixel:
    """
    Defines a pixel within a virtual matrix
    """
    def __init__(self, idx, num_rows, num_cols):
        self.idx = idx
        self.col_id = idx % num_cols
        self.row_id = int((idx - (idx % num_cols)) / num_cols)
        self.address = (self.row_id, self.col_id)
        
        self.r, self.g, self.b = 0, 0, 0
        
    def rgb(self):
        """
        Returns r/g/b values as a tuple
        """
        return self.r, self.g, self.b
    
    def rgbhex(self):
        """
        Returns r/g/b values as a hex value
        """
        hex_color = [format(color, '02x') for color in self.rgb()]
        return '{}{}{}'.format(*hex_color)
    
    def setrgb(self, r=0, g=0, b=0):
        """
        Sets pixel to a new color from r/g/b arguments
        """
        for color in (r, g, b):
            try:
                color = int(color)
            except:
                return
            if color < 0 or color > 255:
                return
            
        self.r = r
        self.g = g
        self.b = b
        
    def sethex(self, hex_str='000000'):
        """
        Sets pixel to a new color from hex
        """
        rgb = _hex2rgb(hex_str)
        return self.setrgb(*rgb)