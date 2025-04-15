import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage.morphology import skeletonize
import random
import os
from skimage import measure
from collections import deque
from utils.find_shortest_path import *
from utils.find_path import *

def find_closest_points(center, all_neighbors, contour, skeleton):
    # number of levels
    N = len(all_neighbors)
    
    # list of pixels in the contour and skeleton
    contour_list_all = np.argwhere(contour>0).astype(int)
    skeleton_list_all = np.argwhere(skeleton>0).astype(int)

    contour_list = [p for p in contour_list_all if center[0]-N <= p[0] <= center[0]+N and
                    center[1]-N <= p[1] <= center[1]+N]
    skeleton_list = [p for p in skeleton_list_all if center[0]-N <= p[0] <= center[0]+N and
                    center[1]-N <= p[1] <= center[1]+N]

    if contour[center[0], center[1]] > 0:
        return None, center, [0,0]

    if skeleton[center[0], center[1]] > 0:
        return center, None, [0,0]
    
    # Initialize the minimum distance and the corresponding points
    min_distance = float('inf')
    closest_skeleton = None

    # find closest point on a skeleton
    for i, neighbors in enumerate(all_neighbors):
        # check if any point in neighbors is also in skeleton
        valid_points = [pix for pix in skeleton_list if any(np.array_equal(pix, x) for x in neighbors)]
        for candidate_point in valid_points:
            # find the shortest path on the grid between center and candidate_point
            path = find_shortest_path(skeleton, center, candidate_point)

            # calculate the distance to the candidate skeleton point
            distance = np.sqrt((candidate_point[0] - center[0])**2 + (candidate_point[1] - center[1])**2)

            # if the candidate point is closer, update the minimum distance and the corresponding point
            if distance < min_distance:
                min_distance = distance
                closest_skeleton = candidate_point
                
    # Initialize the minimum distance and the corresponding points
    min_distance = float('inf')
    closest_contour = None
    best_path = None
    found_path = False
    
    # find closest point on a contour
    for i, neighbors in enumerate(all_neighbors):
        # check if any point in neighbors is also in contour
        valid_points = [pix for pix in contour_list if any(np.array_equal(pix, x) for x in neighbors)]
        # sort candidate points by distance
        if len(valid_points)>0:
            valid_points_arr = np.array(valid_points)
            valid_points_list = [l.tolist() for l in valid_points]
            distance = np.sqrt((valid_points_arr[:,0] - center[0])**2 +
                           (valid_points_arr[:,1] - center[1])**2)
            valid_points = [x for d,x in sorted(zip(distance,valid_points_list))]
        
        for candidate_point in valid_points:
            # check if there is a valid path on the grid between center and candidate_point
            path = find_path(center, candidate_point, skeleton) # a valid path can't cross the skeleton!


            # if the candidate point is closer, update the minimum distance and the corresponding point
            if path is not None:
                found_path = True
                closest_contour = np.array(candidate_point)
                best_path = path
                break

        if found_path == True:
            break
    
    return closest_skeleton, closest_contour, best_path

        




