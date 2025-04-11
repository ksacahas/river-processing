import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.optimize import curve_fit
from scipy import stats

def calculate_slope_regression(neighbors):
    if len(neighbors) < 2:
        return None  # At least two points are needed to calculate a slope

    # Separate the x and y coordinates
    x = np.array([coord[0] for coord in neighbors]).reshape(-1, 1)
    y = np.array([coord[1] for coord in neighbors])

    if np.all(y == y[0]):  # Check if all y-coordinates are the same
        return 0  # The line is horizontal, so return 0
    if np.all(x == x[0]):  # Check if all x-coordinates are the same
        return float('inf')  # The line is vertical, so return infinity

    # Create a linear regression model and fit it to the data
    model = LinearRegression().fit(x, y)
    
    # The slope is the coefficient of x in the linear regression model
    slope = model.coef_[0]
    
    return slope
