from tensorflow import keras

# constants for the dummy game
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
NUM_ACTIONS = 5

# True if the AI should be able to do nothing during a move, or if they have to pick a move that actually moves them
ENABLE_DO_NOTHING = False
TRACK_MOVE_HISTORY = True


# general constants for Checkers game
# True to use a simplified Bellman function, False to use the full version
SIMPLE_BELLMAN = False

# used to stop importing TensorFlow, should only be used for testing, should be True in any full version
USE_TENSOR_FLOW = True

# used to stop importing Pygame, should only be used for testing, should be True in any full version
USE_PY_GAME = True

# used for saving neural Networks
NETWORK_SAVES = "saves"
PIECE_NETWORK_NAME = "piece"
GAME_NETWORK_NAME = "game"
DUEL_MODEL_NAME = "duel model"


# the optimization function used for Q Networks
OPTIMIZE_FUNCTION = keras.optimizers.SGD
# the loss function used for Q Networks
LOSS_FUNCTION = keras.losses.CategoricalCrossentropy

# the reward given when an action cannot be taken
Q_REWARD_INVALID_ACTION = -50

# constants for Q Learning models
# reward for when the game cannot select any pieces to move
Q_GAME_REWARD_NO_ACTIONS = -1

# reward when an ally piece moves
Q_PIECE_REWARD_MOVE = 1
# reward when an enemy piece moves
Q_PIECE_REWARD_ENEMY_MOVE = -1
# reward when a normal enemy piece is captured
Q_PIECE_REWARD_N_CAPTURE = 30
# reward when a king enemy piece is captured
Q_PIECE_REWARD_K_CAPTURE = 40
# reward when a normal ally piece is captured
Q_PIECE_REWARD_N_CAPTURED = -10
# reward when a king ally piece is captured
Q_PIECE_REWARD_K_CAPTURED = -15
# reward when an ally piece becomes a king
Q_PIECE_REWARD_KING = 5
# reward when an enemy piece becomes a king
Q_PIECE_REWARD_KINGED = -2
# reward for winning the game
Q_PIECE_REWARD_WIN = 1000
# reward for losing the game
Q_PIECE_REWARD_LOSE = -2000
# reward for drawing the game
Q_PIECE_REWARD_DRAW = -50
# reward for the game being still in progress
Q_PIECE_REWARD_PLAYING = 0
# this value is multiplied by the total number of moves, and added to the reward when the game ends
Q_PIECE_REWARD_MOVES_FACTOR = -1

# True to use convolutional layers for all neural networks with the Checkers Game Environments
#   False to use feed forward networks
Q_USE_CONVOLUTIONAL_LAYERS = True


# used by Game for the maximum moves which can be made without a capture,
#   before a game ends in a draw
E_MAX_MOVES_WITHOUT_CAPTURE = 25
