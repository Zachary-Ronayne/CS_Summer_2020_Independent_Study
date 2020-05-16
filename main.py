
"""

TODO:

Create class to store the array for the Q learning table
    Should have options for number of actions and number of states

Create a simple grid game, a class to hold it
    AI controls a thing that can go up down left right
    Moving means -1
    Hitting a good square means +1
    Hitting a bad square means -3
    Hitting a dead square means -10 and end
    Hitting a win square means +10 and end

    Make the exploration rate based on the different rewards from each new state, not just randomly exploring or not
        like, higher valued actions should have a higher weight,
        that difference in weight is lowered by exploration rate

Train a network on this grid game

"""

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
model = DummyModel(grid)
qTable = Table(gridW * gridH, 5, model.rewardFunc, model, learnRate=0.5, discountRate=0.7)

# train model
model.explorationRate = 0.9
for i in range(1000):
    total = model.playGame(qTable, learn=True)

# run the model
model.explorationRate = 0
for i in range(1):
    total = model.playGame(qTable, learn=False, printPos=True)
    print(str(model.x) + " " + str(model.y) + " " + str(total))


print(np.array([[model.rewards[g] for g in gg] for gg in grid]))
print(qTable.qTable)
