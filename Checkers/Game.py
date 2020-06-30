# constants for ending game
E_PLAYING = 0
E_RED_WIN = 1
E_BLACK_WIN = 2
E_DRAW = 3
E_MAX_MOVES_WITHOUT_CAPTURE = 25
E_TEXT = [
    "Game In Progress",
    "Red Wins!",
    "Black Wins!",
    "Draw!"
]

# constants for printing the game
P_ALLY = "[A"
P_ENEMY = "[E"
P_NORMAL = " ]"
P_KING = "K]"
P_EMPTY = "[  ]"


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

        self.win = E_PLAYING
        self.movesSinceLastCapture = 0
        # the total number of moves made in the game so far
        self.moves = 0

        self.resetGame()

    def makeCopy(self):
        """
        Get an exact copy of this game, but as a completely separate object
        :return: The copy
        """
        g = Game(self.height)

        g.redTurn = self.redTurn
        g.win = self.win
        g.movesSinceLastCapture = self.movesSinceLastCapture
        g.moves = self.moves

        pieces = self.toList()
        g.setBoard(pieces, g.redTurn)
        return g

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

        # reset number of moves
        self.movesSinceLastCapture = 0
        self.moves = 0

    def clearBoard(self):
        """
        Clear out the entire board, making every space empty
        """
        for y in range(self.height):
            # fill in each spot in the row
            for x in range(self.width):
                yy = self.height - 1 - y
                self.spot(x, yy, None, True)

    def setBoard(self, pieceList, red):
        """
        Set the values of all the grid spaces in this Game
        :param pieceList: A 1D list of piece values, None or a 2-tuple (ally, king)
        :param red: True if the pieces come from red's perspective, False otherwise
        """
        for i, c in enumerate(pieceList):
            x, y = self.singlePos(i)
            self.spot(x, y, c, red)

    def toList(self):
        """
        Put all of the squares of the board into a list, from the perspective
            of the current player of the game
        :return: A 1D list of all the squares, each square is either None for empty,
            or a 2-tuple (ally, king), relative to the current player
        """
        grid = self.currentGrid()
        vals = []
        for r in grid:
            for c in r:
                # separating out values, to make copies, not references
                vals.append(c if c is None else (c[0], c[1]))

        return vals

    def singlePos(self, s):
        """
        Convert position in a 1D array to a position in the grid
        :param s: The position in the 2D array
        :return: A 2-tuple (x, y) of grid coordinates
        """
        return s % self.width, s // self.width

    def string(self, red):
        """
        Convert the game to a string for display
        :param red: True if this get the grid from red perspective, False for black perspective
        :return: The game board
        """
        # list to track all text
        text = ["Red's turn"] if self.redTurn else ["Black's Turn"]

        # show labels for which side is from which perspective
        text.append("Black Side" if red else "Red Side")

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

        # show labels for which side is from which perspective
        text.append("Red Side" if red else "Black Side")

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

    def currentGrid(self):
        """
        Get the game board from the perspective of the current player's turn
        :return The grid
        """
        return self.redGrid if self.redTurn else self.blackGrid

    def area(self):
        """
        Get the total number of squares in the stored game grid
        :return: The area
        """
        return self.width * self.height

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

    def play(self, pos, modifiers):
        """
        Progress the game by one move. This is the method that should be called when a player makes a full move.
        The movement is always based on the player of the current turn.
        :param pos: A 2-tuple (x, y) of positive integers the grid coordinates of the piece to move
        :param modifiers: A list of booleans, (left, forward, jump)
            left: True to move left, False to move Right
            forward: True to move forward, False to move backwards
            jump: True if this move is a jump, False if it is a normal move
        :return: True if it is now the other players turn, False otherwise
        """

        x, y = pos
        left, forward, jump = modifiers

        # cannot play at all if the game is not playing
        if not self.win == E_PLAYING:
            return False

        if self.canPlay(pos, modifiers):
            newX, newY = movePos(pos, modifiers)

            newPiece = self.gridPos(x, y, self.redTurn)

            # set the piece to a king if it reaches the end
            if newY == 0:
                newPiece = (newPiece[0], True)

            self.spot(newX, newY, newPiece, self.redTurn)
            self.spot(x, y, None, self.redTurn)
            # a capture has happened
            if jump:
                self.movesSinceLastCapture = 0
                jX, jY = movePos(pos, [left, forward, False])
                self.spot(jX, jY, None, self.redTurn)

            # update number of moves
            self.movesSinceLastCapture += 1
            self.moves += 1

            # see if the game is over
            self.checkWinConditions()

            changeTurns = not jump
        else:
            changeTurns = False

        if changeTurns:
            self.redTurn = not self.redTurn
        return changeTurns

    def canPlay(self, pos, modifiers):
        """
        Determine if a move can be made in the game.
        The move is based on the current turn of the game, ie. if red is moving,
            then the coordinates are from red's perspective
        :param pos: A 2-tuple (x, y) of positive integers the grid coordinates of the piece to move
        :param modifiers: A list of 3 booleans, (left, forward, jump)
            left: True to move left, False to move Right
            forward: True to move forward, False to move backwards
            jump: True if this move is a jump, False if it is a normal move
        :return True if the piece can make the move, False otherwise
        """
        x, y = pos
        left, forward, jump = modifiers

        if not self.validPiece(x, y, forward):
            return False

        # determine directions
        newX, newY = movePos(pos, modifiers)

        # check to see if movement for the new coordinate is in bounds
        if not self.inRange(newX, newY):
            return False
        # check if the piece jumped over is an enemy
        if jump:
            jX, jY = movePos(pos, [left, forward, False])
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

        # if black has no pieces, red wins
        # if red has no pieces, black wins
        if self.redLeft == 0:
            self.win = E_BLACK_WIN
            return
        elif self.blackLeft == 0:
            self.win = E_RED_WIN
            return

        # see if no one can make any moves
        noMoves = True
        # iterate through rows
        for j in range(self.height):
            # iterate through the columns of each row
            for i in range(self.width):
                # if the spot is not empty, there might be moves
                c = self.gridPos(i, j, self.redTurn)
                if c is not None:
                    # check if the spot piece is an ally and it has moves
                    noMoves = not c[0] or not self.canMovePos((i, j))
                # break out of the loops, a move has been found
                if not noMoves:
                    break
            if not noMoves:
                break

        # if no one can move, or if no one has any pieces, or
        # if too many moves have happened with no captures, it's a draw
        if noMoves or (self.redLeft == 0 and self.blackLeft == 0) or \
                self.movesSinceLastCapture >= E_MAX_MOVES_WITHOUT_CAPTURE:
            self.win = E_DRAW
        else:
            self.win = E_PLAYING

    def calculateMoves(self, s):
        """
        Given the grid coordinates of a square, determine the list of moves that can be played by that piece.
        :param s: The coordinates of a square
        :return The list of moves, a list of 8, 2-tuples, (x, y) of moves that can be taken,
            or None if that move cannot be taken.
            Coordinates relative to the current players turn
        """
        playMoves = []
        # 8 different possible moves
        for i in range(8):
            bins = moveIntToBoolList(i)
            # check if the move can be played
            if self.canPlay(s, bins):
                # determine the position of the move
                move = movePos(s, bins)
                playMoves.append(move)
            else:
                playMoves.append(None)
        return playMoves

    def canMovePos(self, pos):
        """
        Determine if a piece at a given grid position has any moves for the current player
        :param pos: The grid position
        :return: True if a piece at that position has at least one move, False otherwise
        """
        moves = self.calculateMoves(pos)
        for m in moves:
            if m is not None:
                return True
        return False

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


def movePos(pos, modifiers):
    """
    Determine the coordinates of a new move
    The move is based on the current turn of the game, ie. if red is moving,
        then the coordinates are from red's perspective
    :param pos: A 2-tuple (x, y) of positive integers the grid coordinates of the piece to move
    :param modifiers: A list of booleans, (left, forward, jump)
        left: True to move left, False to move Right
        forward: True to move forward, False to move backwards
        jump: True if this move is a jump, False if it is a normal move
    :return The coordinates of the location of the new move, as a 2-tuple (x, y)
    """

    x, y = pos
    left, forward, jump = modifiers

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


def moveIntToBoolList(i):
    """
    Convert an integer in the range [0-7] to a list of 3 boolean values, corresponding to the binary representation
    :param i: The integer
    :return: The list of 3 boolean values
    """
    return [b == '1' for b in "{0:03b}".format(i)]
