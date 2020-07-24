import cProfile

from Checkers.DuelModel import *


game = Game(8)
env = DuelModel(game, rPieceInner=[200, 200, 200], rGameInner=[500, 500, 500],
                bPieceInner=[200, 200, 200], bGameInner=[500, 500, 500])
pieceModel = env.redEnv

game.play((1, 5), (True, True, False))
game.play((2, 5), (True, True, False))
game.play((2, 5), (True, True, False))
game.play((3, 5), (True, True, False))
game.play((1, 6), (True, True, False))
game.play((1, 4), (True, True, False))
pieceModel.current = (3, 5)


def testCode():

    for i in range(350):
        # pieceModel.rewardFunc(game, 7)
        newGame = game.makeCopy()
        pieceModel.oneActionReward(newGame, 7, game.redTurn)
        pieceModel.oneActionReward(newGame, None, game.redTurn)

        # game.play((1, 5), (True, True, False))
        # game.play((2, 5), (True, True, False))
        # game.play((2, 5), (True, True, False))
        # game.play((3, 5), (True, True, False))
        # game.play((1, 6), (True, True, False))
        # game.play((1, 4), (True, True, False))
        # game.play((3, 5), (True, True, True))
        # game.play((2, 3), (True, True, False))
        # game.play((2, 6), (True, True, True))
        # game.play((2, 4), (True, True, True))
        # game.play((1, 2), (False, True, False))
        # game.play((1, 7), (False, True, True))
        # game.play((2, 5), (False, True, False))
        # game.play((1, 4), (True, True, True))
        # game.play((1, 5), (False, True, False))
        # game.play((3, 6), (True, True, True))
        # game.play((2, 4), (True, True, True))
        # game.play((1, 2), (True, True, False))
        # game.play((2, 7), (False, True, True))
        # game.play((3, 5), (True, True, False))
        # game.play((0, 4), (False, True, True))
        # game.play((1, 2), (True, True, False))
        # game.play((3, 7), (True, True, True))
        # game.play((2, 5), (False, True, False))
        # game.play((1, 5), (True, True, False))
        # game.play((2, 4), (True, True, False))
        # game.play((0, 6), (False, True, False))
        # game.play((2, 3), (False, True, True))
        # game.play((3, 1), (True, True, False))
        # game.play((2, 7), (True, True, False))
        # game.play((2, 0), (True, False, True))
        # game.play((1, 2), (False, False, False))
        # game.play((2, 6), (True, True, False))
        # game.play((2, 3), (True, True, True))
        # game.play((1, 1), (False, True, False))
        # game.play((3, 7), (True, True, False))
        # game.play((1, 0), (True, False, True))
        # game.play((0, 2), (False, False, False))
        # game.play((0, 4), (False, True, False))
        # game.play((1, 3), (False, False, False))
        # game.play((1, 3), (False, True, False))
        # game.play((1, 4), (False, False, True))
        # game.play((2, 6), (False, True, False))
        # game.play((0, 5), (False, True, False))
        # game.play((3, 5), (True, True, False))
        # game.play((0, 7), (False, True, False))
        # game.play((2, 4), (False, True, True))
        # game.play((3, 2), (True, True, True))


cProfile.run("testCode()", sort=2)
