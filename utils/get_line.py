import numpy as np

def get_line(x, y, slope):
    # remember the slope we're using isn't "slope" in the plot
    # because x and y in the image follow array indexing
    # we need to convert x, y in the array to x, y in the image
    x_im = y
    y_im = x
    if slope==0:
        return 0, 0
    else:
        im_slope = slope

    b = y_im - im_slope * x_im

    # choose x-coordinates in the vicinity of x
    x_line = np.arange(x_im-5, x_im+6, step=1)
    y_line = im_slope * x_line + b
    return x_line, y_line
