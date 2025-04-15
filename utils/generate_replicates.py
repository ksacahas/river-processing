import numpy as np
import os
import sys
import random
import shutil
import pandas as pd

def parse_list_of_strings(input_list):
    # This function takes a list of strings representing lists of integers,
    # removes the square brackets, splits the strings into individual components,
    # converts them to integers, and returns a list of lists of integers.
    result = []
    for item in input_list:
        # Remove brackets and split the string into numbers
        numbers = [int(num) for num in item.strip('[]').split()]
        # Append the list of numbers to the result
        result.append(numbers)
    return result

def generate_replicates(args):
    data_path, output_path, n_replicates = args

    # Read the CSV into a DataFrame
    data = pd.read_csv(data_path)

    file_name = os.path.basename(data_path)

    n_points = len(data)

    cohort_sizes = np.array([2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 20, 24, 25, 30, 32,
                             32, 40, 50, 60, 80, 90, 100, 120, 150, 160, 200,
                             240, 250, 300, 320,
                             400, 500, 600, 750, 800, 1000, 1250,
                             1600, 2000, 2500])

    cohort_sizes_trunc = cohort_sizes[cohort_sizes <= n_points]

    for r in range(n_replicates):
        # Create a directory for each replicate
        replicate_dir = os.path.join(output_path, f"replicate_{r+1}")
        os.makedirs(replicate_dir, exist_ok=True)

        for n in cohort_sizes_trunc:
            subsample_list = []
            # Generate one cohort of size 'n' for this replicate
            for _ in range(1):  # Only one cohort per size per replicate
                # Choose 'n' random data points
                random_indices = random.sample(range(len(data)), n)
                sampled_data = data.iloc[random_indices]  # Use iloc for row indexing

                # Extract pixel coordinates, slopes, and angles using column names
                pixels = np.array(parse_list_of_strings(sampled_data['pixel']))
                slopes = np.expand_dims(sampled_data['average slope'], axis=1)
                angles = np.expand_dims(sampled_data['average angle'], axis=1)

                # Combine the extracted data
                d = np.hstack((pixels, slopes, angles))
                subsample_list.append(d)

            # Save the cohort as a CSV inside the replicate directory
            subsample_df = pd.DataFrame(np.vstack(subsample_list))
            cohort_filename = f"{os.path.splitext(file_name)[0]}_{n}_samples.csv"
            cohort_path = os.path.join(replicate_dir, cohort_filename)

            subsample_df.to_csv(cohort_path, index=False, header=False)
