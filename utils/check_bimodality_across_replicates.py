import numpy as np
import pandas as pd
import os
import re
from utils.check_bimodality import *

def check_bimodality_across_replicates(args):
    data_dir, bw, save_path = args
    base_name = os.path.basename(data_dir)

    all_replicates = os.listdir(data_dir)

    results = []
    
    # Iterate through replicate directories (1 to 100)
    for replicate_dir in all_replicates:
        if replicate_dir.startswith("replicate_"):

            replicate_index = replicate_dir.split("_")[1]

            # Read CSV files from the replicate directory
            for file_name in os.listdir(os.path.join(data_dir, replicate_dir)):
                if file_name.endswith('.csv'):

                    # Read the CSV file
                    file_path = os.path.join(data_dir, replicate_dir, file_name)

                    # Extract sample count from file name
                    sample_count = int(file_name.split('_')[-2])

                    data = pd.read_csv(file_path, header=None).values
                    angles = data[:, 3]

                    x_vals = np.linspace(-90, 90, 1000)
                    kde_vals = compute_kde(angles, x_vals, bw)
                    peaks, peak_heights = analyze_peaks(kde_vals, x_vals)

                    bimodal, similar_heights, height_check = check_bimodality(angles, bw, True)

                    # Store results in a dictionary
                    results.append({
                        'name': base_name,
                        'samples': sample_count,
                        'bimodal': bimodal,
                        'replicate': replicate_index,  # Include replicate index
                        })

    # Convert results to a DataFrame for easy manipulation
    results_df = pd.DataFrame(results)
    results_df.to_csv(save_path)
