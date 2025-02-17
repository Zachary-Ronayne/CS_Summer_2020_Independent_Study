from Constants import E_MAX_MOVES_WITHOUT_CAPTURE

# constants for ending game
E_PLAYING = 0
E_RED_WIN = 1
E_BLACK_WIN = 2
E_DRAW_NO_PIECES = 3
E_DRAW_NO_MOVES_RED = 4
E_DRAW_NO_MOVES_BLACK = 5
E_DRAW_TOO_MANY_MOVES = 6
E_DRAW_MIN = E_DRAW_NO_PIECES
E_DRAW_MAX = E_DRAW_TOO_MANY_MOVES
E_TEXT = [
    "Game In Progress",
    "Red Wins!",
    "Black Wins!",
    "Draw! No pieces remain",
    "Draw! Red is out of moves",
    "Draw! Black is out of moves",
    "Draw! No capture in " + str(E_MAX_MOVES_WITHOUT_CAPTURE) + " moves"
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
    def __init__(self, size, autoReset=True):
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
        :param autoReset: True to reset the game to a normal state by default,
            False to only initialize bare minimum state
            Default True, should only use False when making copies
        """
        self.width = size // 2
        self.height = size

        self.redGrid = None
        self.blackGrid = None
        self.redTurn = None
        self.redLeft = 0
        self.blackLeft = 0

        self.redMoves = None
        self.blackMoves = None

        self.win = E_PLAYING
        self.movesSinceLastCapture = 0
        # the total number of moves made in the game so far
        self.moves = 0

        if autoReset:
            self.resetGame()

    def makeCopy(self):
        """
        Get an exact copy of this game, but as a completely separate object
        :return: The copy
        """
        g = Game(self.height, autoReset=False)

        g.redTurn = self.redTurn
        g.win = self.win
        g.movesSinceLastCapture = self.movesSinceLastCapture
        g.moves = self.moves
        g.redLeft = self.redLeft
        g.blackLeft = self.blackLeft

        g.redGrid = []
        g.blackGrid = []
        for rr, rb in zip(self.redGrid, self.blackGrid):
            g.redGrid.append([])
            g.blackGrid.append([])
            for cr, cb in zip(rr, rb):
                g.redGrid[-1].append(cr)
                g.blackGrid[-1].append(cb)

        g.redMoves = {m: None for m in self.redMoves}
        g.blackMoves = {m: None for m in self.blackMoves}

        return g

    def resetGame(self, gameBoard=None):
        """
        Bring the game to the default state at the beginning of the game
        :param gameBoard: A Game with the pieces in the state where this game should be set to,
            red still always moves first.
            Use None to have a normal game. Default None
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

        # keep track of all the moves that can be made
        #   the keys are the coordinates represented as an integer, determined by the method self.singlePos
        self.redMoves = {}
        self.blackMoves = {}

        if gameBoard is None:
            # fill in each row
            for y in range(fill):
                # fill in each spot in the row
                for x in range(self.width):
                    yy = self.height - 1 - y
                    # add red piece
                    self.spot(x, yy, (True, False), True)
                    # add black piece
                    self.spot(x, yy, (True, False), False)
        else:
            self.setBoard(gameBoard.toList(), True)
            self.checkWinConditions()

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
                self.spot(x, y, None, True)

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

    def toSinglePos(self, x, y):
        """
        Convert an (x, y) coordinate to a single number representing that location on the grid
        :param x: The x coordinate
        :param y: The y coordinate
        :return: The single number
        """
        return x + y * self.width

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

    def spot(self, x, y, value, red, update=True):
        """
        Set the value at a position in the grid
        :param x: The x coordinate
        :param y: The y coordinate
        :param value: The new value
        :param red: True if this should access from Red side, False otherwise
        :param update: True to also check the moves at this position to check for new moves of surrounding pieces
            False to not check, default True
        """

        oldSpace = self.gridPos(x, y, red)

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

        newSpace = self.gridPos(x, y, red)

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

        if update:
            self.updateMoves(x, y, red)

    def updateMoves(self, x, y, red):
        """
        Check all potential pieces located around a specified piece, and update the move dictionaries for both sides
        :param x: The x coordinate of the piece
        :param y: The y coordinate of the piece
        :param red: True if the coordinates are from red side, False for black side
        """

        # find all spaces that need to be updated
        spaces = [(x, y)]
        for i in range(8):
            spaces.append(movePos((x, y), moveIntToBoolList(i)))

        # determine if each space has moves
        for s in spaces:
            self.updateOneMove(s, red)

    def updateOneMove(self, s, red):
        """
        Update the moves list for a given space. Essentially, determine if a piece at a particular position
            can move, and if it can, update it's corresponding moves list
        :param s: The space to check
        :param red: True if s is from red's perspective, False for black's perspective
        """
        sx, sy = s
        if self.inRange(sx, sy):
            # if this is from red's side, then change the position directly in the redMoves dictionary
            #   otherwise use the opposite side, because s is relative to black side
            changeR = s if red else self.oppositeGrid(s)
            changeR = self.toSinglePos(changeR[0], changeR[1])
            # do the same, but in reverse for black side
            changeB = self.oppositeGrid(s) if red else s
            changeB = self.toSinglePos(changeB[0], changeB[1])

            # get the piece at the location of s
            sGrid = self.gridPos(sx, sy, red)

            # if the grid location is None, remove the location from the dictionaries
            if sGrid is None:
                dictRemove(self.redMoves, changeR)
                dictRemove(self.blackMoves, changeB)
            else:
                # determine if each space has moves
                hasMoves = self.canMovePos(s if sGrid[0] else self.oppositeGrid(s),
                                           red if sGrid[0] else not red)

                # if the space has no moves remove that space from both moves lists
                if not hasMoves:
                    dictRemove(self.redMoves, changeR)
                    dictRemove(self.blackMoves, changeB)

                # if the space is not empty, remove it from the opposite side's moves dictionary,
                #   and add it to the corresponding side's dictionary
                else:
                    # if red side and enemy, or black side and ally,
                    #   remove it from red's dictionary, add to black's dictionary
                    if red ^ sGrid[0]:
                        dictRemove(self.redMoves, changeR)
                        self.blackMoves[changeB] = None

                    # if black side and ally, or red side and enemy,
                    #   remove it from black's dictionary, add to red's dictionary
                    else:
                        self.redMoves[changeR] = None
                        dictRemove(self.blackMoves, changeB)

    def gridPos(self, x, y, red):
        """
        Get the value of a position in the grid
        :param x: The x coordinate
        :param y: The y coordinate
        :param red: True if this should get the value from red side, False to get it from black side
        :return: The value
        """
        return self.redGrid[y][x] if red else self.blackGrid[y][x]

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
        if self.canPlay(pos, modifiers, self.redTurn):
            # get position where the piece will move to
            newPos = movePos(pos, modifiers)
            # unpack that position
            newX, newY = newPos

            # determine the piece at the location which is making a move
            newPiece = self.gridPos(x, y, self.redTurn)

            # set the piece to a king if it reaches the end
            if newY == 0:
                newPiece = (newPiece[0], True)

            # set the grid positions for where the piece was, and where the piece moved to
            self.spot(newX, newY, newPiece, self.redTurn, False)
            self.spot(x, y, None, self.redTurn, False)

            # a capture has happened
            if jump:
                self.movesSinceLastCapture = 0
                mPos = movePos(pos, (left, forward, False))
                jX, jY = mPos
                self.spot(jX, jY, None, self.redTurn, False)
            else:
                mPos = None

            updates = calculateUpdatePieces(pos, newPos, mPos, modifiers)

            # update the moves list based on each position checked
            for m in updates:
                self.updateOneMove(m, self.redTurn)
            # update number of moves
            self.movesSinceLastCapture += 1
            self.moves += 1

            changeTurns = not jump
        else:
            changeTurns = False

        if changeTurns:
            self.redTurn = not self.redTurn

        # see if the game is over
        self.checkWinConditions()

        return changeTurns

    def canPlay(self, pos, modifiers, red):
        """
        Determine if a move can be made in the game.
        The move is based on the current turn of the game, ie. if red is moving,
            then the coordinates are from red's perspective
        :param pos: A 2-tuple (x, y) of positive integers the grid coordinates of the piece to move
        :param modifiers: A list of 3 booleans, (left, forward, jump)
            left: True to move left, False to move Right
            forward: True to move forward, False to move backwards
            jump: True if this move is a jump, False if it is a normal move
        :param red: True if this is from red's side, False otherwise
        :return True if the piece can make the move, False otherwise
        """
        x, y = pos
        left, forward, jump = modifiers

        if not self.validPiece(x, y, forward, red):
            return False

        # determine directions
        newX, newY = movePos(pos, modifiers)

        # check to see if movement for the new coordinate is in bounds
        if not self.inRange(newX, newY):
            return False
        # check if the piece jumped over is an enemy
        if jump:
            jX, jY = movePos(pos, (left, forward, False))
            pos = self.gridPos(jX, jY, red)
            if pos is None or pos[0]:
                return False

        # return if the new position to move to is empty
        return self.gridPos(newX, newY, red) is None

    def checkWinConditions(self):
        """
        See if the game is over, and set win to the appropriate value
        """
        # if the game is already over, no need to check
        if not self.win == E_PLAYING:
            return

        # if red has no pieces, black wins
        if self.redLeft == 0:
            self.win = E_BLACK_WIN
            return
        # if black has no pieces, red wins
        elif self.blackLeft == 0:
            self.win = E_RED_WIN
            return

        # see if no one can make any moves
        # check if the appropriate moves dictionary is empty
        #   this is done by checking if the current player's moves dictionary is empty
        #   noMoves will be evaluate to False if it is empty, True otherwise
        noMoves = len(self.redMoves if self.redTurn else self.blackMoves) == 0

        # if no one can move, or if no one has any pieces, or
        #   if too many moves have happened with no captures, it's a draw
        if noMoves:
            if self.redTurn:
                self.win = E_DRAW_NO_MOVES_RED
            else:
                self.win = E_DRAW_NO_MOVES_BLACK
        elif self.movesSinceLastCapture >= E_MAX_MOVES_WITHOUT_CAPTURE:
            self.win = E_DRAW_TOO_MANY_MOVES
        elif self.redLeft == 0 and self.blackLeft == 0:
            self.win = E_DRAW_NO_PIECES
        else:
            self.win = E_PLAYING

    def calculateMoves(self, s, red):
        """
        Given the grid coordinates of a square, determine the list of moves that can be played by that piece.
        :param s: The coordinates of a square
        :param red: True if the moves should be calculated from red side, False otherwise
        :return The list of moves, a list of 8, 2-tuples, (x, y) of moves that can be taken,
            or None if that move cannot be taken.
        """
        playMoves = []
        # 8 different possible moves
        for i in range(8):
            bins = moveIntToBoolList(i)
            # check if the move can be played
            if self.canPlay(s, bins, red):
                # determine the position of the move
                playMoves.append(movePos(s, bins))
            else:
                playMoves.append(None)
        return playMoves

    def canMovePos(self, pos, red):
        """
        Determine if a piece at a given grid position has any moves for the current player
        :param pos: The grid position
        :param red: True if the piece should be considered from red side, False for black sie
        :return: True if a piece at that position has at least one move, False otherwise
        """
        moves = self.calculateMoves(pos, red)

        for m in moves:
            if m is not None:
                return True
        return False

    def validPiece(self, x, y, forward, red):
        """
        Given a piece, determine if the piece is valid to move.
        If the piece is empty, then it cannot move.
        If the piece is not a king, then it cannot move backwards.
        If the piece is not an ally, then it cannot be moved. This assumes the piece is being obtained from the
            grid relative of that pieces turn
        :param x: The x coordinate of the piece to check
        :param y: The y coordinate of the piece to check
        :param forward: True if this piece is trying to move forward, False otherwise
        :param red: True if this piece should be looked at from red side, False for Black side
        :return: True if the piece can move, False otherwise
        """
        piece = self.gridPos(x, y, red)
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
    Convert an integer in the range [0, 7] to a list of 3 boolean values, corresponding to the binary representation
    :param i: The integer
    :return: The list of 3 boolean values
    """
    # not using loops or append because this is faster, and this method only needs to work for integers in range [0-7]
    num1 = i % 2 == 1
    i //= 2
    num2 = i % 2 == 1
    i //= 2
    num3 = i % 2 == 1
    return num3, num2, num1


def boolListToInt(bools):
    """
    Convert a list of 3 booleans into an integer in the range [0, 7]
    :param bools: The list of booleans
    :return: The integer
    """
    # not using loops for optimized speed at this size
    return 4 * bools[0] + 2 * bools[1] + 1 * bools[2]


def dictRemove(d, e):
    """
    Remove an element from a dictionary, or do nothing if the element is not in the dictionary
    :param d: The dictionary
    :param e: The element to remove
    """
    if e in d:
        d.pop(e)


def isDraw(win):
    """
    Determine if the given win value is a draw
    :param win: The win value
    :return: True if the win value is a draw, False otherwise
    """
    return E_DRAW_MIN <= win <= E_DRAW_MAX


def addDiagMoves(rightDiag, moveList, pos, down, up):
    """
    Helper method for Play. Add to moveList, all of the positions which can be moved on a diagonal
    :param rightDiag: True if this diagonal, in grid space, goes from lower left to upper right, False otherwise
    :param moveList: The list to add the moves
    :param pos: The position to start at
    :param down: True to add moves going down, False otherwise
    :param up: True to add moves going up, False otherwise
    """
    if up:
        moveList.append(movePos(pos, (not rightDiag, True, False)))
        moveList.append(movePos(pos, (not rightDiag, True, True)))
    if down:
        moveList.append(movePos(pos, (rightDiag, False, False)))
        moveList.append(movePos(pos, (rightDiag, False, True)))


def calculateUpdatePieces(pos, newPos, mPos, modifiers):
    """
    Helper method for Game.play
    Determine all of the positions that must be checked after a spot on
    the grid is changed, to ensure that the pieces around the changed square are updated with any
    changes to their possible moves.
    :param pos: The position of the piece before it was moved
    :param newPos: The position of the piece after it was moved
    :param mPos: The position of the piece that was jumped over, or None if a jump did not happen
    :param modifiers: The standard modifiers for how the piece moved, a 3-tuple of (left, forward, jump)
    :return: A list of all the positions that must be checked
    """

    # unpack tuples
    left, forward, jump = modifiers
    x, y = pos
    newX, newY = newPos

    # add the base positions to a list for updating moves lists
    updates = [newPos, pos]

    # determine if the move happened from bottom left to upper right, True
    #   or upper left to lower left, False
    rightDiag = left ^ forward

    # add the moves to check for the main diagonals of the new and old position
    addDiagMoves(not rightDiag, updates, newPos, True, True)
    addDiagMoves(not rightDiag, updates, pos, True, True)

    # add the moves to check for for the half diagonals
    small = (pos, newPos) if y < newY else (newPos, pos)
    small, big = small
    addDiagMoves(rightDiag, updates, big, True, False)
    addDiagMoves(rightDiag, updates, small, False, True)

    # if a capture has happened, update the diagonal on the piece that was jumped over
    if jump:
        updates.append(mPos)
        addDiagMoves(not rightDiag, updates, mPos, True, True)

    return updates


def stringifyPlayMove(pos, modifiers, name="game"):
    """
    A utility method for automating getting code for playing moves.
    Helpful for generating code for testing particular cases of moves made.
    Can be used with things like the GUI or moves made by the QModels to replicate exact board states
        without having to manually place every piece.
    Parameters work in the same way as are passed to Game.play and Game.canPlay
    :param pos: The position of the piece to move
    :param modifiers: A 3-tuple of the modifiers (left, forward, jump) for the piece to move
    :param name: The variable name of the game that this play method call will use
    :return A string representing the code used to make the move
    """
    return name + ".play(" + str(pos) + ", " + str(modifiers) + ")"
