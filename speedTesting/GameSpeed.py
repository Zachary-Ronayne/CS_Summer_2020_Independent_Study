import timeit

from Checkers.Environments import *

game = Game(8)
game.play((1, 5), (False, True, False))

env = PieceEnvironment(game)


def testCode():
    """
    Put code in this method to run for a test
    """
    # game.resetGame()
    # game.play((1, 5), (False, True, False))

    # game.makeCopy().string(True)

    env.trainMove()


print(timeit.timeit(lambda: testCode(), number=20))
