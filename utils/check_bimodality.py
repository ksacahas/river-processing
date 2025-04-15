import numpy as np
from scipy.signal import find_peaks
from sklearn.neighbors import KernelDensity
import matplotlib.pyplot as plt
from rose_diagram import *

def compute_kde(angles, x_vals, bw):
    # Compute KDE with a specified bandwidth.
    kde = KernelDensity(kernel='gaussian', bandwidth=bw).fit(angles[:, None])
    return np.exp(kde.score_samples(x_vals[:, None]))

def analyze_peaks(kde_vals, x_vals, pad_width=5, edge_threshold=85):
    # Find peaks.
    peaks, _ = find_peaks(kde_vals)
    peak_heights = kde_vals[peaks]

    return peaks, peak_heights

def pad_edges(peaks, x_vals, kde_vals, minima, pad_width, edge_threshold):
    # Pad edges if necessary.
    left_edge = peaks[x_vals[peaks] < -edge_threshold]
    right_edge = peaks[x_vals[peaks] > edge_threshold]

    if left_edge.size > 0 or right_edge.size > 0:
        closest_min = get_closest_minimum(kde_vals, left_edge[0], minima) if left_edge.size > 0 else 0
        padded_kde = np.pad(kde_vals, (pad_width, 0), 'constant', constant_values=(closest_min, 0))
        return True
    return False

def get_closest_minimum(data, peak_idx, minima):
    # Find the minimum closest in position to the peak.
    return data[minima[np.argmin(np.abs(minima - peak_idx))]]


def check_bimodality(angles, bw=8, reorient=True):
    # Checks for bimodality based on peak heights.
    # angles:   array-like object containing the flow direction angles. 
    # bw:       bandwidth for KDE analysis. The default value bw=8 has been chosen to produce
    #           maximum agreement with manual bimodality classifications. 
    # reorient: Boolean that determines whether the histogram will be reoriented before the 
    #           bimodality test. If True, all angles will be recalculated with respect to the 
    #           point halfway between the two tallest peaks. Using reorient=True is recommended
    #           because the default angles (calculated with respect to 0° N) are arbitrary, wherease
    #           the reoriented angles may better reflect the data distribution and make it easier 
    #           to detect bimodality.

    bins = np.arange(-90, 91, 10)
    x_vals = np.linspace(-90, 90, 1000)
    angles = (angles + 90) % 180 - 90
    kde_vals = compute_kde(angles, x_vals, bw)
    peaks, peak_heights = analyze_peaks(kde_vals, x_vals)
    kde_vals_reor = np.zeros_like(kde_vals)
    peaks_reor, peak_heights_reor = np.zeros_like(peaks), np.zeros_like(peak_heights)

    # Don't reorient the diagrams
    if reorient==False:
        
        # If there are fewer than 2 peaks, we can't apply a bimodality test 
        if len(peak_heights) < 2:
            bimodal = False
            similar_height = None
            height_check = None

        # If there are at least 2 peaks, we can apply a bimodality test
        else:
            # Get the 2 tallest peaks
            sorted_indices = np.argsort(peak_heights)[::-1]
            tallest_peaks = sorted_indices[:2]

            # Check if the 2 tallest peaks have similar heights
            similar_height = np.isclose(peak_heights[tallest_peaks[0]], peak_heights[tallest_peaks[1]],
                                    atol=0.5*peak_heights[tallest_peaks[0]])

            # If there are only 2 peaks, we only apply the similar height check
            if len(peak_heights)==2:
                bimodal = similar_height
                height_check = None

            # If there are more than 2 peaks, the tallest 2 need to be at least twice as high as all other peaks
            else:
                third_peak = sorted_indices[2]
                height_check = min(peak_heights[tallest_peaks]) >= 2 * peak_heights[third_peak]
                bimodal = similar_height and height_check

    # Reorient the diagrams
    else:
        # If there are fewer than 2 peaks, we can't reorient the diagram or apply a bimodality test 
        if len(peak_heights) < 2:
            bimodal = False
            reoriented_angles = angles
            similar_height = None
            height_check = None
            
        # If there are at least 2 peaks, we can reorient and apply a bimodality test
        else:
            # Get the 2 tallest peaks
            sorted_indices = np.argsort(peak_heights)[::-1]
            tallest_peaks = sorted_indices[:2]
            xs_tallest_peaks = x_vals[peaks][tallest_peaks]  # x-values of the two tallest peaks

            # Calculate the midpoint
            midpoint = np.mean(xs_tallest_peaks)

            # Reorient the angles relative to the midpoint, wrapping them to [-90, +90]
            reoriented_angles = (angles - midpoint + 90) % 180 - 90

            # Recompute the KDE on reoriented angles
            kde_vals_reor = compute_kde(reoriented_angles, x_vals, bw)

            # Recompute peaks and peak heights for the reoriented KDE
            peaks_reor, peak_heights_reor = analyze_peaks(kde_vals_reor, x_vals)          

            # The reoriented KDE may have a different number of peaks than the original KDE
            # If there are fewer than 2 peaks, we can't apply a bimodality test 
            if len(peak_heights_reor) < 2:
                bimodal = False
                similar_height = None
                height_check = None
                
            # If there are at least 2 peaks, we can apply a bimodality test
            else:
                # Get the 2 tallest peaks for the reoriented KDE
                sorted_indices_reor = np.argsort(peak_heights_reor)[::-1]
                tallest_peaks_reor = sorted_indices_reor[:2]

                # Check if they have similar heights
                similar_height = np.isclose(peak_heights_reor[tallest_peaks_reor[0]], 
                                                   peak_heights_reor[tallest_peaks_reor[1]],
                                    atol=0.5*peak_heights_reor[tallest_peaks_reor[0]])

                # If there are only 2 peaks, we only apply the similar height check
                if len(peak_heights_reor)==2:
                    bimodal = similar_height
                    height_check = None

                # If there are more than 2 peaks, the tallest 2 need to be at least twice as high as all other peaks
                else:
                    third_peak_reor = sorted_indices_reor[2]
                    height_check = (min(peak_heights_reor[tallest_peaks_reor]) 
                                           >= 2 * peak_heights_reor[third_peak_reor])
                    bimodal = similar_height and height_check

    return bimodal, similar_height, height_check
