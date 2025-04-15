import numpy as np

def dist(point1, point2):
    return np.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

def weightedaverage(pix, p1, p2, slope1, slope2):
    dist1 = dist(pix, p1)
    dist2 = dist(pix, p2)
    
    w1 = 1/(dist1)
    w2 = 1/(dist2)

    if not np.isfinite(slope1) and not np.isfinite(slope2):
        return 100
   
    elif np.abs(slope1)==0.0 and np.abs(slope2)==0.0:
        return 0

    elif slope1==-slope2 and np.abs(slope1)>1 and dist1==dist2:
        return 100
    
    elif slope1==-slope2 and np.abs(slope1)<1 and dist1==dist2:
        return 0

    elif slope1==-0.0 and not np.isfinite(slope2):
        return -1

    elif slope1==0.0 and not np.isfinite(slope2):
        return 1

    elif not np.isfinite(slope1) and slope2==-0.0:
        return -1

    elif not np.isfinite(slope1) and slope2==0.0:
        return 1
        
    elif not np.isfinite(slope1) and np.isfinite(slope2):
        slope1 = 0
        slope2 = -1/slope2
        tot = (w1 * slope1 + w2 * slope2) / (w1 + w2)
        return -1/tot

    elif np.isfinite(slope1) and not np.isfinite(slope2):
        slope1 = -1/slope1
        slope2 = 0
        tot = (w1 * slope1 + w2 * slope2) / (w1 + w2)
        return -1/tot

    else:
        tot = (w1 * slope1 + w2 * slope2) / (w1 + w2)
        return tot
