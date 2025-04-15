import pandas as pd
import numpy as np
from PIL import Image
import os
import sys
import random
import shutil

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# List all PNG and CSV files in the current directory
image_files = sorted([f for f in os.listdir(current_dir) if f.endswith('.png')])
data_files = sorted([f for f in os.listdir(current_dir) if f.endswith('.csv')])

# Define sample sizes
n_sample_choices = np.array([2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 20, 24, 25, 30, 32,
                             32, 40, 50, 60, 80, 90, 100, 120, 150, 160, 200,
                             240, 250, 300, 320,
                             400, 500, 600, 750, 800, 1000, 1250,
                             1600, 2000, 2500])
Nc = len(n_sample_choices)

# Number of replicates
n_replicates = 100

for i in range(len(data_files)):
    # Image and data paths
    image_path = image_files[i]
    data_path = data_files[i]
    file_name = os.path.basename(data_path)

    # Import data
    data = pd.read_csv(data_path).values

    for r in range(n_replicates):
        # Create a directory for each replicate
        replicate_dir = f"replicate_{r+1}"
        os.makedirs(replicate_dir, exist_ok=True)
        shutil.copy(image_path, replicate_dir)

        for n in n_sample_choices:
            subsample_list = []
            # Generate one cohort of size 'n' for this replicate
            for _ in range(1):  # Only one cohort per size per replicate
                # Choose 'n' random data points
                random_indices = random.sample(range(len(data)), n)
                sampled_data = data[random_indices, :]

                # Extract pixel coordinates, slopes, and angles
                pixels = np.array(parse_list_of_strings(sampled_data[:, 1]))
                slopes = np.expand_dims(sampled_data[:, 6], axis=1)
                angles = np.expand_dims(sampled_data[:, 7], axis=1)

                d = np.hstack((pixels, slopes, angles))
                subsample_list.append(d)

            # Save the cohort as a CSV inside the replicate directory
            subsample_df = pd.DataFrame(np.vstack(subsample_list))
            cohort_filename = f"{os.path.splitext(file_name)[0]}_{n}_samples.csv"
            cohort_path = os.path.join(replicate_dir, cohort_filename)

            subsample_df.to_csv(cohort_path, index=False, header=False)
)
