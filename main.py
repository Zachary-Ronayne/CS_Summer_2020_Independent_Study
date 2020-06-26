
"""

TODO:

Make test cases

Find new source of slow speed in network code, probably the training and set up time
    Speed up general Checkers Game code
Try adding adaptive learning rate and discount rate
Try using convolutional layers
Try having two models, one for each player

Add distance to other pieces as part of the reward
    More reward for nearby pieces
Should be no reward for invalid actions, or high negative reward

Allow user to train network based on the user's input
    So when the user makes an action, that action should be used for the reward function,
    which trains the network

Add a control to the GUI to tell it to make a move with an exploration rate of zero

Fix the dummy model not working with recent changes

"""

# normal imports
from Checkers.Gui import *
from Checkers.Environments import *

"""
# center pygame window
os.environ['SDL_VIDEO_CENTERED'] = "1"


# for loading in or not loading in the saved version of the Networks
loadModel = False

# make game
game = Game(8)

pEnv = PieceEnvironment(game, current=None, pieceInner=[200, 200], gameInner=[500])
model = pEnv.internalNetwork
model.learnRate = 0.1
model.explorationRate = 0.1
model.discountRate = 0.0

gameModel = pEnv.gameNetwork
gameModel.learnRate = 0.1
gameModel.explorationRate = 0.1
gameModel.discountRate = 0.0

if loadModel:
    pEnv.loadNetworks(PIECE_NETWORK_NAME, GAME_NETWORK_NAME)

for i in range(30):
    currentTime = time.time()
    print("Game", str(i))
    print("(red reward, black reward, total moves)", str(pEnv.playGame(printReward=False)))
    print("took:", time.time() - currentTime, "seconds")
    print(E_TEXT[game.win], "final game board:")
    print(game.string(True))
    print()

game.resetGame()

gui = Gui(pEnv, printFPS=False)
gui.loop()
"""

# create a grid
gridUse = 4

if gridUse == 0:
    gridW, gridH = 3, 1
    startX, startY = 1, 0
elif gridUse == 1:
    gridW, gridH = 5, 1
    startX, startY = 2, 0
elif gridUse == 2:
    gridW, gridH = 5, 2
    startX, startY = 2, 0
elif gridUse == 3:
    gridW, gridH = 2, 2
    startX, startY = 0, 0
else:
    gridW, gridH = 4, 6
    startX, startY = 0, 0

grid = np.zeros((gridH, gridW), dtype=np.int32)

if gridUse == 0:
    grid[0, 0] = WIN
    grid[0, 2] = DEAD
elif gridUse == 1 or gridUse == 2:
    grid[0, 0] = WIN
    grid[0, 4] = DEAD
    grid[0, 1] = BAD
    grid[0, 3] = GOOD
    if gridUse == 2:
        grid[1, 0] = GOOD
        grid[1, 1] = GOOD
        grid[1, 2] = GOOD
        grid[0, 1] = DEAD
elif gridUse == 3:
    grid[1, 0] = GOOD
    grid[0, 1] = BAD
    grid[1, 1] = WIN
else:
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
    
    # grid[2, 2] = GOOD
    # grid[4, 2] = GOOD
    # grid[4, 3] = GOOD


def testDummyGame():
    """
    Simple code used to test the execution of the DummyEnvironment with Q learning
    """
    # make the model
    model = DummyGame(grid, sizeStates=True, pos=(startX, startY))

    # use the network model, or the QTable model
    network = True

    if network:
        # make the network
        net = Network(NUM_ACTIONS, model, inner=[],
                      learnRate=0.1, explorationRate=0.1, discountRate=0.5)

        # train the network
        for i in range(15):
            total = model.playGame(net, learn=True)
            print("Training: " + str(i) + ", " + str(model.x) + " " + str(model.y) + " " + str(total))

        # run the final results of the trained model
        net.explorationRate = 0
        print("Final score: " + str(model.playGame(net, learn=False, printPos=True)))

        print("Final Pos: " + str(model.x) + " " + str(model.y))
        print("Grid:")
        print(np.array([[model.rewards[g] for g in gg] for gg in grid]))

    else:
        # make the table
        qTable = Table(NUM_ACTIONS, model, learnRate=0.5, discountRate=0.7)

        # train model
        qTable.explorationRate = 1
        for i in range(100):
            model.playGame(qTable, learn=True)

        # run the model
        qTable.explorationRate = 0
        total = model.playGame(qTable, learn=False, printPos=True)
        print(str(model.x) + " " + str(model.y) + " " + str(total))
        print()

        # print the game grid and q table
        print(np.array([[model.rewards[g] for g in gg] for gg in grid]))
        print()
        print(qTable.qTable)
