from learning.QLearn import *

if USE_PY_GAME:
    import pygame

import time

# technical constants
ENABLE_LOOP_WAIT = False

# constants for ending game
E_PLAYING = 0
E_RED_WIN = 1
E_BLACK_WIN = 2
E_DRAW = 3
E_MAX_MOVES_WITHOUT_CAPTURE = 50
E_TEXT = [
    "Game In Progress",
    "Red Wins!",
    "Black Wins!",
    "Draw!"
]
E_RED_PLAYING = "Red's Turn"
E_BLACK_PLAYING = "Black's Turn"
E_TEXT_COLOR = (0, 0, 0)
E_GAME_STATE_X = 10
E_GAME_STATE_Y = 10

# constants for printing the game
P_ALLY = "[A"
P_ENEMY = "[E"
P_NORMAL = " ]"
P_KING = "K]"
P_EMPTY = "[  ]"

# constants for drawing the game
DR_SQUARE_SIZE = 80
DR_BORDER_SIZE = 20
DR_GAME_BORDER_SIZE = 5
DR_TOP_SPACE = 120
DR_GRID_X = DR_BORDER_SIZE + DR_GAME_BORDER_SIZE
DR_GRID_Y = DR_BORDER_SIZE + DR_TOP_SPACE + DR_GAME_BORDER_SIZE
DR_PIECE_SIZE = 70
DR_PIECE_BORDER = 3
DR_FONT_SIZE = 50
DR_FONT_FACE = "Arial"

# constants for instruction text at the top
I_FONT_SIZE = 20
I_UP_LEFT_X = 10
I_UP_LEFT_Y = 70
I_LINE_SPACING = 25
I_TEXT = [
    "R: reset game",
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


class Game:
    """
    An object that stores the state of a game of checkers and handles all operations controlling the game
    """
    def __init__(self, size):
        """
        Create a new Game object, initialized to a standard default state
        The grid represents a square game board, but only stores the half of the board with pieces.
        The lowest left spot on the grid is where the first piece goes, the furthest right spot on
          the corresponding row of the game board would be empty.
        This bottom row is an even row, and the odd rows are opposite of even rows.
        For an odd row, the leftmost spot on the game board would be empty, the rightmost spot would
          have a piece
        A spot in the grid is None if it has no piece, or a tuple if it is filled.
        Each filled spot in the grid is a tuple of two boolean values, the first is Ally, the second is king.
          Ally = True means the piece is an ally, False means it is not
          King = True means the piece is a king and came move forwards and backwards,
              False means it is not, and can only move forward
        Ally pieces start at the bottom, enemy pieces start at the top.
        redGrid is the grid from the perspective of red, blackGrid is from the perspective of black
        redGrid and blackGrid should not directly be accessed, use the helper functions.
        :param size: The width and height of the game board, must be an even integer > 2
        """
        self.width = size // 2
        self.height = size

        self.redGrid = None
        self.blackGrid = None
        self.redTurn = None
        self.redLeft = 0
        self.blackLeft = 0
        self.resetGame()

        self.win = E_PLAYING
        self.movesSinceLastCapture = 0

    def resetGame(self):
        """
        Bring the game to the default state at the beginning of the game
        """
        # initialize to blank grid
        self.redGrid = []
        for i in range(self.height):
            self.redGrid.append([None] * self.width)
        self.blackGrid = []
        for i in range(self.height):
            self.blackGrid.append([None] * self.width)

        # fill in all but the 2 middle rows
        fill = self.height // 2 - 1

        # track the number of each piece
        self.redLeft = 0
        self.blackLeft = 0

        # fill in each row
        for y in range(fill):
            # fill in each spot in the row
            for x in range(self.width):
                yy = self.height - 1 - y
                # add red piece
                self.spot(x, yy, (True, False), True)
                # add black piece
                self.spot(x, yy, (True, False), False)

        # set it to reds turn
        self.redTurn = True
        self.win = E_PLAYING

    def clearBoard(self):
        """
        Clear out the entire board, making every space empty
        :return:
        """
        for y in range(self.height):
            # fill in each spot in the row
            for x in range(self.width):
                yy = self.height - 1 - y
                self.spot(x, yy, None, True)

    def string(self, red):
        """
        Convert the game to a string for display
        :param red: True if this get the grid from red perspective, False for black perspective
        :return: The game board
        """
        # list to track all text
        text = ["Red's turn"] if self.redTurn else ["Black's Turn"]

        # iterate through each row
        for j, r in enumerate(self.redGrid):
            # list to track row text
            row = []
            # iterate through each column
            for i, c in enumerate(r):
                # even row
                if j % 2 == 0:
                    row.append(P_EMPTY)
                    row.append(pieceString(self.gridPos(i, j, red)))
                # odd row
                else:
                    row.append(pieceString(self.gridPos(i, j, red)))
                    row.append(P_EMPTY)
            # combine the text into a row
            text.append("".join(row))
        # return the final result
        return "\n".join(text)

    def oppositeGrid(self, p):
        """
        Get the coordinates of a place in the grid from the opposing side of the given coordinates
        :param p: A 2-tuple the original x, y
        :return: A 2-tuple (x, y) of the original x and y, but from the perspective of the other side of the board
        """
        x, y = p
        return self.width - 1 - x, self.height - 1 - y

    def spot(self, x, y, value, red):
        """
        Set the value at a position in the grid
        :param x: The x coordinate
        :param y: The y coordinate
        :param value: The new value
        :param red: True if this should access from Red size, False otherwise
        """

        oldSpace = self.redGrid[y][x] if red else self.blackGrid[y][x]

        allyX, allyY = x, y
        enemyX, enemyY = self.oppositeGrid((allyX, allyY))
        if value is None:
            ally = None
            enemy = None
        else:
            ally = value
            enemy = (not value[0], value[1])
        if red:
            self.redGrid[allyY][allyX] = ally
            self.blackGrid[enemyY][enemyX] = enemy
        else:
            self.redGrid[enemyY][enemyX] = enemy
            self.blackGrid[allyY][allyX] = ally

        newSpace = self.redGrid[y][x] if red else self.blackGrid[y][x]

        if not newSpace == oldSpace:
            if newSpace is not None:
                if newSpace[0] == red:
                    self.redLeft += 1
                else:
                    self.blackLeft += 1
            if oldSpace is not None:
                if oldSpace[0] == red:
                    self.redLeft -= 1
                else:
                    self.blackLeft -= 1

    def gridPos(self, x, y, red):
        """
        Get the value of a position in the grid
        :param x: The x coordinate
        :param y: The y coordinate
        :param red: True if this should get the value from red side, False to get it from black side
        :return: The value
        """
        if red:
            return self.redGrid[y][x]
        else:
            return self.blackGrid[y][x]

    def play(self, x, y, left, forward, jump):
        """
        Progress the game by one move. This is the method that should be called when a player makes a full move.
        The movement is always based on the player of the current turn.
        Red moves first.
        :param x: The x coordinate of the piece to move
        :param y: The y coordinate of the piece to move
        :param left: True to move left, False to move Right
        :param forward: True to move forward, False to move backwards
        :param jump: True if this move is a jump, False if it is a normal move
        :return: True if it is now the other players turn, False otherwise
        """
        # cannot play at all if the game is not playing
        if not self.win == E_PLAYING:
            return False

        if self.canPlay(x, y, left, forward, jump):
            newX, newY = movePos(x, y, left, forward, jump)

            newPiece = self.gridPos(x, y, self.redTurn)

            # set the piece to a king if it reaches the end
            if newY == 0:
                newPiece = (newPiece[0], True)

            self.spot(newX, newY, newPiece, self.redTurn)
            self.spot(x, y, None, self.redTurn)
            # a capture has happened
            if jump:
                self.movesSinceLastCapture = 0
                jX, jY = movePos(x, y, left, forward, False)
                self.spot(jX, jY, None, self.redTurn)

            # update number of moves
            self.movesSinceLastCapture += 1

            # see if the game is over
            self.checkWinConditions()

            changeTurns = not jump
        else:
            changeTurns = False

        if changeTurns:
            self.redTurn = not self.redTurn
        return changeTurns

    def canPlay(self, x, y, left, forward, jump):
        """
        Determine if a move can be made in the game.
        The move is based on the current turn of the game, ie. if red is moving,
            then the coordinates are from red's perspective
        :param x: The x coordinate of the piece to move, it is assumed the coordinate is in bounds of the grid
        :param y: The y coordinate of the piece to move, it is assumed the coordinate is in bounds of the grid
        :param left: True if the piece is moving to diagonally left, False for diagonally right
        :param forward: True if the piece is moving forward, relative to that sides direction,
            False to move backwards, only happens if kings can do it
        :param jump: True if this move is a jump, False if it is a normal move
        :return True if the piece can make the move, False otherwise
        """

        if not self.validPiece(x, y, forward):
            return False

        # determine directions
        newX, newY = movePos(x, y, left, forward, jump)

        # check to see if movement for the new coordinate is in bounds
        if not self.inRange(newX, newY):
            return False
        # check if the piece jumped over is an enemy
        if jump:
            jX, jY = movePos(x, y, left, forward, False)
            pos = self.gridPos(jX, jY, self.redTurn)
            if pos is None or pos[0]:
                return False

        # return if the new position to move to is empty
        return self.gridPos(newX, newY, self.redTurn) is None

    def checkWinConditions(self):
        """
        See if the game is over, and set win to the appropriate value
        """
        # if the game is already over, no need to check
        if not self.win == E_PLAYING:
            return

        # if too many moves have happened with no captures, the game is a draw
        if self.movesSinceLastCapture >= E_MAX_MOVES_WITHOUT_CAPTURE:
            self.win = E_DRAW
            return

        # see if no one can make any moves
        noMoves = True
        self.redTurn = not self.redTurn
        # iterate through rows
        for j in range(self.height):
            # iterate through the columns of each row
            for i in range(self.width):
                # if the spot contains a piece and that piece is an ally
                c = self.gridPos(i, j, self.redTurn)
                potentialMoves = self.calculateMoves((i, j))
                if c is not None and c[0]:
                    # find the moves of that piece
                    # if at least one of those moves is valid, then there are not no moves
                    for p in potentialMoves:
                        if p is not None:
                            noMoves = False
                            break
                # break each of the outer loops if a move is found
                if not noMoves:
                    break
            if not noMoves:
                break
        self.redTurn = not self.redTurn

        # if black has no pieces, red wins
        # if red has no pieces, black wins
        # if no one has any pieces, or no one can move, it's a draw
        if (self.redLeft == 0 and self.blackLeft == 0) or noMoves:
            self.win = E_DRAW
        elif self.redLeft == 0:
            self.win = E_BLACK_WIN
        elif self.blackLeft == 0:
            self.win = E_RED_WIN
        else:
            self.win = E_PLAYING

    def calculateMoves(self, s):
        """
        Given the grid coordinates of a square, determine the list of moves that can be played by that piece.
        :param s: The coordinates of a square
        :return The list of moves, a list of 8, 2-tuples, (x, y) of moves that can be taken,
            or None if that move cannot be taken. The move index is based on binary,
            4s place = left, 2s place = forward, 1s place = jump
            Coordinates relative to the current players turn
        """
        playMoves = []
        # 8 different possible moves
        for i in range(8):
            bins = moveIntToBoolList(i)
            # check if the move can be played
            if self.canPlay(s[0], s[1], bins[0], bins[1], bins[2]):
                # determine the position of the move
                move = movePos(s[0], s[1], bins[0], bins[1], bins[2])
                playMoves.append(move)
            else:
                playMoves.append(None)
        return playMoves

    def validPiece(self, x, y, forward):
        """
        Given a piece, determine if the piece is valid to move.
        If the piece is empty, then it cannot move.
        If the piece is not a king, then it cannot move backwards.
        If the piece is not an ally, then it cannot be moved. This assumes the piece is being obtained from the
            grid relative of that pieces turn
        :param x: The x coordinate of the piece to check
        :param y: The y coordinate of the piece to check
        :param forward: True if this piece is trying to move forward, False otherwise
        :return: True if the piece can move, False otherwise
        """
        piece = self.gridPos(x, y, self.redTurn)
        return not (piece is None or (not piece[1] and not forward) or not piece[0])

    def inRange(self, x, y):
        """
        Determine if a coordinate for a piece is in the range of the game board
        :param x: The x coordinate of the piece to check
        :param y: The y coordinate of the piece to check
        :return: True if the piece is in the range, False otherwise
        """
        return 0 <= y < self.height and 0 <= x < self.width


def pieceString(piece):
    """
    Convert the given piece of a Checkers Game to a string.
    :param piece: The piece, must be either a 2-tuple of boolean values, or None
    :return: The string representation
    """
    if piece is None:
        return P_EMPTY

    text = []
    if piece[0]:
        text.append(P_ALLY)
    else:
        text.append(P_ENEMY)
    if piece[1]:
        text.append(P_KING)
    else:
        text.append(P_NORMAL)
    return "".join(text)


def movePos(x, y, left, forward, jump):
    """
    Determine the coordinates of a new move
    The move is based on the current turn of the game, ie. if red is moving,
        then the coordinates are from red's perspective
    :param x: The x coordinate of the piece to move, it is assumed the coordinate is in bounds of the grid
    :param y: The y coordinate of the piece to move, it is assumed the coordinate is in bounds of the grid
    :param left: True if the piece is moving to diagonally left, False for diagonally right
    :param forward: True if the piece is moving forward, relative to that sides direction,
        False to move backwards, only happens if kings can do it
    :param jump: True if this move is a jump, False otherwise
    :return The coordinates of the location of the new move, as a 2-tuple (x, y)
    """
    if jump:
        # determine direction for y axis
        newY = y - 2 if forward else y + 2
        # determine direction for x axis
        if left:
            newX = x - 1
        else:
            newX = x + 1
    else:
        # determine direction for y axis
        newY = y - 1 if forward else y + 1
        # determine direction for x axis
        if left:
            newX = x - 1 if y % 2 == 1 else x
        else:
            newX = x + 1 if y % 2 == 0 else x
    return newX, newY


class PieceEnvironment(Environment):
    """
    An Environment used to determine where a piece should move to
    """

    def __init__(self):
        pass

    def stateSize(self):
        return 0

    def toState(self):
        return np.zeros((1, 0))

    def currentState(self):
        return 0

    def numStates(self):
        return 0

    def rewardFunc(self, s, a):
        return 0

    def takeAction(self, action):
        return 0


class GameEnvironment(Environment):
    """
    An Environment used to determine which piece in a Game should vbe moved
    """

    def __init__(self):
        pass

    def stateSize(self):
        return 0

    def toState(self):
        return np.zeros((1, 0))

    def currentState(self):
        return 0

    def numStates(self):
        return 0

    def rewardFunc(self, s, a):
        return 0

    def takeAction(self, action):
        return 0


class Gui:
    """
    A class that handles displaying and taking input for playing a Checkers Game in a GUI with pygame
    """

    def __init__(self, game, fps=20, printFPS=False):
        """
        Create and display the pygame Gui with the given game.
        Must call loop() to make the Gui stay open
        :param game: The Checkers Game object to use with this Gui
        :param fps: The capped frame rate of the Gui, default 20
        :param printFPS: True to print the frames per second, every second, False otherwise, default False
        """
        self.game = game

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
                                    self.game.play(s[0], s[1], bins[0], bins[1], bins[2])

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
        if event.key == pygame.K_r:
            self.game.resetGame()
            self.unselectSquare()
        elif event.key == pygame.K_ESCAPE:
            self.running = False

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


def moveIntToBoolList(i):
    """
    Convert an integer in the range [0-7] to a list of 3 boolean values, corresponding to the binary representation
    :param i:
    :return:
    """
    return [b == '1' for b in "{0:03b}".format(i)]


def makeFont(face, size):
    """
    Utility method for setting font
    :param face: The font type of the font
    :param size: The size of the font
    :return: the font object
    """
    return pygame.font.SysFont(face, size)
