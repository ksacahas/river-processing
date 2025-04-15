import numpy as np

def find_path(start, goal, skeleton):
    # Define possible movement directions (up, down, left, right)
    directions = [(-1,0), # up
                  (1,0), # down
                  (0,-1), # left
                  (0,1)] # right

    
    # initialize the path with the starting point
    start = tuple(start)
    goal = tuple(goal)
    path = [start]

    # keep track of visited points to avoid going in circles
    visited = set([start])

    while path[-1] != goal:
        x, y = path[-1]

        # determine the relative position of the goal with respect
        # to the current point
        dx = goal[0] - x
        dy = goal[1] - y

        # prioritize moves based on relative position
        if dx < 0 and (x-1,y) not in visited and skeleton[x-1,y]==0:
            # move up
            path.append((x-1,y))
            # mark the current point as visited
            visited.add(path[-1])

        elif dx > 0 and (x+1,y) not in visited and skeleton[x+1,y]==0:
            # move down
            path.append((x+1,y))
            # mark the current point as visited
            visited.add(path[-1])

        elif dy < 0 and (x,y-1) not in visited and skeleton[x,y-1]==0:
            # move left
            path.append((x,y-1))
            # mark the current point as visited
            visited.add(path[-1])

        elif dy > 0 and (x,y+1) not in visited and skeleton[x,y+1]==0:
            # move right
            path.append((x,y+1))
            # mark the current point as visited
            visited.add(path[-1])

        else:
            # no valid moves in the prioritized order —> backtrack
            path.pop()


        # if the path becomes empty, no valid path exists
        if not path:
            return None

    return path
            
