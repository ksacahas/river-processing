import numpy as np
from count_mismatches import *

def optimize_bandwidth(calibration_folder, sgr_folder, plot=False):
    bws = np.arange(1, 16, step=1.0)
    mismatch_counts = []
    for bw in bws:
        m = count_mismatches(calibration_folder, sgr_folder, bw)
        mismatch_counts.append(m)

    if plot:
        plt.figure()
        plt.plot(bws, mismatch_counts, color='deeppink')
        plt.xlabel("Bandwidth")
        plt.ylabel("# of mismatches")
        plt.show()
    
    
    am = np.argmin(mismatch_counts)
    return bws[am]

