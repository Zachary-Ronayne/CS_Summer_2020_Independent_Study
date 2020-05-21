
"""

TODO:

Train a neural network on the grid game
    Figure out methods with TensorFlow to make it not slow
    Play with network settings for good performance

"""

# hide warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# normal imports
from learning.QLearn import *

from Constants import *

# create a grid
gridW, gridH = 4, 6
grid = np.zeros((gridH, gridW), dtype=np.int32)
grid[5, 3] = WIN
grid[3, 3] = DEAD

grid[1, 0] = BAD
grid[2, 0] = GOOD
grid[3, 0] = GOOD
grid[3, 1] = GOOD
grid[3, 2] = GOOD

grid[0, 1] = GOOD
grid[0, 2] = GOOD
grid[0, 3] = GOOD
grid[1, 3] = GOOD
grid[2, 3] = GOOD


# make the model
model = DummyGame(grid)

# use the network model, or the QTable model
network = True

if network:
    # make the network
    net = Network(gridW * gridH, 5, model, inner=[100])

    print(net.getOutputs())

    # train the network
    for i in range(1):
        total = model.playGame(net, learn=True)
        print("Training: " + str(i))
    print(net.getOutputs())

    # run the final results of the game
    # print(model.playGame(net, learn=False, printPos=True))

else:
    # make the table
    qTable = Table(gridW * gridH, 5, model, learnRate=0.5, discountRate=0.7)

    # train model
    qTable.explorationRate = 0.9
    for i in range(1000):
        total = model.playGame(qTable, learn=True)

    # run the model
    qTable.explorationRate = 0
    for i in range(1):
        total = model.playGame(qTable, learn=False, printPos=True)
        print(str(model.x) + " " + str(model.y) + " " + str(total))
    print()

    # print the game grid and q table
    print(np.array([[model.rewards[g] for g in gg] for gg in grid]))
    print()
    print(qTable.qTable)
