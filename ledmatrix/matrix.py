import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions

from .vmatrix import vmatrix

_SETTINGS = {
    'hardware_mapping': 'adafruit-hat',
    'rows': 32,
    'cols': 64,
    'gpio_slowdown': 2
}

def draw_matrix(func):
    """
    Wrapper function to be used as a decorator on an app's primary draw function
    """
    def run_matrix(*args, **kwargs):
        
        # Set matrix options
        options = RGBMatrixOptions()
        for setting, val in _SETTINGS.items():
            setattr(options, setting, val)
            
        # Initialize RGB matrix and two virtual matrices (cache, new)
        matrix = RGBMatrix(options=options)
        print('Matrix initialized.')
        vm_cache = vmatrix(SETTINGS['rows'], _SETTINGS['cols'])
        vm_new = vmatrix(SETTINGS['rows'], _SETTINGS['cols'])
        
        # LOOP until interrupted
        try:
            while True:
                # Refresh data and draw in new virtual matrix
                func(vmatrix=vm_new, *args, **kwargs)
                
                # If virtual matrix is changed, redraw changed pixels and recache
                changed_pixels = vm_new.compare_to_cache(vm_cache)
                if changed_pixels:
                    _draw_changes(matrix, changed_pixels)
                    vm_cache.set_pixels(changed_pixels)
                    
                # Sleep before refreshing, if sleep time is passed in
                if 'sleep' in kwargs:
                    try:
                        time.sleep(kwargs['sleep'])
                    except:
                        pass
                    
        except KeyboardInterrupt:
            print('Matrix terminated.')
            
    return run_matrix


def _draw_changes(matrix, changed_pixels):
    """
    Redraw list of pixels on physical matrix
    """
    for px in changed_pixels:
        matrix.SetPixel(px.col_id, px.row_id, px.r, px.g, px.b)