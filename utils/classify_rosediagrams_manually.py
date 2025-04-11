import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from scipy.signal import find_peaks, peak_prominences
from sklearn.neighbors import KernelDensity
from rose_diagram import rose_diagram
from datetime import datetime

def classify_rosediagrams_manually(input_dir, output_path):
    bimodality_results = []
    cohort_sizes = np.array([2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 20, 24, 25, 30, 32,
                             32, 40, 50, 60, 80, 90, 100, 120, 150, 160, 200,
                             240, 250, 300, 320, 400, 500, 600, 750, 800, 1000, 1250,
                             1600, 2000, 2500])
    
    class BimodalitySelector:
        def __init__(self, file_name):
            self.file_name = file_name
            self.bimodal_button = Button(plt.axes([0.1, 0.05, 0.3, 0.075]), 'Bimodal')
            self.not_bimodal_button = Button(plt.axes([0.6, 0.05, 0.3, 0.075]), 'Not Bimodal')
            self.bimodal_button.on_clicked(lambda _: self.save_result(True))
            self.not_bimodal_button.on_clicked(lambda _: self.save_result(False))
            plt.show()
        
        def save_result(self, is_bimodal):
            bimodality_results.append([self.file_name, is_bimodal])
            plt.close()
    
    sample_files = {
        f"{os.path.basename(root).removeprefix('sine_generated_river').lstrip('_')}_{file}": os.path.join(root, file)
        for root, _, files in os.walk(input_dir) for file in files if file.startswith('w') and file.endswith('.csv')
        and not file.endswith('samples.csv')
    }
    
    for file_path in sample_files.values():
        #print("processing file path: ", file_path)

        file_name = os.path.basename(file_path)
        data = pd.read_csv(file_path)
        angles = data['average angle'].values
        max_size = len(angles)
        available_cohorts = cohort_sizes[cohort_sizes <= max_size]

        for idx, cohort_size in enumerate(available_cohorts):
            base_name = file_name.replace(".csv", "")
            file_name_with_cohortsize = f"{base_name}_{cohort_size}samples.csv"
            subset = data.sample(n=cohort_size, replace=True)
            subset_angles = subset['average angle'].values
            x_vals = np.linspace(-90, 90, 1000)
            kde = KernelDensity(kernel='gaussian', bandwidth=8).fit(subset_angles[:, None])
            kde_vals = np.exp(kde.score_samples(x_vals[:, None]))
            peaks, _ = find_peaks(kde_vals)
            prominences = peak_prominences(kde_vals, peaks)[0]
            
            output_file = f"{os.path.splitext(file_path)[0]}_{cohort_size}samples.csv"
            output_basename = os.path.basename(output_file)
            subset.to_csv(output_file, index=False)

            # Continue working with our subset
            fig = plt.figure(figsize=(12,6))
            plt.subplots_adjust(bottom=0.22)
            gs = fig.add_gridspec(1, 2, width_ratios=[1, 1])
            ax1 = fig.add_subplot(gs[0, 0])

            ax1.hist(subset_angles, bins=np.arange(-90, 100, 10), density=True,
                     color='black', label='Histogram')
            ax1.plot(x_vals, kde_vals, color='gray', label='KDE')
            ax1.plot(x_vals[peaks], kde_vals[peaks], 'o', color='gray', label='Peaks')
            ax1.set_title(f"KDE and Histogram for {file_name}, cohort size={cohort_size}")
            ax1.set_xlabel("Angle")
            ax1.set_ylabel("Density")
            ax1.legend()

            theta, hist = rose_diagram(subset_angles, 10)
            ax2 = fig.add_subplot(gs[0, 1], polar=True)
            ax2.bar(theta, hist, width=np.deg2rad(10), align='edge', color='black')
            ax2.set_xticks(np.linspace(0, 2 * np.pi, 36, endpoint=False))
            ax2.set_xticklabels([f'{i}°' for i in range(0, 360, 10)])
            ax2.set_theta_direction(-1)
            ax2.set_theta_offset(np.radians(90))
            ax2.set_yticklabels([])
            ax2.spines['polar'].set_visible(False)  
            BimodalitySelector(file_name_with_cohortsize)
    
    results_df = pd.DataFrame(bimodality_results, columns=['File', 'Bimodal'])
    results_df.to_csv(output_path, index=False)
    return None
