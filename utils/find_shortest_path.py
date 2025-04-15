import numpy as np
from collections import deque

def find_shortest_path(matrix, start, goal):
    # Define possible movement directions (up, down, left, right)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Convert start and goal to tuples
    start = tuple(start)
    goal = tuple(goal)

    # Queue for BFS
    queue = deque()

    # Dictionary to store parent information for reconstructing the path
    parents = {}

    # Set of visited nodes
    visited = set()

    # Initialize starting node
    queue.append(start)
    visited.add(start)

    while queue:
        current = queue.popleft()

        # Check if we reached the goal
        if current == goal:
            # Reconstruct the path
            path = []
            while current in parents:
                path.append(current)
                current = parents[current]
            path.append(start)  # Include the start node
            path.reverse()      # Reverse the path to get it in the correct order
            return path

        # Explore neighbors
        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])

            # Check if the neighbor is within the matrix bounds
            if 0 <= neighbor[0] < matrix.shape[0] and 0 <= neighbor[1] < matrix.shape[1]:
                # Check if the neighbor is a valid move (non-zero in the matrix)
                # if matrix[neighbor[0], neighbor[1]] != 0:
                #    continue

                # Check if the neighbor has been visited
                if neighbor in visited:
                    continue

                # Mark the neighbor as visited and store parent information
                visited.add(neighbor)
                parents[neighbor] = current

                # Enqueue the neighbor
                queue.append(neighbor)

    # If no valid path is found, return an empty path
    return []
