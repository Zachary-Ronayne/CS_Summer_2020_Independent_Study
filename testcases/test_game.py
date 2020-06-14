from unittest import TestCase

from Checkers.Environments import *


class TestGame(TestCase):

    def test_makeCopy(self):
        # create a Game object
        game = Game(8)
        # make a move in the Game to ensure the copy will also have those moves
        game.play((1, 2), (True, True, False))
        # make a copy
        copy = game.makeCopy()

        # make sure the Games are not the same
        self.assertNotEqual(game, copy)

        # test that each field in the Game is the same
        self.assertEqual(game.width, copy.width)
        self.assertEqual(game.height, copy.height)
        self.assertEqual(game.redTurn, copy.redTurn)
        self.assertEqual(game.redLeft, copy.redLeft)
        self.assertEqual(game.blackLeft, copy.blackLeft)
        self.assertEqual(game.win, copy.win)
        self.assertEqual(game.movesSinceLastCapture, copy.movesSinceLastCapture)
        self.assertEqual(game.moves, copy.moves)

        # test that both grids are the same
        for gRedRow, cRedRow, gBlackRow, cBlackRow in zip(game.redGrid, copy.redGrid, game.blackGrid, copy.blackGrid):
            for gRedCol, cRedCol, gBlackCol, cBlackCol in zip(gRedRow, cRedRow, gBlackRow, cBlackRow):
                self.assertEqual(gRedCol, cRedCol)
                self.assertEqual(gBlackCol, cBlackCol)

    def test_resetGame(self):
        # create a Game object and reset it
        game = Game(8)
        game.resetGame()

        # ensure the Game is in a default state

        # check all fields are as expected
        self.assertEqual(game.width, 4)
        self.assertEqual(game.height, 8)
        self.assertEqual(game.redLeft, 12)
        self.assertEqual(game.blackLeft, 12)
        self.assertEqual(game.win, E_PLAYING)
        self.assertEqual(game.moves, 0)
        self.assertEqual(game.movesSinceLastCapture, 0)

        # check that the grids are in a default state
        red = game.redGrid
        black = game.blackGrid
        for i in range(4):
            for j in range(3):
                self.assertEqual(red[j][i], (False, False))
                self.assertEqual(black[j][i], (False, False))
                self.assertEqual(red[7 - j][i], (True, False))
                self.assertEqual(black[7 - j][i], (True, False))
            for j in range(2):
                self.assertEqual(red[j + 3][i], None)
                self.assertEqual(black[j + 3][i], None)

    def test_clearBoard(self):
        # create a Game and clear the board
        game = Game(8)
        game.clearBoard()

        # check that there are no more pieces
        self.assertEqual(game.redLeft, 0)
        self.assertEqual(game.blackLeft, 0)

        # check that the board is empty
        red = game.redGrid
        black = game.blackGrid
        for i in range(4):
            for j in range(8):
                self.assertEqual(red[j][i], None)

                self.assertEqual(black[j][i], None)

    def test_setBoard(self):
        # create a Game and clear the board, and set some pieces
        game = Game(8)
        game.clearBoard()
        game.setBoard((
            None, (True, True), None, None,
            (False, True), None, (True, False)),
            True)

        # check that each piece was placed correctly
        red = game.redGrid
        self.assertEqual(red[0][0], None)
        self.assertEqual(red[0][1], (True, True))
        self.assertEqual(red[0][2], None)
        self.assertEqual(red[0][3], None)
        self.assertEqual(red[1][0], (False, True))
        self.assertEqual(red[1][1], None)
        self.assertEqual(red[1][2], (True, False))

    def test_toList(self):
        # create Game and set pieces
        game = Game(4)
        game.clearBoard()
        game.spot(0, 0, (True, True), True)
        game.spot(0, 1, (False, True), True)
        game.spot(1, 1, (False, False), True)
        game.spot(1, 3, (True, False), True)

        # verify that toList returns the expected list
        expected = [
            (True, True), None,
            (False, True), (False, False),
            None, None,
            None, (True, False)
        ]
        actual = game.toList()
        self.assertEqual(expected, actual)

    def test_singlePos(self):
        # create a Game
        game = Game(6)

        # verify that its dimensions work
        self.assertEqual(game.singlePos(0), (0, 0))
        self.assertEqual(game.singlePos(2), (2, 0))
        self.assertEqual(game.singlePos(3), (0, 1))
        self.assertEqual(game.singlePos(7), (1, 2))

    def test_oppositeGrid(self):
        # create a Game
        game = Game(8)

        # ensure the opposite grid returns correct coordinates
        self.assertTrue(game.oppositeGrid((0, 0)), (3, 7))
        self.assertTrue(game.oppositeGrid((0, 2)), (3, 5))
        self.assertTrue(game.oppositeGrid((3, 2)), (0, 5))
        self.assertTrue(game.oppositeGrid((1, 4)), (2, 3))

    def test_currentGrid(self):
        # create a Game
        game = Game(6)

        # ensure that the correct grid is returned
        game.redTurn = True
        self.assertEqual(game.redGrid, game.currentGrid())
        game.redTurn = False
        self.assertEqual(game.blackGrid, game.currentGrid())

    def test_area(self):
        # verify the area of various game boards
        self.assertEqual(Game(2).area(), 2)
        self.assertEqual(Game(4).area(), 8)
        self.assertEqual(Game(6).area(), 18)
        self.assertEqual(Game(8).area(), 32)

    def test_spot(self):
        # create a Game and clear the board
        game = Game(8)
        game.clearBoard()

        # place pieces, and verify they are placed, and that the piece counts are updated

        # place a red piece
        game.spot(0, 0, (True, False), True)
        self.assertEqual(game.redGrid[0][0], (True, False))
        self.assertEqual(game.blackGrid[7][3], (False, False))
        self.assertEqual(game.redLeft, 1)
        self.assertEqual(game.blackLeft, 0)

        # place a black piece
        game.spot(2, 4, (True, False), False)
        self.assertEqual(game.redGrid[3][1], (False, False))
        self.assertEqual(game.blackGrid[4][2], (True, False))
        self.assertEqual(game.redLeft, 1)
        self.assertEqual(game.blackLeft, 1)

        # replace the red piece with a black piece
        game.spot(3, 7, (True, False), False)
        self.assertEqual(game.redGrid[0][0], (False, False))
        self.assertEqual(game.blackGrid[7][3], (True, False))
        self.assertEqual(game.redLeft, 0)
        self.assertEqual(game.blackLeft, 2)

        # remove one of the black pieces
        game.spot(2, 4, None, False)
        self.assertEqual(game.redGrid[3][1], None)
        self.assertEqual(game.blackGrid[4][2], None)
        self.assertEqual(game.redLeft, 0)
        self.assertEqual(game.blackLeft, 1)

    def test_gridPos(self):
        # create a Game
        game = Game(8)

        # verify locations of default squares
        self.assertEqual(game.gridPos(0, 0, True), (False, False))
        self.assertEqual(game.gridPos(0, 7, True), (True, False))
        self.assertEqual(game.gridPos(0, 0, False), (False, False))
        self.assertEqual(game.gridPos(0, 7, False), (True, False))
        self.assertEqual(game.gridPos(2, 4, True), None)
        self.assertEqual(game.gridPos(2, 4, False), None)

    def test_play(self):
        # create a Game
        game = Game(8)

        # make a move, red piece on far left forward
        game.play((0, 5), (False, True, False))
        # verify the piece moved
        self.assertFalse(game.redTurn)
        self.assertEqual(game.gridPos(0, 5, True), None)
        self.assertEqual(game.gridPos(0, 4, True), (True, False))

        # make a move, black piece to match the red piece, allowing the red piece to jump
        game.play((2, 5), (False, True, False))
        # verify the piece moved
        self.assertTrue(game.redTurn)
        self.assertEqual(game.gridPos(2, 5, False), None)
        self.assertEqual(game.gridPos(2, 4, False), (True, False))

        # jump over the red piece with the black piece
        game.play((0, 4), (False, True, True))
        # verify the piece moved, it should still be red's turn
        self.assertTrue(game.redTurn)
        self.assertEqual(game.gridPos(0, 4, True), None)
        self.assertEqual(game.gridPos(1, 3, True), None)
        self.assertEqual(game.gridPos(1, 2, True), (True, False))

    def test_canPlay(self):
        # create a Game
        game = Game(8)

        # testing moving on all basic directions for normal pieces
        game.resetGame()
        self.assertTrue(game.canPlay((0, 5), (False, True, False)))
        self.assertFalse(game.canPlay((0, 5), (True, True, False)))
        self.assertFalse(game.canPlay((0, 5), (False, False, False)))
        self.assertFalse(game.canPlay((0, 5), (True, False, False)))
        self.assertFalse(game.canPlay((0, 5), (False, True, True)))
        self.assertFalse(game.canPlay((0, 5), (True, True, True)))
        self.assertFalse(game.canPlay((0, 5), (False, False, True)))
        self.assertFalse(game.canPlay((0, 5), (True, False, True)))

        self.assertFalse(game.canPlay((3, 2), (False, True, False)))
        self.assertFalse(game.canPlay((3, 2), (True, True, False)))
        self.assertFalse(game.canPlay((3, 2), (False, False, False)))
        self.assertFalse(game.canPlay((3, 2), (True, False, False)))
        self.assertFalse(game.canPlay((3, 2), (False, True, True)))
        self.assertFalse(game.canPlay((3, 2), (True, True, True)))
        self.assertFalse(game.canPlay((3, 2), (False, False, True)))
        self.assertFalse(game.canPlay((3, 2), (True, False, True)))

        # testing jumping with normal pieces
        game.resetGame()
        game.clearBoard()
        game.spot(0, 7, (True, False), True)
        game.spot(0, 6, (False, False), True)
        self.assertTrue(game.canPlay((0, 7), (False, True, True)))
        game.spot(0, 6, (True, False), True)
        self.assertFalse(game.canPlay((0, 7), (False, True, True)))
        game.spot(0, 6, None, True)
        self.assertFalse(game.canPlay((0, 7), (False, True, True)))

        # testing jumping with king pieces
        game.resetGame()
        game.clearBoard()
        game.spot(1, 5, (True, True), True)
        game.spot(0, 6, (False, False), True)
        self.assertTrue(game.canPlay((1, 5), (True, False, True)))
        game.spot(0, 6, (True, False), True)
        self.assertFalse(game.canPlay((1, 5), (True, False, True)))
        game.spot(0, 6, None, True)
        self.assertFalse(game.canPlay((1, 5), (True, False, True)))

        game.resetGame()
        game.clearBoard()
        game.spot(1, 5, (True, False), True)
        game.spot(0, 6, (False, False), True)
        self.assertFalse(game.canPlay((1, 5), (True, False, True)))
        game.spot(0, 6, (True, False), True)
        self.assertFalse(game.canPlay((1, 5), (True, False, True)))
        game.spot(0, 6, None, True)
        self.assertFalse(game.canPlay((1, 5), (True, False, True)))

    def test_checkWinConditions(self):
        # create a Game
        game = Game(8)

        # test red wins with one red piece and nothing else
        game.resetGame()
        game.clearBoard()
        game.spot(0, 0, (True, True), True)
        game.checkWinConditions()
        self.assertEqual(game.win, E_RED_WIN)

        # test black wins with one black piece and nothing else
        game.resetGame()
        game.clearBoard()
        game.spot(0, 0, (True, True), False)
        game.checkWinConditions()
        self.assertEqual(game.win, E_BLACK_WIN)

        # test game is not over with red and black both having a piece
        game.resetGame()
        game.clearBoard()
        game.spot(1, 1, (True, True), True)
        game.spot(1, 1, (True, True), False)
        game.checkWinConditions()
        self.assertEqual(game.win, E_PLAYING)

        # test game is a draw with no one having any moves
        game.resetGame()
        game.clearBoard()
        game.spot(0, 0, (True, False), True)
        game.spot(0, 0, (True, False), False)
        game.checkWinConditions()
        self.assertEqual(game.win, E_DRAW)

        # test game is a draw, it is red's turn and red has no moves,
        #   but both red and black have pieces
        game.resetGame()
        game.clearBoard()
        game.redTurn = True
        game.spot(0, 1, (True, False), True)
        game.spot(0, 0, (False, False), True)
        game.checkWinConditions()
        self.assertEqual(game.win, E_DRAW)

        # test game is a draw, it is black's turn and black has no moves,
        #   but both red and black have pieces
        game.resetGame()
        game.clearBoard()
        game.redTurn = False
        game.spot(0, 1, (True, False), False)
        game.spot(0, 0, (False, False), False)
        game.checkWinConditions()
        self.assertEqual(game.win, E_DRAW)

        # test the game is a draw with too many moves since last capture
        game.resetGame()
        game.movesSinceLastCapture = E_MAX_MOVES_WITHOUT_CAPTURE
        game.checkWinConditions()
        self.assertEqual(game.win, E_DRAW)

    def test_calculateMoves(self):
        # create a Game
        game = Game(8)

        # test finding moves for a default piece
        moves = game.calculateMoves((0, 5))
        self.assertTrue((0, 4) in moves)
        moves.remove((0, 4))
        for i in range(7):
            self.assertEqual(moves[i], None)

        # test finding moves for an empty square
        moves = game.calculateMoves((0, 4))
        for i in range(8):
            self.assertEqual(moves[i], None)

        # test finding moves for a normal piece to jump on empty board
        game.clearBoard()
        game.spot(1, 2, (True, False), True)
        game.spot(2, 1, (False, False), True)
        moves = game.calculateMoves((1, 2))
        self.assertTrue((2, 0) in moves)
        moves.remove((2, 0))
        self.assertTrue((1, 1) in moves)
        moves.remove((1, 1))
        for i in range(6):
            self.assertEqual(moves[i], None)

        # test finding moves for a king on empty board
        game.clearBoard()
        game.spot(1, 2, (True, True), True)
        moves = game.calculateMoves((1, 2))
        self.assertTrue((1, 1) in moves)
        moves.remove((1, 1))
        self.assertTrue((2, 1) in moves)
        moves.remove((2, 1))
        self.assertTrue((1, 3) in moves)
        moves.remove((1, 3))
        self.assertTrue((2, 3) in moves)
        moves.remove((2, 3))
        for i in range(4):
            self.assertEqual(moves[i], None)

        # test finding moves for a king on empty board in a corner
        game.clearBoard()
        game.spot(0, 0, (True, True), True)
        moves = game.calculateMoves((0, 0))
        self.assertTrue((1, 1) in moves)
        moves.remove((1, 1))
        self.assertTrue((0, 1) in moves)
        moves.remove((0, 1))
        for i in range(6):
            self.assertEqual(moves[i], None)

        # test finding moves for a king to jump on empty board
        game.clearBoard()
        game.spot(1, 2, (True, True), True)
        game.spot(1, 1, (False, False), True)
        game.spot(1, 3, (False, False), True)
        moves = game.calculateMoves((1, 2))
        self.assertTrue((0, 0) in moves)
        moves.remove((0, 0))
        self.assertTrue((0, 4) in moves)
        moves.remove((0, 4))
        self.assertTrue((2, 1) in moves)
        moves.remove((2, 1))
        self.assertTrue((2, 3) in moves)
        moves.remove((2, 3))
        for i in range(4):
            self.assertEqual(moves[i], None)

    def test_canMovePos(self):
        # create a Game
        game = Game(8)

        # test ally piece can move, can't move empty square, can't move locked ally, can't move enemy
        self.assertTrue(game.canMovePos((0, 5)))
        self.assertFalse(game.canMovePos((0, 4)))
        self.assertFalse(game.canMovePos((0, 6)))
        self.assertFalse(game.canMovePos((0, 2)))

        # test kings being able to move backwards, and normal pieces can't
        game.clearBoard()
        game.spot(0, 0, (True, True), True)
        self.assertTrue(game.canMovePos((0, 0)))
        game.spot(0, 0, (True, False), True)
        self.assertFalse(game.canMovePos((0, 0)))

    def test_validPiece(self):
        # create a Game
        game = Game(8)

        # test empty square is invalid
        self.assertFalse(game.validPiece(0, 4, True))

        # test ally piece is valid
        self.assertTrue(game.validPiece(0, 5, True))
        self.assertTrue(game.validPiece(0, 6, True))

        # test enemy piece is invalid
        self.assertFalse(game.validPiece(0, 1, True))
        self.assertFalse(game.validPiece(0, 2, True))

        # test king can move backwards, normal can't
        self.assertFalse(game.validPiece(0, 5, False))
        game.spot(0, 5, (True, True), True)
        self.assertTrue(game.validPiece(0, 5, False))

    def test_inRange(self):
        # create a Game
        game = Game(8)

        # verify coordinates
        self.assertTrue(game.inRange(0, 0))
        self.assertTrue(game.inRange(3, 7))
        self.assertTrue(game.inRange(2, 4))

        self.assertFalse(game.inRange(-1, 0))
        self.assertFalse(game.inRange(0, -1))
        self.assertFalse(game.inRange(4, 0))
        self.assertFalse(game.inRange(0, 8))

    def test_movePos(self):
        # verify moving from even squares to odd squares
        # move
        # forward
        self.assertEqual(movePos((0, 6), (True, True, False)), (0, 5))
        self.assertEqual(movePos((0, 6), (False, True, False)), (1, 5))
        # backwards
        self.assertEqual(movePos((0, 6), (True, False, False)), (0, 7))
        self.assertEqual(movePos((0, 6), (False, False, False)), (1, 7))
        # jump
        # forward
        self.assertEqual(movePos((0, 6), (True, True, True)), (-1, 4))
        self.assertEqual(movePos((0, 6), (False, True, True)), (1, 4))
        # backwards
        self.assertEqual(movePos((0, 6), (True, False, True)), (-1, 8))
        self.assertEqual(movePos((0, 6), (False, False, True)), (1, 8))

        # verify moving from odd squares to even squares
        # move
        # forward
        self.assertEqual(movePos((1, 5), (True, True, False)), (0, 4))
        self.assertEqual(movePos((1, 5), (False, True, False)), (1, 4))
        # backwards
        self.assertEqual(movePos((1, 5), (True, False, False)), (0, 6))
        self.assertEqual(movePos((1, 5), (False, False, False)), (1, 6))
        # jump
        # forward
        self.assertEqual(movePos((1, 5), (True, True, True)), (0, 3))
        self.assertEqual(movePos((1, 5), (False, True, True)), (2, 3))
        # backwards
        self.assertEqual(movePos((1, 5), (True, False, True)), (0, 7))
        self.assertEqual(movePos((1, 5), (False, False, True)), (2, 7))

    def test_moveIntToBoolList(self):
        # verify each number
        self.assertEqual(moveIntToBoolList(0), [False, False, False])
        self.assertEqual(moveIntToBoolList(1), [False, False, True])
        self.assertEqual(moveIntToBoolList(2), [False, True, False])
        self.assertEqual(moveIntToBoolList(3), [False, True, True])
        self.assertEqual(moveIntToBoolList(4), [True, False, False])
        self.assertEqual(moveIntToBoolList(5), [True, False, True])
        self.assertEqual(moveIntToBoolList(6), [True, True, False])
        self.assertEqual(moveIntToBoolList(7), [True, True, True])
