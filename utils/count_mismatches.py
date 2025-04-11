import os
import pandas as pd
import numpy as np
from scipy.signal import find_peaks, peak_prominences
from scipy.stats import gaussian_kde
from sklearn.neighbors import KernelDensity
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from datetime import datetime
from check_bimodality import *    


def count_mismatches(calibration_folder, sgr_folder, bw):
    # Count the number of mismatches between the bimodality calibration set
    # and the results from applying the bimodality check to the 'samples.csv' files.

    bimodality_data = {}

    # Step 1: Load all .csv files from the calibration folder
    calibration_files = [f for f in os.listdir(calibration_folder) if f.startswith('bimodality_calibration_set')
                         and f.endswith('.csv')]

    dataframes = []

    for file in calibration_files:
        df = pd.read_csv(os.path.join(calibration_folder, file))
        dataframes.append(df)

    combined_df = pd.concat(dataframes, ignore_index=True)

    # Group by 'Name' and calculate the mean of the second column for each group
    average_df = combined_df.groupby('File')['Bimodal'].mean().reset_index()

    # Rename columns if needed for clarity
    average_df.columns = ['File', 'Average']

    average_df['Average'] = average_df['Average'] >= 0.5

    mismatch_count = 0
    # Walk through the SGR directory to find all 'samples.csv' files
    for root, _, files in os.walk(sgr_folder):
        for file in files:
            if file.endswith('samples.csv'):
                file_path = os.path.join(root, file)

                # Apply the bimodality check to the file
                data = pd.read_csv(file_path)
                angles = data['average angle'].values

                x_vals = np.linspace(-90, 90, 1000)
                kde_vals = compute_kde(angles, x_vals, bw)
                peaks, peak_heights = analyze_peaks(kde_vals, x_vals)

                bimodal_result, similar_heights, height_check = check_bimodality(angles, bw, reorient=True)


                # Check against the calibration set
                if file in average_df['File'].values:
                    
                    expected_bimodal = average_df[average_df['File']==file]['Average'].values[0]
                    # If the bimodality results don't match, count it as a mismatch
                    if (bimodal_result != expected_bimodal):
                        mismatch_count += 1
                        
    return mismatch_count
