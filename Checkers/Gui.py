from Checkers.Game import *
from Constants import *

if USE_PY_GAME:
    import pygame

import time

# technical constants
ENABLE_LOOP_WAIT = False
TICK_RATE = 60
TICK_TIME = 1.0 / TICK_RATE

E_RED_PLAYING = "Red's Turn"
E_BLACK_PLAYING = "Black's Turn"
E_TEXT_COLOR = (0, 0, 0)
E_GAME_STATE_X = 10
E_GAME_STATE_Y = 10

# constants for drawing the game
DR_SQUARE_SIZE = 80
DR_BORDER_SIZE = 20
DR_GAME_BORDER_SIZE = 5
DR_TOP_SPACE = 167
DR_GRID_X = DR_BORDER_SIZE + DR_GAME_BORDER_SIZE
DR_GRID_Y = DR_BORDER_SIZE + DR_TOP_SPACE + DR_GAME_BORDER_SIZE
DR_PIECE_SIZE = 70
DR_PIECE_BORDER = 3
DR_FONT_SIZE = 50
DR_FONT_FACE = "Arial"

# constants for instruction text at the top
I_FONT_SIZE = 16
I_UP_LEFT_X = 10
I_UP_LEFT_Y = 60
I_LINE_SPACING = 18
I_TEXT = [
    "R: reset game",
    "E: reset game custom",
    "A: make AI move",
    "T: make AI move and train",
    "Q: make AI move without exploring",
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

# variables for tracking animations
T_SAVE_TIME = 120
T_SAVE_TEXT = {True: "Save Successful", False: "Save Failed", None: ""}
T_SAVE_TEXT_COLOR = {True: (0, 0, 100), False: (100, 0, 0), None: (0, 0, 0)}
T_SAVE_X = 140
T_SAVE_Y = 60


class Gui:
    """
    A class that handles displaying and taking input for playing a Checkers Game in a GUI with pygame
    """

    def __init__(self, qObject, fps=20, printFPS=False, defaultGame=None, playerTrainer=None):
        """
        Create and display the pygame Gui with the given game.
        Must call loop() to make the Gui stay open
        :param qObject: The PieceEnvironment object to use for making an AI move, the Game object also comes from here
        :param fps: The capped frame rate of the Gui, default 20
        :param printFPS: True to print the frames per second, every second, False otherwise, default False
        :param defaultGame: A custom Game with the pieces in the state where they should start,
            red still always moves first.
            Use None to have a normal game. Default None
        :param playerTrainer: A PlayerTrainer object which will be used
            for training the network by a user playing the game. None to not use this feature.
            Default None.
        """
        # initialize objects
        self.qDuelModel = qObject
        self.game = qObject.game
        self.defaultGame = defaultGame
        self.playerTrainer = playerTrainer

        # create dictionary for activating key presses
        self.keyDict = {
            pygame.K_r: lambda: self.resetGame(),
            pygame.K_e: lambda: self.resetGame(self.defaultGame),
            pygame.K_ESCAPE: lambda: self.stop(),
            pygame.K_a: lambda: self.unselectSquare() if self.makeQModelMove() else None,
            pygame.K_t: lambda: self.unselectSquare() if self.makeQModelMove(train=True) else None,
            pygame.K_q: lambda: self.unselectSquare() if self.makeQModelMove(explore=0) else None,
            pygame.K_s: lambda: self.saveGame(),
            None: lambda: None
        }

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

        # variables for tracking save notification
        self.saveNoteTimer = 0
        self.saveSuccess = None

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

    def stopLoop(self):
        """
        Stop running the game and close the window
        """
        self.running = False

    def loop(self):
        """
        A method that handles updating the state of the game
        """
        lastTime = time.time()
        lastFrame = time.time()
        lastTick = time.time()
        frames = 0
        while self.running:
            frameTime = 1 / self.fps
            self.handleEvents()

            currTime = time.time()

            # determine if the game should be redrawn
            if currTime - lastFrame > frameTime:
                frames += 1
                lastFrame = time.time()
                self.redrawPygame()
            elif ENABLE_LOOP_WAIT:
                # wait a bit of time to prevent the loop from running unnecessarily long amounts of time
                time.sleep(0.01)

            # determine if the game should be ticked again
            currTime = time.time()
            if currTime - lastTick > TICK_TIME:
                frames += 1
                lastTick = time.time()
                self.tick()

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
            if self.hoverSquare is None:
                # only move the piece if playMoves and selectedSquare exist
                if self.playMoves is not None and self.selectedSquare is not None:
                    self.handleMoveSelect()
                    self.unselectSquare()
            # otherwise, select that square, and calculate the moves the square can use
            else:
                self.selectSquare()
                if self.selectedSquare is not None:
                    self.calculateMoves(self.selectedSquare)

    def handleMoveSelect(self):
        """
        Assume that self.playMoves and self.selectedSquare are valid.
        Make a move in the game based on the position of the mouse by selecting a valid move.
        """
        mPos = pygame.mouse.get_pos()
        gPos = self.mouseToGrid(mPos[0], mPos[1])
        if gPos is not None:
            self.handleGameMove(gPos)

    def handleGameMove(self, gPos):
        """
        Assume that self.playMoves and self.selectedSquare are valid,
        then make a move based on those squares
        :param gPos: The position in the game to move
        """
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
                    if self.playerTrainer is not None:
                        self.handlePlayerTrainerMove(s, bins)
                    else:
                        self.game.play(s, bins)

    def handlePlayerTrainerMove(self, s, modifiers):
        """
        Train and make a move with the player trainer.
        :param s: The position of the piece to move
        :param modifiers: The modifiers for the move, a 3-tuple (left, forward, jump)
        """
        if not self.game.redTurn == self.playerTrainer.redSide:
            self.playerTrainer.makeOpponentMove(s, modifiers)
            self.game.play(s, modifiers)
            over = not (self.game.win == E_PLAYING)
            if self.game.redTurn == self.playerTrainer.redSide or over:
                if over:
                    self.game.redTurn = not self.game.redTurn
                self.playerTrainer.train()

    def handleKeyUp(self, event):
        """
        This method is run every time pygame detects a key on the keyboard has been released
        :param event: The pygame event object from the keypress
        """
        k = event.key
        if k in self.keyDict:
            self.keyDict[k]()

    def saveGame(self):
        """
        Save the current state of the game to the default file
        """
        self.saveNoteTimer = T_SAVE_TIME
        self.saveSuccess = self.qDuelModel.save("", DUEL_MODEL_NAME)

    def resetGame(self, defaultGame=None):
        """
        Bring the game in the GUI to a default state.
        :param defaultGame: A Checkers Game with the pieces in the desired starting state.
        """
        self.game.resetGame(defaultGame)
        self.unselectSquare()
        if self.playerTrainer is not None:
            self.playerTrainer.reset()

    def makeQModelMove(self, train=False, explore=None):
        """
        Make the next move in the game with the current QModel. Does nothing if that QModel is None
        :param train: True to also train the network with this move, False otherwise, default False
        :param explore: The exploration rate to use for this move, None to not make any changes, default None
        :return True if a move was successfully made, False otherwise
        """

        # if the game is over, don't make a move
        if not self.game.win == E_PLAYING:
            return

        # get the appropriate environment
        qEnv = self.qDuelModel.currentEnvironment()

        # save the old exploration rate
        oldExplorePiece = qEnv.internalNetwork.explorationRate
        oldExploreGame = qEnv.gameNetwork.explorationRate

        # set the new exploration rate
        if explore is not None:
            qEnv.internalNetwork.explorationRate = explore
            qEnv.gameNetwork.explorationRate = explore

        # ensure a model exists
        model = qEnv.internalNetwork
        if model is None or qEnv is None:
            return False

        # make the move
        if train:
            qEnv.trainMove()
        else:
            if self.playerTrainer is None:
                qEnv.performAction(model)
            else:
                # using the player trainer, determine which moves to make, and make them
                pieceAction, gameAction = qEnv.generateAction()

                self.playerTrainer.makeMove(pieceAction, gameAction)

                if not self.game.win == E_PLAYING:
                    self.playerTrainer.train()

        # reset the exploration rate
        qEnv.internalNetwork.explorationRate = oldExplorePiece
        qEnv.gameNetwork.explorationRate = oldExploreGame

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

        moves = self.game.calculateMoves(s, self.game.redTurn)
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

    def tick(self):
        """
        Update variables tracking animations
        """
        if self.saveNoteTimer > 0:
            self.saveNoteTimer -= 1

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

        # draw save notification
        if self.saveNoteTimer > 0:
            self.drawText(T_SAVE_X, T_SAVE_Y, T_SAVE_TEXT[self.saveSuccess],
                          T_SAVE_TEXT_COLOR[self.saveSuccess], smallFont)

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
        """
        self.running = False


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
