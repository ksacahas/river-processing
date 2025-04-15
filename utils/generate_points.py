import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
import pandas as pd
from PIL import Image
from skimage.morphology import skeletonize
from skimage import measure
import random
import sys
import os
from utils.find_closest_points import *
from utils.find_angles import *
from utils.find_neighbors import *
from utils.plot_line_segment import *

def generate_points(args):
    # This function generates randomly sampled points from an image,
    # approximates the flow direction, and saves the sampled points.

    # Unpack arguments
    image_path, file_path, K, plot = args

    # Import image
    image_name = os.path.basename(image_path)

    tg = Image.open(image_path)

    w, h = tg.size

    # Convert image to binary
    tg_binary = tg.convert('L')
    tg_binary = np.array(tg_binary)
    tg_binary[tg_binary < 128] = 0
    tg_binary[tg_binary >= 128] = 1

    tg_binary_river = np.argwhere(tg_binary > 0)
    
    # Find river skeleton
    skeleton = skeletonize(tg_binary, method='lee')
    skeleton_list = np.argwhere(skeleton > 0).astype(int)
    
    # Find river contours
    contour_list = measure.find_contours(1 - tg_binary, 0)
    contour_list = np.vstack(contour_list).astype(int)

    contour = np.zeros([tg_binary.shape[0], tg_binary.shape[1]])
    for item in contour_list:
        contour[item[0], item[1]] = 1

    # Apply edge filter
    # Points will not be sampled in the outermost 10 pixels of the image
    filtered_coords = [coord for coord in tg_binary_river
                       if 10 <= coord[0] < h - 10 and 10 <= coord[1] < w - 10
                       ]

    # Randomly select pixels
    pixels = [random.choice(filtered_coords) for _ in range(K)]

    # Initialize containers for generated points and directions
    ncs, nss, slopes_nc, slopes_ns, slopes, angles = [], [], [], [], [], []

    # Generate points 
    for i in range(len(pixels)):
        pix = pixels[i]
        # Set neighbor search radius
        N = 40
        # Find neighbors
        neighbors = find_all_neighbors(tg_binary, pix, N)
        # Find closest contour and skeleton points
        ns, nc, path = find_closest_points(pix, neighbors, contour, skeleton)

        # If pix is neither in skeleton nor in contour
        if skeleton[pix[0], pix[1]] == 0 and contour[pix[0], pix[1]] == 0:
            # Check for valid contour and skeleton points, otherwise replace
            while nc is None or ns is None:
                pix = random.choice(filtered_coords)
                neighbors = find_all_neighbors(tg_binary, pix, N)
                ns, nc, path = find_closest_points(pix, neighbors, contour, skeleton)
            pixels[i] = pix
                        
        # Calculate slopes and angles
        found_angles = False
        while found_angles == False:
            try:
                slope_nc, slope_ns, slope_av, angle_av = find_angles(tg_binary, skeleton, contour, pix, ns, nc)
            except:
                pix = random.choice(filtered_coords)
                neighbors = find_all_neighbors(tg_binary, pix, N)
                ns, nc, path = find_closest_points(pix, neighbors, contour, skeleton)
                pixels[i] = pix
            else:
                found_angles = True
        
        # Append data to lists
        ncs.append(nc)
        nss.append(ns)
        slopes_nc.append(slope_nc)
        slopes_ns.append(slope_ns)
        slopes.append(float(slope_av))
        angles.append(float(angle_av))

    # Create dataframe for saving
    df = pd.DataFrame({
        'pixel': pixels,
        'closest contour point': ncs,
        'closest skeleton point': nss,
        'slope at nc': slopes_nc,
        'slope at ns': slopes_ns,
        'average slope': slopes,
        'average angle': angles
    })

    # Save data
    return df
