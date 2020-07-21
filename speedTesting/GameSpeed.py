import timeit

from Checkers.DuelModel import *

game = Game(8)
# game.play((1, 5), (False, True, False))

# create the model
# env = DuelModel(game, rPieceInner=[200, 200, 200], rGameInner=[500, 500, 500],
#                 bPieceInner=[200, 200, 200], bGameInner=[500, 500, 500])


def testCode():
    """
    Put code in this method to run for a test
    """
    # game.updateMoves(0, 0, True)
    # game.updateMoves(1, 2, True)
    # game.updateMoves(2, 4, True)
    # game.updateMoves(3, 5, True)
    # game.updateMoves(1, 7, True)

    game.play((1, 5), (False, True, False))
    game.resetGame()


print(timeit.timeit(lambda: testCode(), number=500))
