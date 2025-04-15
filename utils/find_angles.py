import numpy as np
from utils.find_neighbors import *
from utils.calculate_slope_regression import *
from utils.calculate_angle import *
from utils.weightedaverage import *
from utils.find_path import *

def find_angles(tg_binary, skeleton, contour, pix, ns, nc):

    # list of pixels that belong to the skeleton
    skeleton_list = np.argwhere(skeleton>0).astype(int)

    # list of pixels that belong to the contour
    contour_list = np.argwhere(contour>0).astype(int)

    # initialize containers to store the slopes and angles
    slope_c = None
    slope_s = None
    angle_s = None
    angle_c = None
    slope_av = None
    angle_av = None

    # if pix is in skeleton
    if skeleton[pix[0], pix[1]] > 0 and contour[pix[0], pix[1]] == 0:
        
        # identify the pixel's first and second neighbors 
        ns_neighbors = find_all_neighbors(tg_binary, ns, 2)
        ns_neighbors = [*ns_neighbors[0], *ns_neighbors[1]]

        # now identify first and second neighbors that are in skeleton_list
        ns_s_n = (ns, *[n for n in ns_neighbors if any(np.array_equal(n, r) for r in skeleton_list)])

        # calculate slope and angle
        slope_s = calculate_slope_regression(ns_s_n)

        angle_s = calculate_angle(slope_s)

    # if pix is in contour
    elif contour[pix[0], pix[1]] > 0 and skeleton[pix[0], pix[1]] == 0:

        # identify the pixel's first and second neighbors
        nc_neighbors = find_all_neighbors(tg_binary, nc, 2)
        nc_neighbors = [*nc_neighbors[0], *nc_neighbors[1]]

        # now identify first and second neighbors that are in contour_list
        nc_c_n_candidates = (nc, *[n for n in nc_neighbors if any(np.array_equal(n, r) for r in contour_list)])
        nc_c_n = []

        for candidate_point in nc_c_n_candidates:
            # check if there is a valid path on the grid between pix and candidate_point
            path = find_path(pix, candidate_point, skeleton) # a valid path can't cross the skeleton!

            if path is not None:
                nc_c_n.append(candidate_point)
                
        # calculate slope and angle
        slope_c = calculate_slope_regression(nc_c_n)

        angle_c = calculate_angle(slope_c)

    # if pix is neither in skeleton nor in contour
    else:
        # identify the closest skeleton point's first and second neighbors
        ns_neighbors = find_all_neighbors(tg_binary,ns, 2)
        ns_neighbors = [*ns_neighbors[0], *ns_neighbors[1]]

        # now identify first and second neighbors that are in skeleton_list
        ns_s_n = (ns, *[n for n in ns_neighbors if any(np.array_equal(n, r) for r in skeleton_list)])
        ns_s_n = ns_s_n[:5]

        # calculate slope
        slope_s = calculate_slope_regression(ns_s_n)

        # identify the closest contour point's first and second neighbors
        # start with some extra neighbors in case we need to remove some due to invalid paths (see below)
        nc_neighbors = find_all_neighbors(tg_binary, nc, 3) 
        nc_neighbors = [*nc_neighbors[0], *nc_neighbors[1]]

        # now identify first and second neighbors that are in contour_list, without crossing skeleton line
        nc_c_n = (nc, *[n for n in nc_neighbors if any(np.array_equal(n, r) for r in contour_list)])
        
        # this part ensures that we aren't crossing the skeleton line to find the nearest contour points
        # this can be an issue is the river is only a few pixels wide (points on the opposite riverbank may
        # be closer to the closest contour point than other contour points up- or downstream)
        for nc_c_n_point in nc_c_n:
            path = find_path(pix, nc_c_n_point, skeleton) # a valid path can't cross the skeleton!
            # if no valid path is found, remove the point from the list
            if path is None: 
                nc_c_n_list = list(nc_c_n)
                nc_c_n_list = list(filter(lambda x: not np.array_equal(x, nc_c_n_point), nc_c_n_list))
                nc_c_n = tuple(nc_c_n_list)
                
        # only use the closest 5 points (this is in case we didn't delete any invalid points above)        
        nc_c_n = nc_c_n[:5]
        
        # calculate slope
        slope_c = calculate_slope_regression(nc_c_n)

    if slope_s is not None and slope_c is not None:
        slope_av = weightedaverage(pix, nc, ns, slope_c, slope_s)
        angle_av = calculate_angle(slope_av)

    if slope_c is None and slope_s is not None:
        slope_av = slope_s
        angle_av = calculate_angle(slope_s)

    if slope_s is None and slope_c is not None:
        slope_av = slope_c
        angle_av = calculate_angle(slope_c)

    return slope_c, slope_s, slope_av, angle_av
