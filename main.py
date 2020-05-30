
"""

TODO:

Train a neural network on the grid game
    Create good training strategy
        Find Q values of next state, and use the maximum Q value of that state to backpropagate?
            page 108 in book

    Find new source of slow speed in network code, probably the training and set up time
    Should Adam be used for the net in compile?
        make a way to update learning rate from the optimizer in net.compile
    Should discount rate be used at all in the neural network model?
    Allow for network to have no hidden layers, it throws an error if there are none

    Add ability for player to play and train network

"""

# hide warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# normal imports
from learning.QLearn import *

from Constants import *


# create a grid
# gridW, gridH = 4, 6
gridW, gridH = 3, 1
startX, startY = 1, 0
grid = np.zeros((gridH, gridW), dtype=np.int32)

grid[0, 0] = WIN
grid[0, 2] = DEAD

"""
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
"""


# make the model
model = DummyGame(grid, pos=(startX, startY))

# use the network model, or the QTable model
network = True

if network:
    # make the network
    net = Network(gridW * gridH, NUM_ACTIONS, model, inner=[20], learnRate=0.1, explorationRate=.71)

    # train the network
    for i in range(5):
        total = model.playGame(net, learn=True)
        print("Training: " + str(i) + ", " + str(model.x) + " " + str(model.y) + " " + str(total))

    # run the final results of the trained model
    net.explorationRate = 0
    print("Final score: " + str(model.playGame(net, learn=False, printPos=True)))

    print("Outputs: " + str(net.getOutputs()))

    print("Final Pos: " + str(model.x) + " " + str(model.y))
    print("Grid:")
    print(np.array([[model.rewards[g] for g in gg] for gg in grid]))

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
