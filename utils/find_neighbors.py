import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import random

def find_neighbors(matrix, start_pixel, n):
    rows, cols = len(matrix), len(matrix[0])
    visited = [[False] * cols for _ in range(rows)]

    # Mark the start_pixel as visited
    visited[start_pixel[0]][start_pixel[1]] = True

    # Define possible moves (including diagonals)
    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    # Queue for BFS
    queue = [(start_pixel, 0)]  # Each element is a tuple (pixel, distance)

    neighbors = []

    while queue:
        current_pixel, distance = queue.pop(0)
        row, col = current_pixel

        if distance == n:
            neighbors.append(current_pixel)
            continue  # Skip further exploration for this pixel at the current distance

        if distance < n:
            for move in moves:
                new_row, new_col = row + move[0], col + move[1]
                # Check if the new position is within the matrix bounds and is part of the river
                if 0 <= new_row < rows and 0 <= new_col < cols and matrix[new_row][new_col] == 1 and not visited[new_row][new_col]:
                    visited[new_row][new_col] = True
                    queue.append(((new_row, new_col), distance + 1))

    return neighbors

def find_all_neighbors(matrix, start_pixel, N):
    # finds all neighbors up to level N
    all_neighbors = []
    for n in range(1, N+1):
        neighbors = find_neighbors(matrix, start_pixel, n)
        all_neighbors.append(np.array(neighbors))
    return all_neighbors

