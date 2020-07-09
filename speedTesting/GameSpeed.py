import timeit

from Checkers.Game import *

game = Game(8)
game.play((1, 5), (False, True, False))


def testCode():
    """
    Put code in this method to run for a test
    """
    game.resetGame()
    game.play((1, 5), (False, True, False))

    # game.makeCopy().string(True)


print(timeit.timeit(lambda: testCode(), number=1000))
