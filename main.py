
"""

TODO:

Make test cases

Find new source of slow speed in network code, probably the training and set up time
Try adding adaptive learning rate and discount rate
Try using convolutional layers

"""

# hide warnings
import os
# TODO hide warnings again?
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
"""
2020-06-11 11:36:09.516806: W tensorflow/stream_executor/platform/default/dso_loader.cc:55] Could not load dynamic library 'cudart64_101.dll'; dlerror: cudart64_101.dll not found
2020-06-11 11:36:09.517508: I tensorflow/stream_executor/cuda/cudart_stub.cc:29] Ignore above cudart dlerror if you do not have a GPU set up on your machine.
2020-06-11 11:36:13.923133: W tensorflow/stream_executor/platform/default/dso_loader.cc:55] Could not load dynamic library 'nvcuda.dll'; dlerror: nvcuda.dll not found
2020-06-11 11:36:13.923260: E tensorflow/stream_executor/cuda/cuda_driver.cc:313] failed call to cuInit: UNKNOWN ERROR (303)
2020-06-11 11:36:13.927083: I tensorflow/stream_executor/cuda/cuda_diagnostics.cc:169] retrieving CUDA diagnostic information for host: DESKTOP-AGIR9UI
2020-06-11 11:36:13.927254: I tensorflow/stream_executor/cuda/cuda_diagnostics.cc:176] hostname: DESKTOP-AGIR9UI
2020-06-11 11:36:13.930923: I tensorflow/core/platform/cpu_feature_guard.cc:143] Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2
2020-06-11 11:36:13.965047: I tensorflow/compiler/xla/service/service.cc:168] XLA service 0x2ce45804a70 initialized for platform Host (this does not guarantee that XLA will be used). Devices:
2020-06-11 11:36:13.965201: I tensorflow/compiler/xla/service/service.cc:176]   StreamExecutor device (0): Host, Default Version
"""

# normal imports
from Checkers.Gui import *
from Checkers.Environments import *

# center pygame window
os.environ['SDL_VIDEO_CENTERED'] = "1"


# for loading in or not loading in the saved version of the Networks
loadModel = True

# make game
game = Game(8)

pEnv = PieceEnvironment(game, current=None)
model = pEnv.internalNetwork
model.learnRate = 0.1
model.explorationRate = 0.1
model.discountRate = 0.5

gameModel = pEnv.gameNetwork
gameModel.learnRate = 0.1
gameModel.explorationRate = 0.1
gameModel.discountRate = 0.5

if loadModel:
    pEnv.loadNetworks(PIECE_NETWORK_NAME, GAME_NETWORK_NAME)

for i in range(100):
    currentTime = time.time()
    print("Game: " + str(i))
    print("Reward and total moves" + str(pEnv.playGame(printReward=False)))
    print("took:", time.time() - currentTime, "seconds")

game.resetGame()

gui = Gui(pEnv, printFPS=False)
gui.loop()


# create a grid
"""
gridUse = 2

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
    for i in range(1000):
        total = model.playGame(qTable, learn=True)

    # run the model
    qTable.explorationRate = 0
    total = model.playGame(qTable, learn=False, printPos=True)
    print(str(model.x) + " " + str(model.y) + " " + str(total))
    print()

    # print the game grid and q table
    print(np.array([[model.rewards[g] for g in gg] for gg in grid]))
    print()
    print(qTable.qTable)
"""