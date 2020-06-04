from unittest import TestCase

from Checkers import Game


class TestGame(TestCase):
    def test_move(self):
        pass

    def test_canMove(self):
        game = Game(8)
        game.resetGame()

        self.assertTrue(game.canMove(0, 5, False, True))
        self.assertFalse(game.canMove(0, 5, True, True))
        self.assertFalse(game.canMove(0, 5, True, False))
        self.assertFalse(game.canMove(0, 5, True, False))

        # TODO make comprehensive test cases

    def test_jump(self):
        pass

    def test_canJump(self):
        pass
