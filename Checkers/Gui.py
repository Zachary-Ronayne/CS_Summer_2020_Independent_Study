from Checkers.Game import *
from Constants import *

if USE_PY_GAME:
    import pygame

import time

# technical constants
ENABLE_LOOP_WAIT = False

E_RED_PLAYING = "Red's Turn"
E_BLACK_PLAYING = "Black's Turn"
E_TEXT_COLOR = (0, 0, 0)
E_GAME_STATE_X = 10
E_GAME_STATE_Y = 10

# constants for drawing the game
DR_SQUARE_SIZE = 80
DR_BORDER_SIZE = 20
DR_GAME_BORDER_SIZE = 5
DR_TOP_SPACE = 140
DR_GRID_X = DR_BORDER_SIZE + DR_GAME_BORDER_SIZE
DR_GRID_Y = DR_BORDER_SIZE + DR_TOP_SPACE + DR_GAME_BORDER_SIZE
DR_PIECE_SIZE = 70
DR_PIECE_BORDER = 3
DR_FONT_SIZE = 50
DR_FONT_FACE = "Arial"

# constants for instruction text at the top
I_FONT_SIZE = 17
I_UP_LEFT_X = 10
I_UP_LEFT_Y = 60
I_LINE_SPACING = 19
I_TEXT = [
    "R: reset game",
    "A: make AI move",
    "T: make AI move and train",
    "S: save the current state of the model",
    "ESC: close game"
]
I_TEXT_COLOR = (0, 0, 0)

# color constants
C_ON_SQUARE = (220, 220, 220)
C_OFF_SQUARE = (40, 40, 40)
C_BACKGROUND = (180, 180, 180)
C_GAME_BORDER = (0, 0, 0)
C_RED_PIECE = (200, 0, 0)
C_BLACK_PIECE = (20, 20, 20)
C_RED_KING = (30, 0, 0)
C_BLACK_KING = (170, 160, 160)
C_PIECE_BORDER = (0, 0, 0)
C_SELECTED_HIGHLIGHT = (0, 0, 200, 140)
C_HOVER_HIGHLIGHT = (0, 0, 230, 50)
C_MOVE_HIGHLIGHT = (0, 200, 0, 127)
C_CAPTURE_HIGHLIGHT = (200, 0, 0, 127)


class Gui:
    """
    A class that handles displaying and taking input for playing a Checkers Game in a GUI with pygame
    """

    def __init__(self, qObject, fps=20, printFPS=False):
        """
        Create and display the pygame Gui with the given game.
        Must call loop() to make the Gui stay open
        :param qObject: The PieceEnvironment object to use for making an AI move, the Game object also comes from here
        :param fps: The capped frame rate of the Gui, default 20
        :param printFPS: True to print the frames per second, every second, False otherwise, default False
        """
        self.qEnv = qObject
        self.game = qObject.game

        # setup pygame
        pygame.init()
        pygame.font.init()

        # create the gui object
        self.gridWidth = self.game.height * DR_SQUARE_SIZE
        self.gridHeight = self.game.height * DR_SQUARE_SIZE
        self.pixelWidth = (DR_BORDER_SIZE + DR_GAME_BORDER_SIZE) * 2 + self.gridWidth
        self.pixelHeight = (DR_BORDER_SIZE + DR_GAME_BORDER_SIZE) * 2 + self.gridHeight + DR_TOP_SPACE
        self.gui = pygame.display.set_mode((self.pixelWidth, self.pixelHeight))
        pygame.display.set_caption("Checkers")

        # variables for tracking the clock that runs the game
        self.running = True
        self.fps = fps
        self.printFPS = printFPS

        # variables for drawing text
        self.font = makeFont(DR_FONT_FACE, DR_FONT_SIZE)
        self.font.set_bold(True)

        # variables for tracking mouse input
        self.hoverSquare = None
        self.selectedSquare = None

        # playMoves should be either None, or a list of exactly 8 elements
        #   each element is None, or a 2-tuple of the grid coordinates to where the selected piece can move
        self.playMoves = None

        # captureMoves should either be None, or a list of up to 4 elements
        #   each element is None, or a 2-tuple of the grid coordinates where a piece can be captured
        self.captureMoves = None

    def loop(self):
        """
        A method that handles updating the state of the game
        """
        lastTime = time.time()
        lastFrame = time.time()
        frames = 0
        while self.running:
            frameTime = 1 / self.fps
            self.handleEvents()

            currTime = time.time()
            if currTime - lastFrame > frameTime:
                frames += 1
                lastFrame = time.time()
                self.redrawPygame()
            elif ENABLE_LOOP_WAIT:
                # wait a bit of time to prevent the loop from running unnecessarily long amounts of time
                time.sleep(0.01)

            currTime = time.time()
            if currTime - lastTime > 1:
                if self.printFPS:
                    print("FPS: " + str(frames))
                frames = 0
                lastTime = currTime

    def handleEvents(self):
        """
        A method that handles events that happen each loop of the pygame window
        """
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.MOUSEMOTION:
                self.handleMouseMove()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                self.handleMouseUp()
            elif e.type == pygame.KEYUP:
                self.handleKeyUp(e)

    def handleMouseMove(self):
        """
        This method is run every time pygame detects a mouse movement
        """

        # only select a square to hover over while the game is not over
        if self.game.win == E_PLAYING:
            mPos = pygame.mouse.get_pos()
            gPos = self.mouseToGrid(mPos[0], mPos[1])
            # only set the hover piece if the square under the mouse is a playable square
            if gPos is not None:
                # only set hover if that square contains a player whose turn it is
                square = self.game.gridPos(gPos[0], gPos[1], True)
                if square is not None and square[0] == self.game.redTurn:
                    self.hoverSquare = gPos
            else:
                self.hoverSquare = None

    def handleMouseUp(self):
        """
        This method is run every time pygame detects a mouse button up
        """
        # if there is not a selected square, then select the hovered square
        if self.selectedSquare is None:
            self.selectSquare()
            if self.selectedSquare is not None:
                self.calculateMoves(self.selectedSquare)
        # if the is a selected square, multiple things can happen
        else:
            # if the hover square is nothing, then unselect the square
            # can only move to places where the hover square is not finding a piece
            if self.hoverSquare is None:
                # TODO may want to move some of this code
                # select the move to play, based on the mouse location
                if self.playMoves is not None and self.selectedSquare is not None:
                    # find the square in the grid, based on the mouse position
                    mPos = pygame.mouse.get_pos()
                    gPos = self.mouseToGrid(mPos[0], mPos[1])
                    # if the square is on the grid, see if a move exists there
                    if gPos is not None:
                        # iterate through all possible moves
                        for i, p in enumerate(self.playMoves):
                            if p is not None:
                                # determine the directions of moving
                                bins = moveIntToBoolList(i)

                                # if the turn is in the opposite direction from red's perspective,
                                #   then the square must be reversed to get black's perspective
                                s = self.selectedSquare
                                if not self.game.redTurn:
                                    s = self.game.oppositeGrid(s)
                                # make the move the square it matches the one from the mouse
                                if gPos == p:
                                    self.game.play(s, bins)

                self.unselectSquare()
            # if there is a hovered square, select that square, and calculate the moves the square can use
            else:
                self.selectSquare()
                if self.selectedSquare is not None:
                    self.calculateMoves(self.selectedSquare)

    def handleKeyUp(self, event):
        """
        This method is run every time pygame detects a key on the keyboard has been released
        :param event: The pygame event object from the keypress
        """
        k = event.key
        if k == pygame.K_r:
            self.game.resetGame()
            self.unselectSquare()
        elif k == pygame.K_ESCAPE:
            self.running = False
        elif k == pygame.K_a:
            if self.makeQModelMove():
                self.unselectSquare()
        elif k == pygame.K_t:
            if self.makeQModelMove(True):
                self.unselectSquare()
        elif k == pygame.K_s:
            # TODO should add some kind of notification on the screen for successful or failed save
            self.qEnv.saveNetworks(PIECE_NETWORK_NAME, GAME_NETWORK_NAME)

    def makeQModelMove(self, train=False):
        """
        Make the next move in the game with the current QModel. Does nothing if that QModel is None
        :param train: True to also train the network with this move, False otherwise, default False
        :return True if a move was successfully made, False otherwise
        """
        model = self.qEnv.internalNetwork
        if model is None or self.qEnv is None:
            return False

        if train:
            self.qEnv.trainMove()
        else:
            self.qEnv.performAction(model)

        return True

    def unselectSquare(self):
        """
        Takes the current square and sets it as no longer selected
        """
        self.selectedSquare = None
        self.playMoves = None
        self.captureMoves = None

    def selectSquare(self):
        """
        Set the selected square to the hover square
        """
        if self.game.win == E_PLAYING:
            self.selectedSquare = self.hoverSquare

    def calculateMoves(self, s):
        """
        Given the grid coordinates of a square, determine the list of moves that can be played by that piece.
        The result is stored in playMoves
        :param s: The coordinates of a square
        """
        # find the playable moves
        self.playMoves = []

        # if the turn is in the opposite direction from red's perspective,
        #   then the square must be reversed to get black's perspective
        s = s if self.game.redTurn else self.game.oppositeGrid(s)

        moves = self.game.calculateMoves(s)
        # need to switch the moves around to be from the red perspective if it is black's turn
        for m in moves:
            if m is None or self.game.redTurn:
                self.playMoves.append(m)
            else:
                self.playMoves.append(self.game.oppositeGrid(m))

        # find the squares that have pieces which can be captured
        self.captureMoves = []
        # only consider the jumping moves, which is every odd index
        for m in range(1, 8, 2):
            # if the move exists, then find the square between the move and the piece position
            move = self.playMoves[m]
            if move is not None:
                # if it is not red's turn, the piece needs to be inverted
                origin = s if self.game.redTurn else self.game.oppositeGrid(s)
                xOffset = 0 if move[1] % 2 == 1 else 1
                self.captureMoves.append((
                    (move[0] + origin[0]) // 2 + xOffset,
                    (move[1] + origin[1]) // 2
                ))

    def redrawPygame(self):
        """
        Draw the current state of the Checkers Game to the pygame window
        """

        # background fill
        self.gui.fill(C_BACKGROUND)

        # draw game board border
        pygame.draw.rect(self.gui, C_GAME_BORDER, (
            DR_GRID_X - DR_GAME_BORDER_SIZE,
            DR_GRID_Y - DR_GAME_BORDER_SIZE,
            self.gridWidth + DR_GAME_BORDER_SIZE * 2, self.gridHeight + DR_GAME_BORDER_SIZE * 2
        ))

        # draw the grid squares
        grid = self.game.redGrid
        for j, r in enumerate(grid):
            # iterate through each column
            for i, c in enumerate(r):
                self.drawSquare(j, i, c, True)
                self.drawSquare(j, i, None, False)

        # draw the moves that can be taken by the selected piece
        moves = []
        if self.playMoves is not None:
            moves.extend(self.playMoves)
        if self.captureMoves is not None:
            moves.extend(self.captureMoves)

        for p in moves:
            if p is not None:
                gridSquare = self.game.gridPos(p[0], p[1], True)
                color = C_MOVE_HIGHLIGHT if gridSquare is None else C_CAPTURE_HIGHLIGHT
                square = gridToBounds(p[0], p[1])
                self.drawSquareHighlight(square, color)

        # draw text at top
        if self.game.win == E_PLAYING:
            text = E_RED_PLAYING if self.game.redTurn else E_BLACK_PLAYING
        else:
            text = E_TEXT[self.game.win]
        self.drawText(E_GAME_STATE_X, E_GAME_STATE_Y, text, E_TEXT_COLOR)

        # draw extra instruction text
        smallFont = makeFont(DR_FONT_FACE, I_FONT_SIZE)
        smallFont.set_bold(True)
        for i, text in enumerate(I_TEXT):
            self.drawText(I_UP_LEFT_X, I_UP_LEFT_Y + i * I_LINE_SPACING, text, I_TEXT_COLOR, smallFont)

        # update display
        pygame.display.update()

    def drawSquare(self, r, c, piece, holds):
        """
        Draw a square of the game
        :param r: The row of the square in the stored game grid
        :param c: The column of the square in the stored game grid
        :param piece: The piece on the square
        :param holds: True if this square is one that holds pieces, False otherwise
        """
        # get square coordinates
        x, y = gridToMouse(c, r)

        # offset if appropriate
        if not (r % 2 == 0 ^ holds):
            x += DR_SQUARE_SIZE

        # draw the square
        square = (x, y, DR_SQUARE_SIZE, DR_SQUARE_SIZE)
        pygame.draw.rect(self.gui, C_ON_SQUARE if holds else C_OFF_SQUARE, square)

        # draw the piece, if one exists
        if piece is not None:
            pColor = C_RED_PIECE if piece[0] else C_BLACK_PIECE
            kColor = C_RED_KING if piece[0] else C_BLACK_KING

            # draw the piece
            # outline
            circleOffset = (DR_SQUARE_SIZE - DR_PIECE_SIZE) * .5 - DR_PIECE_BORDER
            pygame.draw.ellipse(self.gui, C_PIECE_BORDER, (
                square[0] + circleOffset, square[1] + circleOffset,
                DR_PIECE_SIZE + DR_PIECE_BORDER * 2, DR_PIECE_SIZE + DR_PIECE_BORDER * 2
            ))

            # fill
            circleOffset = (DR_SQUARE_SIZE - DR_PIECE_SIZE) * .5
            pygame.draw.ellipse(self.gui, pColor, (
                square[0] + circleOffset, square[1] + circleOffset,
                DR_PIECE_SIZE, DR_PIECE_SIZE
            ))

            # if it is a king, draw a K on the circle
            if piece[1]:
                self.drawText(square[0] + DR_PIECE_SIZE * .3, square[1] + DR_FONT_SIZE * .25, "K", kColor)

        # if a piece is selected, then draw an appropriate highlight over it
        if holds:
            if self.selectedSquare is not None and self.selectedSquare == (c, r):
                self.drawSquareHighlight(square, C_SELECTED_HIGHLIGHT)
            elif self.hoverSquare is not None and self.hoverSquare == (c, r):
                self.drawSquareHighlight(square, C_HOVER_HIGHLIGHT)

    def drawText(self, x, y, text, color, textFont=None):
        """
        Draw some text to the pygame Gui
        :param x: The x coordinate of the text
        :param y: The y coordinate of the text
        :param text: The text to draw
        :param color: The color of the text
        :param textFont: Font to use, or None to use default
        """
        if textFont is None:
            textFont = self.font
        value = textFont.render(text, False, color)
        self.gui.blit(value, (x, y))

    def drawSquareHighlight(self, square, color):
        """
        Draw a highlight over a square on the Game Gui
        :param square: The bounds of the square to draw
        :param color: The color of the highlight, including alpha channel
        """
        highlight = pygame.Surface((square[2], square[3]), pygame.SRCALPHA)
        pygame.draw.rect(highlight, color, highlight.get_rect())
        self.gui.blit(highlight, square)

    def mouseToGrid(self, x, y):
        """
        Given x and y coordinates on the Checkers Game Gui, get the row and column of the selected square
        :param x: The x position of the mouse
        :param y: The y position of the mouse
        :return: A 2-tuple of the red side grid row and column values for the selected piece (r, c)
            or None if no valid square was selected
        """
        x = int((x - (DR_PIECE_BORDER + DR_BORDER_SIZE)) / DR_SQUARE_SIZE)
        y = int((y - (DR_PIECE_BORDER + DR_BORDER_SIZE + DR_TOP_SPACE)) / DR_SQUARE_SIZE)

        evenR = y % 2 == 0
        evenC = x % 2 == 0

        x = x // 2

        if evenR ^ evenC and self.game.inRange(x, y):
            return x, y
        else:
            return None

    def stop(self):
        """
        End the pygame window thread
        :return:
        """
        self.running = False
        pygame.quit()


def gridToMouse(c, r):
    """
    Convert the coordinates in grid row and column to pixels in mouse coordinates
    :param c: The column of the square to obtain
    :param r: The row of the square to obtain
    :return: A 2-tuple (x, y) of the pixel coordinates
    """
    return DR_GRID_X + c * 2 * DR_SQUARE_SIZE, DR_GRID_Y + r * DR_SQUARE_SIZE


def gridToBounds(c, r):
    """
    Convert the coordinates in grid row and column to pixels bounds in mouse coordinates
    :param c: The column of the square to obtain
    :param r: The row of the square to obtain
    :return: A 4-tuple (x, y, width, height) of the pixel bounds
    """
    x, y = gridToMouse(c, r)

    # offset if appropriate
    if r % 2 == 0:
        x += DR_SQUARE_SIZE

    # return the bounds
    return x, y, DR_SQUARE_SIZE, DR_SQUARE_SIZE


def makeFont(face, size):
    """
    Utility method for setting font
    :param face: The font type of the font
    :param size: The size of the font
    :return: the font object
    """
    return pygame.font.SysFont(face, size)
