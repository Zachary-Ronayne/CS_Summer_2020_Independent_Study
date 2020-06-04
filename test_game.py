from unittest import TestCase

from Checkers import Game


class TestGame(TestCase):
    def test_canPlay(self):
        game = Game(8)
        game.resetGame()

        self.assertTrue(game.canPlay(0, 5, False, True, False))
        self.assertFalse(game.canPlay(0, 5, True, True, False))
        self.assertFalse(game.canPlay(0, 5, False, False, False))
        self.assertFalse(game.canPlay(0, 5, True, False, False))
        self.assertFalse(game.canPlay(0, 5, False, True, True))
        self.assertFalse(game.canPlay(0, 5, True, True, True))
        self.assertFalse(game.canPlay(0, 5, False, False, True))
        self.assertFalse(game.canPlay(0, 5, True, False, True))

        self.assertFalse(game.canPlay(3, 2, False, True, False))
        self.assertFalse(game.canPlay(3, 2, True, True, False))
        self.assertFalse(game.canPlay(3, 2, False, False, False))
        self.assertFalse(game.canPlay(3, 2, True, False, False))
        self.assertFalse(game.canPlay(3, 2, False, True, True))
        self.assertFalse(game.canPlay(3, 2, True, True, True))
        self.assertFalse(game.canPlay(3, 2, False, False, True))
        self.assertFalse(game.canPlay(3, 2, True, False, True))

        game.resetGame()
        game.clearBoard()
        game.spot(0, 7, (True, False), True)
        game.spot(0, 6, (False, False), True)
        self.assertTrue(game.canPlay(0, 7, False, True, True))

# TODO make comprehensive test cases
