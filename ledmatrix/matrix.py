import time

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from .vmatrix import vmatrix

_SETTINGS = {
    'hardware_mapping': 'adafruit-hat',
    'rows': 32,
    'cols': 64,
    'gpio_slowdown': 2
}

_CYCLE = None

def draw_matrix(func):
    """
    Wrapper function to be used as a decorator on an app's primary draw function
    """
    def run_matrix(*args, **kwargs):
        global _CYCLE
        
        # Set matrix options
        options = RGBMatrixOptions()
        for setting, val in _SETTINGS.items():
            setattr(options, setting, val)
            
        # Initialize RGB matrix and two virtual matrices (cache, new)
        matrix = RGBMatrix(options=options)
        print('Matrix initialized.')
        vm_cache = vmatrix(_SETTINGS['rows'], _SETTINGS['cols'])
        vm_new = vmatrix(_SETTINGS['rows'], _SETTINGS['cols'])
        
        # LOOP until interrupted
        try:
            while True:
                # Refresh data and draw in new virtual matrix
                # func is the function being wrapped; func_return is a dict of return arguments
                if _CYCLE is not None:
                    kwargs['cycle'] = _CYCLE
                func_return = func(vmatrix=vm_new, *args, **kwargs)
                
                # If virtual matrix is changed, redraw changed pixels and recache
                changed_pixels = vm_new.compare_to_cache(vm_cache)
                if changed_pixels:
                    _draw_physical(matrix, changed_pixels)
                    vm_cache.set_pixels(changed_pixels)
                    vm_new.clear()
                    
                # func_return parameters
                if type(func_return) == dict:
                    
                    # Sleep before refreshing again
                    if 'sleep' in func_return:
                        if type(func_return['sleep']) in [int, float]:
                            if func_return['sleep'] > 0:
                                time.sleep(func_return['sleep'])
                                
                    # Cycle through multiple panels
                    if 'cycle' in func_return:
                        cycle = func_return['cycle']
                        if type(cycle) == tuple:
                            if len(cycle) == 2:
                                _CYCLE = ((cycle[0] + 1) % cycle[1], cycle[1])
                    
        except KeyboardInterrupt:
            print('\nMatrix terminated.')
            
    return run_matrix


def _draw_physical(matrix, changed_pixels):
    """
    Redraw list of pixels on physical matrix
    """
    for px in changed_pixels:
        matrix.SetPixel(px.col_id, px.row_id, px.r, px.g, px.b)