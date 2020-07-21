import cProfile

from Checkers.DuelModel import *


def testCode():
    game = Game(8)
    # env = DuelModel(game, rPieceInner=[200, 200, 200], rGameInner=[500, 500, 500],
    #                 bPieceInner=[200, 200, 200], bGameInner=[500, 500, 500])

    for i in range(1000):
        # game.spot(0, 0, None, True)
        # game.spot(1, 2, (True, False), True)
        # game.spot(1, 2, (False, False), True)
        # game.spot(2, 2, (True, False), True)
        # game.spot(2, 2, (False, False), True)
        # game.spot(1, 5, (True, False), True)
        # game.spot(1, 5, (False, False), True)
        # game.spot(2, 5, (True, False), True)
        # game.spot(2, 5, (False, False), True)

        game.play((1, 5), (False, True, False))
        game.resetGame()


cProfile.run("testCode()")
