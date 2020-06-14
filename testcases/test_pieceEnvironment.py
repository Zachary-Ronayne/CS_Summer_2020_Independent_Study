from unittest import TestCase

from Checkers.Environments import *


class TestPieceEnvironment(TestCase):

    def test_networkInputs(self):
        pass

    def test_toNetInput(self):
        pass

    def test_currentState(self):
        pass

    def test_numStates(self):
        pass

    def test_rewardFunc(self):
        # TODO
        pass

    def test_moveReward(self):
        # create a Game and environment
        game = Game(4)
        env = PieceEnvironment(game)

        # test ally moving normally
        game.clearBoard()
        game.redTurn = True
        game.spot(0, 3, (True, False), True)
        state = game.toList()
        self.assertEqual(env.moveReward(state, (0, 3), [False, True, False]), Q_PIECE_REWARD_MOVE)

        # test enemy moving normally
        game.clearBoard()
        game.redTurn = False
        game.spot(0, 3, (False, False), False)
        state = game.toList()
        self.assertEqual(env.moveReward(state, (0, 3), [False, True, False]), Q_PIECE_REWARD_ENEMY_MOVE)

        # test ally capturing normal piece, then king
        game.clearBoard()
        game.redTurn = True
        game.spot(0, 3, (True, False), True)
        game.spot(0, 2, (False, False), True)
        state = game.toList()
        self.assertEqual(env.moveReward(state, (0, 3), [False, True, True]), Q_PIECE_REWARD_N_CAPTURE)

        game.spot(0, 2, (False, True), True)
        state = game.toList()
        self.assertEqual(env.moveReward(state, (0, 3), [False, True, True]), Q_PIECE_REWARD_K_CAPTURE)

        # test enemy capturing normal piece, then king
        game.clearBoard()
        game.redTurn = False
        game.spot(0, 3, (False, False), False)
        game.spot(0, 2, (True, False), False)
        state = game.toList()
        self.assertEqual(env.moveReward(state, (0, 3), [False, True, True]), Q_PIECE_REWARD_N_CAPTURED)

        game.spot(0, 2, (True, True), False)
        state = game.toList()
        self.assertEqual(env.moveReward(state, (0, 3), [False, True, True]), Q_PIECE_REWARD_K_CAPTURED)

        # test reward for ally getting a king, then test that if they are already a king, they don't get extra reward
        game.clearBoard()
        game.redTurn = True
        game.spot(0, 1, (True, False), True)
        state = game.toList()
        self.assertEqual(env.moveReward(state, (0, 1), [False, True, False]), Q_PIECE_REWARD_KING + Q_PIECE_REWARD_MOVE)

        game.spot(0, 1, (True, True), True)
        state = game.toList()
        self.assertEqual(env.moveReward(state, (0, 1), [False, True, False]), Q_PIECE_REWARD_MOVE)

        # test reward for enemy getting a king, then test that if they are already a king, they don't get extra reward
        game.clearBoard()
        game.redTurn = False
        game.spot(0, 1, (False, False), False)
        state = game.toList()
        self.assertEqual(env.moveReward(state, (0, 1), [False, True, False]),
                         Q_PIECE_REWARD_KINGED + Q_PIECE_REWARD_ENEMY_MOVE)

        game.spot(0, 1, (False, True), False)
        state = game.toList()
        self.assertEqual(env.moveReward(state, (0, 1), [False, True, False]), Q_PIECE_REWARD_ENEMY_MOVE)

    def test_stateToPiece(self):
        # TODO
        pass

    def test_canTakeAction(self):
        pass

    def test_takeAction(self):
        # TODO
        pass

    def test_performAction(self):
        # TODO
        pass

    def test_trainMove(self):
        # TODO
        pass

    def test_playGame(self):
        # TODO
        pass

    def test_saveNetworks(self):
        # TODO
        pass

    def test_loadNetworks(self):
        # TODO
        pass

    def test_endGameReward(self):
        # create a Game and environment
        game = Game(4)
        env = PieceEnvironment(game)

        # test game is not over
        game.resetGame()
        self.assertEqual(endGameReward(game.win, True, 0), Q_PIECE_REWARD_PLAYING)

        # test a draw has happened

        # test red has won

        # test red has lost

        # test black has won

        # test black has lost

        # test game is over with varying amounts of moves

        # TODO
