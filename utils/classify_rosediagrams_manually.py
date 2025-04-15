import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")  # Ensure interactive backend for .exe
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
    sample_files = {
        f"{os.path.basename(root).removeprefix('sine_generated_river').lstrip('_')}_{file}": os.path.join(root, file)
        for root, _, files in os.walk(input_dir) for file in files
        if file.startswith('w') and file.endswith('.csv') and not file.endswith('samples.csv')
    }

    class BimodalitySelector:
        def __init__(self, file_name):
            self.file_name = file_name
            self.fig = plt.gcf()
            self.ax_bimodal = plt.axes([0.1, 0.05, 0.3, 0.075])
            self.ax_not_bimodal = plt.axes([0.6, 0.05, 0.3, 0.075])
            self.bimodal_button = Button(self.ax_bimodal, 'Bimodal')
            self.not_bimodal_button = Button(self.ax_not_bimodal, 'Not Bimodal')
            self.bimodal_button.on_clicked(self.bimodal_clicked)
            self.not_bimodal_button.on_clicked(self.not_bimodal_clicked)
            self.fig.canvas.draw()
            plt.show(block=True)

        def bimodal_clicked(self, event):
            self.save_result(True)

        def not_bimodal_clicked(self, event):
            self.save_result(False)

        def save_result(self, is_bimodal):
            bimodality_results.append([self.file_name, is_bimodal])
            plt.close(self.fig)

    for file_path in sample_files.values():
        file_name = os.path.basename(file_path)
        data = pd.read_csv(file_path)
        angles = data['average angle'].values
        max_size = len(angles)
        available_cohorts = cohort_sizes[cohort_sizes <= max_size]

        for cohort_size in available_cohorts:
            base_name = file_name.replace(".csv", "")
            file_name_with_cohortsize = f"{base_name}_{cohort_size}samples.csv"
            subset = data.sample(n=cohort_size, replace=True)
            subset_angles = subset['average angle'].values

            output_file = f"{os.path.splitext(file_path)[0]}_{cohort_size}samples.csv"
            subset.to_csv(output_file, index=False)

            fig = plt.figure(figsize=(12, 6))
            plt.subplots_adjust(bottom=0.22)
            gs = fig.add_gridspec(1, 2, width_ratios=[1, 1])
            ax1 = fig.add_subplot(gs[0, 0])

            ax1.hist(subset_angles, bins=np.arange(-90, 100, 10), density=True,
                     color='black', label='Histogram')
            ax1.set_title(f"Histogram for {file_name}, cohort size={cohort_size}")
            ax1.set_xlabel("Angle")
            ax1.set_ylabel("Density")
            ax1.legend()

            theta, hist = rose_diagram(subset_angles, 10)
            ax2 = fig.add_subplot(gs[0, 1], polar=True)
            ax2.bar(theta, hist, width=np.deg2rad(10), align='edge', color='black')
            ax2.set_xticks(np.linspace(0, 2 * np.pi, 36, endpoint=False))
            ax2.set_xticklabels([f'{i}\u00b0' for i in range(0, 360, 10)])
            ax2.set_theta_direction(-1)
            ax2.set_theta_offset(np.radians(90))
            ax2.set_yticklabels([])
            ax2.spines['polar'].set_visible(False)

            BimodalitySelector(file_name_with_cohortsize)

    results_df = pd.DataFrame(bimodality_results, columns=['File', 'Bimodal'])
    results_df.to_csv(output_path, index=False)
