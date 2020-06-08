from learning.QLearn import *

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

# constants for printing the game
P_ALLY = "[A"
P_ENEMY = "[E"
P_NORMAL = " ]"
P_KING = "K]"
P_EMPTY = "[  ]"

# constants for Q Learning models
Q_GAME_NUM_GRIDS = 4

Q_PIECE_NUM_GRIDS = 6
Q_PIECE_NUM_ACTIONS = 8

# TODO this may need to be defined in a better way
Q_PIECE_ID_MOVE = 0
Q_PIECE_ID_N_CAPTURE = 1
Q_PIECE_ID_K_CAPTURE = 2
Q_PIECE_ID_N_CAPTURED = 3
Q_PIECE_ID_K_CAPTURED = 4
Q_PIECE_ID_KING = 5
Q_PIECE_ID_KINGED = 6
Q_PIECE_ID_WIN = 7
Q_PIECE_ID_LOSE = 8
Q_PIECE_ID_DRAW = 9

Q_PIECE_REWARD_MOVE = 1
Q_PIECE_REWARD_N_CAPTURE = 8
Q_PIECE_REWARD_K_CAPTURE = 12
Q_PIECE_REWARD_N_CAPTURED = -3
Q_PIECE_REWARD_K_CAPTURED = -6
Q_PIECE_REWARD_KING = 5
Q_PIECE_REWARD_KINGED = -2
Q_PIECE_REWARD_WIN = 100
Q_PIECE_REWARD_LOSE = -200
Q_PIECE_REWARD_DRAW = -50
Q_PIECE_REWARDS = [
    Q_PIECE_REWARD_MOVE,
    Q_PIECE_REWARD_N_CAPTURE,
    Q_PIECE_REWARD_K_CAPTURE,
    Q_PIECE_REWARD_N_CAPTURED,
    Q_PIECE_REWARD_K_CAPTURED,
    Q_PIECE_REWARD_KING,
    Q_PIECE_REWARD_KINGED,
    Q_PIECE_REWARD_WIN,
    Q_PIECE_REWARD_LOSE,
    Q_PIECE_REWARD_DRAW
]


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

        # reset number of moves
        self.movesSinceLastCapture = 0

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
        Red moves first.
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
        if self.redLeft == 0:
            self.win = E_BLACK_WIN
        elif self.blackLeft == 0:
            self.win = E_RED_WIN
        elif (self.redLeft == 0 and self.blackLeft == 0) or noMoves:
            self.win = E_DRAW
        # if too many moves have happened with no captures, the game is a draw
        elif self.movesSinceLastCapture >= E_MAX_MOVES_WITHOUT_CAPTURE:
            self.win = E_DRAW
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
            if self.canPlay(s, bins):
                # determine the position of the move
                move = movePos(s, bins)
                playMoves.append(move)
            else:
                playMoves.append(None)
        return playMoves

    def canMovePos(self, pos):
        """
        Determine if a piece at a given grid position has any moves
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


class PieceEnvironment(Environment):
    """
    An Environment used to determine where a piece should move to.
    This Environment is incompatible with a QTable.
    This environment considers the move they take, and the next opponent move when determining rewards
    """

    def __init__(self, game, current=None, inner=None, learnRate=0.5, discountRate=0.5, explorationRate=0.5):
        """
        Create a new Environment for determining which move a given piece should move
        :param game: The Checkers Game that the piece will exist

        :param current: A 2-tuple of the current grid coordinates of the piece that this Environment should control
            Default None, must be set to a valid tuple in order to use this Environment.
            The coordinates must be at a spot with a piece, otherwise this Environment will not work
        :param inner: The inner layers of the Network used for controlling the game, None to have no inner layers,
            default None.  Should only be positive integers
        :param learnRate: The learning rate of the Network, for the Network used for controlling the game
        :param discountRate: The discount rate of the Network, for the Network used for controlling the game
        :param explorationRate: The probability that a random action will be taken, rather than the optimal one,
            for the Network used for controlling the game
        """
        self.game = game
        self.gameEnv = GameEnvironment(self.game, self)
        self.gameNetwork = Network(self.game.area(), self.gameEnv,
                                   inner=[] if inner is None else inner,
                                   learnRate=learnRate, discountRate=discountRate, explorationRate=explorationRate)
        self.current = current

    def stateSize(self):
        # 6 times the grid area, 1 grid for each piece type:
        #   ally normal, ally king, enemy normal, enemy king, controlled normal, controlled king
        return self.game.area() * Q_PIECE_NUM_GRIDS

    def toState(self):
        # states = np.zeros((1, self.stateSize()), dtype=np.int)
        # g = self.game
        #
        # size = g.area()
        # grid = g.currentGrid()
        #
        # for j, r in enumerate(grid):
        #     for i, c in enumerate(r):
        #         # only proceed if a piece exists
        #         if c is not None:
        #             # if the piece is an ally
        #             if c[0]:
        #                 # if the piece is the one selected by Environment
        #                 if (i, j) == self.current:
        #                     index = 5 if c[1] else 4
        #                 # if it's a normal piece
        #                 else:
        #                     index = 1 if c[1] else 0
        #             else:
        #                 index = 3 if c[1] else 2
        #             states[0][index * size + j * g.width + i] = 1
        #
        # return states

        # TODO is this right?
        state = self.currentState()
        states = np.zeros((1, self.stateSize()), dtype=np.int)
        g = self.game
        size = g.area()
        for i, s in enumerate(state):
            x, y = self.gameEnv.actionToPos(i)
            if s is not None:
                # if the piece is an ally
                if s[0]:
                    # if the piece is the one selected by Environment
                    if (x, y) == self.current:
                        index = 5 if s[1] else 4
                    # if it's a normal piece
                    else:
                        index = 1 if s[1] else 0
                else:
                    index = 3 if s[1] else 2
                states[0][index * size + y * g.width + x] = 1
        return states

    def currentState(self):
        grid = self.game.currentGrid()
        vals = []
        # TODO make this code efficient
        for r in grid:
            for c in r:
                vals.append(c)

        return vals

    def numStates(self):
        return self.stateSize()

    def rewardFunc(self, s, a):
        # TODO determine reward for taking the given action

        # TODO determine the punishment received for the other player making a move
        #   OR? Do the punishments come from the other player making a move?
        #   So find the reward and punishment for both sides, and apply both of them?

        totalReward = 0

        bins = moveIntToBoolList(a)
        newPos = movePos(self.current, bins)

        # if it's a jump, add capture reward for appropriate piece
        if bins[2]:
            capturedPos = movePos(self.current, (bins[0], bins[1], False))
            captured = self.stateToPiece(s, capturedPos)
            totalReward += Q_PIECE_REWARD_K_CAPTURE if captured[1] else Q_PIECE_REWARD_N_CAPTURE

        # otherwise, add move reward
        else:
            totalReward += Q_PIECE_REWARD_MOVE

        # if it lands on the end, add king reward
        if newPos[1] == 0:
            totalReward += Q_PIECE_REWARD_KING

        # if the game ends
        #   in a win, add win reward
        #   in a draw, add draw reward
        #   in a loss, add loss reward

        # calculate reward for the enemy move?
        #   this should be from the perspective of the opponent
        #   assuming they take the same action that this environment would?
        #   So how to know what the next move would be?

        # take the given action, in a copy of the game?
        #   will want to minimize calls to this function then

        # if piece is kinged, add kinged punishment

        # if a piece is captured, add captured punishment for appropriate piece

        # if the game ends
        #   in a win, add win reward
        #   in a draw, add draw reward
        #   in a loss, add loss reward

        return totalReward

    def stateToPiece(self, s, pos):
        """
        Given a state, and coordinates, obtain the piece located on that position
        :param s: The state
        :param pos: A 2-tuple (x, y) of the position coordinate on the grid
        :return: The place on the grid, either None for empty square, or a 2-tuple of (ally, king)
        """

        x, y = pos
        piece = s[x + y * self.game.width]
        if piece is None:
            return None

        return piece

    def canTakeAction(self, action):
        return self.game.canPlay(self.current, moveIntToBoolList(action))

    def takeAction(self, action):
        bins = moveIntToBoolList(action)
        c = self.current
        self.game.play(c, bins)

    def performAction(self, qModel):
        action = self.gameNetwork.chooseAction(self.currentState(), takeAction=self.gameEnv.canTakeAction)
        self.gameEnv.takeAction(action)
        self.takeAction(qModel.chooseAction(self.currentState(), self.canTakeAction))

    def playGame(self, qModel, printReward=False):
        """
        Play one game of checkers, and train the given Q model as it plays
        :param qModel: The QModel to train with this method
        :param printReward: True to print the reward obtained each time a move is made, False otherwise, default False
        :return: A 2-tuple, (total, moves), the total reward from playing the game, and number of moves in the game
        """

        self.game.resetGame()

        total = 0
        moves = 0

        # play the game until it's over
        while self.game.win == E_PLAYING:

            # select a piece for the AI to play
            self.gameEnv.performAction(self.gameNetwork)

            # get the current state
            state = self.currentState()

            # determine the action for that piece to take
            action = qModel.chooseAction(state, takeAction=self.canTakeAction)

            # if no action is found, then the game is over, end the game
            if action is None:
                break
            # otherwise, perform the action by training with it
            else:
                # find the reward for the action
                reward = self.rewardFunc(state, action)
                if printReward:
                    print("Reward this turn: " + str(reward))
                total += reward
                qModel.train(state, action, takeAction=self.canTakeAction)

                # keep track of the total moves made
                moves += 1

        return total, moves


class GameEnvironment(Environment):
    """
    An Environment used to determine which piece in a Game should be moved
    """

    def __init__(self, game, pieceEnv):
        """
        Create a new Environment for determining which piece should move in a given Checkers Game
        :param game: The Checkers Game that the piece will exist
        :param pieceEnv: The PieceEnvironment used by this GameEnvironment
        """
        self.game = game
        self.pieceEnv = pieceEnv

    def stateSize(self):
        return self.game.area() * Q_GAME_NUM_GRIDS

    def toState(self):
        states = np.zeros((1, self.stateSize()), dtype=np.int)
        g = self.game

        size = g.area()
        grid = g.currentGrid()

        for j, r in enumerate(grid):
            for i, c in enumerate(r):
                # only proceed if a piece exists
                if c is not None:
                    # if the piece is an ally
                    if c[0]:
                        index = 1 if c[1] else 0
                    else:
                        index = 3 if c[1] else 2
                    states[0][index * size + j * g.width + i] = 1
        return states

    def currentState(self):
        raise TypeError("This Environment is incompatible with the QModel being used")

    def numStates(self):
        return self.stateSize()

    def rewardFunc(self, s, a):
        pos = self.actionToPos(a)

        # Take all possible actions from pos, and return the one with the highest Q value
        actions = self.game.calculateMoves(pos)
        high = None
        for act in actions:
            if act is not None:
                reward = self.pieceEnv.rewardFunc(s, act)
                if high is None or high < reward:
                    high = reward
        return 0 if high is None else high

    def canTakeAction(self, action):
        x, y = self.actionToPos(action)
        return self.game.canMovePos((x, y))

    def performAction(self, qModel):
        action = qModel.chooseAction(0, self.canTakeAction)
        self.takeAction(action)

    def actionToPos(self, action):
        """
        Convert an action in the range [0, game.area() - 1] to a grid position
        :param action: The action
        :return: A 2-tuple (x, y) of the position
        """
        return action % self.game.width, action // self.game.width

    def takeAction(self, action):
        # convert the action into coordinates for a piece to move
        self.pieceEnv.current = self.actionToPos(action)


def moveIntToBoolList(i):
    """
    Convert an integer in the range [0-7] to a list of 3 boolean values, corresponding to the binary representation
    :param i:
    :return:
    """
    return [b == '1' for b in "{0:03b}".format(i)]
