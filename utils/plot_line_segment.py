import numpy as np

def plot_line_segment(point, slope, length):
    y1, x1 = point
    if slope==0:
        dx = 0
        dy = 5
    else:
        slope = 1/slope

        dx = length / (2 * np.sqrt(1 + slope**2))
        dy = slope * dx

    x2 = x1 + dx
    y2 = y1 + dy

    x0 = x1 - dx
    y0 = y1 - dy

    return [x0,x2],[y0,y2]

