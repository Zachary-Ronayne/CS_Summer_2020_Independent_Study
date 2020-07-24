import timeit

from Checkers.DuelModel import *

game = Game(4)

# create a model
# env = DuelModel(game, rPieceInner=[200, 200, 200], rGameInner=[500, 500, 500],
#                 bPieceInner=[200, 200, 200], bGameInner=[500, 500, 500])


def testCode():
    """
    Put code in this method to run for a test
    """
    game.resetGame()
    game.play((0, 3), (False, True, False))
    game.play((1, 3), (True, True, False))
    game.play((0, 2), (True, True, False))
    game.play((0, 2), (False, True, False))
    game.play((0, 1), (False, True, False))
    game.play((1, 1), (False, True, False))
    game.play((0, 0), (True, False, False))
    game.play((1, 0), (True, False, False))
    game.play((0, 1), (False, True, False))
    game.play((0, 3), (False, True, False))
    game.play((1, 3), (False, True, False))
    game.play((1, 1), (False, False, False))


print(timeit.timeit(lambda: testCode(), number=10000))
