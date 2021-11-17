import numpy as np
import maze as mz

# Description of the maze as a numpy array
maze = np.array([
    [0, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [3, 1, 1, 1, 1, 1, 0],
    [4, 3, 0, 0, 0, 2, 0]
])

env = mz.Maze(maze)

# Finite horizon
horizon = 10
# Solve the MDP problem with dynamic programming
V, policy= mz.dynamic_programming(env,horizon)

method = 'DynProg'
start  = (0,0)
path = env.simulate(start, policy, method)