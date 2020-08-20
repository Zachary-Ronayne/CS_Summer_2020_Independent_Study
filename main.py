
"""

TODO:

Demonstrate intelligent gameplay on 4x4 or 6x6

In Environments
    optimize oneActionReward

"""

# normal imports
from Checkers.Gui import *
from Checkers.DuelModel import *
from Checkers.PlayerTrainer import *


# center pygame window
os.environ['SDL_VIDEO_CENTERED'] = "1"

# disable GPU
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# True to run the checkers test code, False to run the DummyModel test code
checkers = True


def setRates(model):
    """
    Utility for setting hyperparameters
    """
    model.learnRate = 0.000001
    model.explorationRate = 0.2
    model.discountRate = 0.8
    model.updateOptimizerRate(0.0000001)

    model.learnDecay = 0.96
    model.explorationDecay = 0.97
    model.optimizerRateDecay = 0.96


def resetRates(env):
    """
    Utility for changing hyperparameters at a regular interval
    """
    setRates(env.redEnv.internalNetwork)
    setRates(env.redEnv.gameNetwork)
    setRates(env.blackEnv.internalNetwork)
    setRates(env.blackEnv.gameNetwork)


def testCheckers():
    """
    Simple code for playing checkers game
    """

    # for loading in or not loading in the saved version of the Networks
    loadModel = True
    # number of games to play in training
    trainGames = 400
    # number of games to randomly pick moves and learn all at once
    collectiveGames = 0
    # number for the default game to play, use None to just play a normal game
    defaultGameModel = None
    # the size od the grid to play
    gameSize = 6
    # Side to use for the player trainer, use to manually train AI by playing games
    #   True for AI plays red, False for AI plays Black
    #   Set to None to turn off
    #   When in use, AI will only play the specified side
    playerTrainerSide = False
    # reset the rates for learning and exploration every this number of games
    resetRatesInterval = 100

    # make game
    game = Game(gameSize)

    # create the model
    env = DuelModel(game, rPieceInner=[30] * 3, rGameInner=[60] * 3,
                    bPieceInner=[30] * 3, bGameInner=[60] * 3)
    resetRates(env)

    # load in the model if applicable
    if loadModel:
        env.load("", DUEL_MODEL_NAME)

    # set up a default game
    defaultGame = Game(gameSize)
    defaultGame.clearBoard()

    # determine the piece locations for the default game
    if defaultGameModel == 0:
        defaultGame.spot(1, 3, (True, False), True)
        defaultGame.spot(0, 2, (False, False), True)
    elif defaultGameModel == 1:
        defaultGame.spot(1, 3, (True, False), True)
        defaultGame.spot(0, 1, (False, False), True)
    elif defaultGameModel == 2:
        defaultGame.spot(1, 2, (True, False), True)
        defaultGame.spot(0, 3, (True, False), True)
        defaultGame.spot(0, 1, (False, False), True)
    elif defaultGameModel == 3:
        defaultGame.spot(0, 0, (False, False), False)
        defaultGame.spot(0, 0, (False, False), True)
    elif defaultGameModel == 4:
        defaultGame.spot(0, 0, (False, False), False)
        defaultGame.spot(0, 0, (False, False), True)
        defaultGame.spot(1, 0, (False, False), True)
    elif defaultGameModel == 5:
        defaultGame.spot(0, 0, (False, False), True)
        defaultGame.spot(0, 0, (False, False), False)
        defaultGame.spot(1, 0, (False, False), False)
    else:
        defaultGame = None

    # train the appropriate number of times
    for i in range(trainGames):
        currentTime = time.time()
        print("Game", str(i))
        print("(red, black reward, red, black moves)", str(
            env.playGame(printReward=False, defaultState=defaultGame))
        )
        print("took:", time.time() - currentTime, "seconds")
        print(E_TEXT[game.win], "| Final game board:")
        print(game.string(True))
        print("Current learn rate:", env.redEnv.internalNetwork.learnRate)
        print("Current explore rate:", env.redEnv.internalNetwork.explorationRate)
        print("Current discount rate:", env.redEnv.internalNetwork.discountRate)
        print()
        if i % resetRatesInterval == resetRatesInterval - 1:
            resetRates(env)
        else:
            env.decayModels()

    # train games where random moves are taken
    env.trainCollective(collectiveGames, printGames=True)

    # reset the game to the default state
    game.resetGame()

    # create the player trainer
    if playerTrainerSide is None:
        trainer = None
    else:
        trainer = PlayerTrainer(env.redEnv if playerTrainerSide else env.blackEnv, playerTrainerSide)

    # set up and begin the gui
    gui = Gui(env, printFPS=False, defaultGame=defaultGame, playerTrainer=trainer)
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
        net = Network(NUM_ACTIONS, env, inner=[10],
                      learnRate=0.1, explorationRate=0.1, discountRate=0.5)
        # train the network
        for j in range(100):
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
