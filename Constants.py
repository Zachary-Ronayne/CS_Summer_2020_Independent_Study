# indexes for rewards on grid spaces
MOVE = 0
GOOD = 1
BAD = 2
DEAD = 3
WIN = 4
DO_NOTHING = 5
NUM_REWARD_SQUARES = 5

# reward values for corresponding indexes
D_MOVE = 0
D_GOOD = 1
D_BAD = -3
D_DEAD = -10
D_STUCK = -10
D_WIN = 10
D_DO_NOTHING = -1

# indexes for moves
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
CANT_MOVE = 4

# game constants
MOVE_COST = 1
MAX_MOVES = 40
SIMPLE_BELLMAN = False
NUM_ACTIONS = 5

# True if the AI should be able to do nothing during a move, or if they have to pick a move that actually moves them
ENABLE_DO_NOTHING = False

TRACK_MOVE_HISTORY = True

# used to stop importing TensorFlow, should only be used for testing, should be False in any full version
USE_TENSOR_FLOW = True

# used to stop importing Pygame, should only be used for testing, should be False in any full version
USE_PY_GAME = True
