
"""

TODO:

Fix case where moves are not correcly calculated

Make a simple test game, like there is one correct move to win the game right away for the AI
    and make sure the AI can win in that simple case

Should be no reward for invalid actions, or high negative reward
    Ensure this is working for both reward functions

Add options to change filter size for convolutional layers
Fix bug where game ends while in progress

Demonstrate intelligent gameplay on 4x4 or 6x6

Also allow user to train network based on the user's input
    So when the user makes an action, that action should be used for the reward function,
    which trains the network

Add distance to other pieces as part of the reward
    More reward for nearby pieces

Speed up general Checkers Game code
    specifically the update moves method
    also optimize code in Environments
    also code in DuelModel
Improve code when making random moves
Allow network data outside TensorFlow to be saved, like learning rate and related

"""

# normal imports
from Checkers.Gui import *
from Checkers.DuelModel import *

# center pygame window
os.environ['SDL_VIDEO_CENTERED'] = "1"

# disable GPU
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

checkers = True


def setRates(model):
    """
    Utility for setting hyperparameters
    """
    model.learnRate = 0.5
    model.explorationRate = 0.8
    model.discountRate = 0.4
    model.explorationDecay = 0.95
    model.learnDecay = 0.95


def testCheckers():
    """
    Simple code for playing checkers game
    """
    # for loading in or not loading in the saved version of the Networks
    loadModel = True
    # number of games to play in training
    trainGames = 10
    # number for the default game to play, use None to just play a normal game
    defaultGameModel = 2

    # make game
    game = Game(4)

    # create the model
    env = DuelModel(game, rPieceInner=[200, 200, 200], rGameInner=[500, 500, 500],
                    bPieceInner=[200, 200, 200], bGameInner=[500, 500, 500])
    setRates(env.redEnv.internalNetwork)
    setRates(env.redEnv.gameNetwork)
    setRates(env.blackEnv.internalNetwork)
    setRates(env.blackEnv.gameNetwork)

    # load in the model if applicable
    if loadModel:
        env.load("", DUEL_MODEL_NAME)

    # set up a default game
    defaultGame = Game(4)
    defaultGame.clearBoard()

    if defaultGameModel == 0:
        defaultGame.spot(1, 3, (True, False), True)
        defaultGame.spot(0, 2, (False, False), True)
    elif defaultGameModel == 1:
        defaultGame.spot(1, 3, (True, False), True)
        defaultGame.spot(0, 1, (False, False), True)
    elif defaultGameModel == 2:
        defaultGame.spot(1, 3, (True, False), True)
        defaultGame.spot(0, 3, (True, False), True)
        defaultGame.spot(0, 1, (False, False), True)
    else:
        defaultGame = None

    for i in range(trainGames):
        currentTime = time.time()
        print("Game", str(i))
        print("(red, black reward, red, black moves)", str(
            env.playGame(printReward=False, defaultState=defaultGame))
        )
        print("took:", time.time() - currentTime, "seconds")
        print(E_TEXT[game.win] + ",", "final game board:")
        print(game.string(True))
        print("Current learn rate:", env.redEnv.internalNetwork.learnRate)
        print("Current explore rate:", env.redEnv.internalNetwork.explorationRate)
        print("Current discount rate:", env.redEnv.internalNetwork.discountRate)
        print()
        env.decayModels()

    env.trainCollective(0, printGames=True)

    game.resetGame()

    # for setting the default game with testing
    if defaultGame is not None:
        game.setBoard(defaultGame.toList(), True)

    gui = Gui(env, printFPS=False)
    gui.loop()


def testDummyGame():
    """
    Simple code used to test the execution of the DummyEnvironment with Q learning
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

    # make the model
    env = DummyGame(grid, sizeStates=True, pos=(startX, startY))

    # use the network model, or the QTable model
    network = True

    if network:
        # make the network
        net = Network(NUM_ACTIONS, env, inner=[],
                      learnRate=0.1, explorationRate=0.1, discountRate=0.5)
        # train the network
        for j in range(50):
            total = env.playGame(net, learn=True)
            print("Training: " + str(j) + ", " + str(env.x) + " " + str(env.y) + " " + str(total))

        # run the final results of the trained model
        net.explorationRate = 0
        print("Final score: " + str(env.playGame(net, learn=False, printPos=True)))

        print("Final Pos: " + str(env.x) + " " + str(env.y))
        print("Grid:")
        print(np.array([[env.rewards[g] for g in gg] for gg in grid]))

    else:
        # make the table
        qTable = Table(NUM_ACTIONS, env, learnRate=0.5, discountRate=0.7)

        # train model
        qTable.explorationRate = 1
        for j in range(100):
            env.playGame(qTable, learn=True)

        # run the model
        qTable.explorationRate = 0
        total = env.playGame(qTable, learn=False, printPos=True)
        print(str(env.x) + " " + str(env.y) + " " + str(total))
        print()

        # print the game grid and q table
        print(np.array([[env.rewards[g] for g in gg] for gg in grid]))
        print()
        print(qTable.qTable)


if checkers:
    testCheckers()
else:
    testDummyGame()
