import numpy as np

def calculate_angle(slope):
    if np.abs(slope)<=1e-6:
        return 0
    if slope==float('inf'):
        return 90
    dx = 1
    dy = slope 
    angle = np.degrees(-np.arcsin(dy / np.sqrt(dx**2 + dy**2) )) # the minus sign makes result agree with angle definition
    return angle
