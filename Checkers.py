from learning.QLearn import *

# some constants for printing the game
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
        self.resetGame()

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

        # fill in each row
        for y in range(fill):
            # fill in each spot in the row
            for x in range(self.width):
                yy = self.height - 1 - y
                self.spot(x, yy, (True, False), False)
                self.spot(x, yy, (True, False), True)

        # set it to reds turn
        self.redTurn = True

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

    def spot(self, x, y, value, red):
        """
        Set the value at a position in the grid
        :param x: The x coordinate
        :param y: The y coordinate
        :param value: The new value
        :param red: True if this should access from Red size, False otherwise
        """
        allyX, allyY = x, y
        enemyX, enemyY = self.width - 1 - allyX, self.height - 1 - allyY
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
        :return: True if the move happened and it is now the other players turn, False otherwise
        """
        if self.canPlay(x, y, left, forward, jump):
            newX, newY = movePos(x, y, left, forward, jump)
            self.spot(newX, newY, self.gridPos(x, y, self.redTurn), self.redTurn)
            self.spot(x, y, None, self.redTurn)
            success = True
        else:
            success = False

        if success:
            self.redTurn = not self.redTurn
        return success

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
        x, y = movePos(x, y, left, forward, jump)

        # check to see if movement for the new coordinate is in bounds
        if not self.inRange(x, y):
            return False

        # return if the new position to move to is empty
        return self.gridPos(x, y, self.redTurn) is None

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
