from Checkers.ConvModel import *
from Checkers.Game import *
if USE_TENSOR_FLOW:
    from tensorflow.keras.models import load_model

import os.path as path
import os


# number of grids for input of a neural network for the game
Q_GAME_NUM_GRIDS = 4
# number of grids for input of a neural network for a piece in the game
Q_PIECE_NUM_GRIDS = 6
# the total number of actions a piece can take
Q_PIECE_NUM_ACTIONS = 8


class PieceEnvironment(Environment):
    """
    An Environment used to determine where a piece should move to.
    This Environment is incompatible with a QTable.
    This environment considers the move they take, and the next opponent move when determining rewards
    """

    def __init__(self, game, current=None, gameInner=None, pieceInner=None, enemyEnv=None):
        """
        Create a new Environment for determining which move a given piece should move
        :param game: The Checkers Game that the piece will exist

        :param current: A 2-tuple of the current grid coordinates of the piece that this Environment should control
            Default None, must be set to a valid tuple in order to use this Environment.
            The coordinates must be at a spot with a piece, otherwise this Environment will not work
        :param pieceInner: The inner layers of the Network used for controlling the piece movement,
            None to have no inner layers, default None. Should only be positive integers
        :param gameInner: The inner layers of the Network used for controlling the piece selection,
            None to have no inner layers, default None.  Should only be positive integers
        :param enemyEnv: The environment used to make enemy moves. Use None to make the same network used
            for ally and enemy moves. Default None
        """

        self.game = game
        self.gameEnv = GameEnvironment(self.game, self)
        if Q_USE_CONVOLUTIONAL_LAYERS:
            self.gameNetwork = ConvNetwork(self.game.area(), self.gameEnv, self.game, Q_GAME_NUM_GRIDS,
                                           inner=[] if gameInner is None else gameInner)
            self.internalNetwork = ConvNetwork(Q_PIECE_NUM_ACTIONS, self, self.game, Q_PIECE_NUM_GRIDS,
                                               inner=[] if pieceInner is None else pieceInner)
        else:
            self.gameNetwork = Network(self.game.area(), self.gameEnv,
                                       inner=[] if gameInner is None else gameInner)

            self.internalNetwork = Network(Q_PIECE_NUM_ACTIONS, self,
                                           inner=[] if pieceInner is None else pieceInner)

        self.enemyEnv = enemyEnv

        self.current = current

    def networkInputs(self):
        return self.game.area() * Q_PIECE_NUM_GRIDS

    def toNetInput(self):
        if self.current is None:
            return None
        return gameToNetInput(self.game, self.current)

    def currentState(self):
        return self.game

    def numStates(self):
        return self.networkInputs()

    def getEnemyEnv(self):
        """
        Determine the environment used by the enemy
        :return: The environment
        """
        return self if self.enemyEnv is None else self.enemyEnv

    def rewardFunc(self, s, a):
        # if a move cannot be made, return the reward for that
        if self.canTakeAction(a):
            return Q_REWARD_INVALID_ACTION

        # initial reward for making a move
        totalReward = 0

        # make a copy of the game and set it to the internal game objects
        newState = s.makeCopy()

        # keep track of the player being given this reward
        redTurn = newState.redTurn

        # make moves until it is the enemy's turn, or the game ends
        while redTurn == newState.redTurn and newState.win == E_PLAYING:
            r = self.oneActionReward(newState, a, redTurn)
            if r is None:
                break
            else:
                totalReward += r
            a = None

        # select the correct environment, depending on if an enemy environment exists
        env = self.getEnemyEnv()

        # continue to make moves, until it is again the original player's turn, or the game ends
        while not redTurn == newState.redTurn and newState.win == E_PLAYING:
            r = env.oneActionReward(newState, None, redTurn)
            if r is None:
                break
            else:
                totalReward += r

        return totalReward

    def oneActionReward(self, state, action, redTurn):
        """
        Determine the reward for taking the given action in the given state, with no further moves.
        The action is always taken from the perspective of the current turn of the internal game object.
        The state of the current game is always modified, a copy should be sent if the state should not be modified.
        :param state: The state where the given action should take place
        :param action: The action to take, None if an action must be determined
        :param redTurn: True if this action should be based on red side, False for black side.
            The reward returned is based on whose turn it is in the game, and this value.
            For example, if redTurn is True, and red is moving, then capturing a piece will return positive reward.
        :return: The reward for making the move, or None if no action could be taken
        """

        # TODO also need to make it possible for a player to train the network
        #   The environment should make a move and remember the state and action for that move
        #   Then when the player makes a move, that is the move used for determining the next
        #   part of the reward function, determining the punishment.
        #   Essentially, remember the reward for making the moves to make it the player's turn
        #   then add the punishment received for the player making their moves
        #   Once both values are determined, train the network with that state and action,
        #   using the total reward and punishment

        # save the original game
        oldGame = self.game
        self.game = state
        self.gameEnv.game = state
        oldCurrent = self.current

        # initialize reward for this action
        totalReward = 0

        # if the given action is None, then an action must be determined
        if action is None:
            # determine which enemy piece will move
            self.gameEnv.performAction(self.gameNetwork)

            # determine the direction that piece will move
            # if there is no valid network input, do not make an action
            netInput = self.toNetInput()
            # find the actual action
            if netInput is not None:
                action = self.internalNetwork.chooseAction(netInput, takeAction=self.canTakeAction)
            else:
                # This shouldn't ever be reached, because if self.toNetInput() returns None,
                #   then self.current must be None, which only should happen after
                #   self.gameEnv.performAction(self.gameNetwork) is called, but it should
                #   only set that if the game is over, so if that first move ended the game
                #   then this part of the code should never be reached
                # If this line is reached, then some error has happened
                action = None

        piecePos = self.current

        # if no action can be taken, then the game must be over, so do not take another move
        if action is not None:
            # find the modifiers for the action
            modifiers = moveIntToBoolList(action)

            # add the reward for the piece moving
            moveR = moveReward(self.game, piecePos, modifiers)
            if moveR is not None:
                totalReward += moveR
                # make the move
                self.game.play(piecePos, modifiers)

                # if the game ends, add reward for winning
                winReward = endGameReward(self.game.win, redTurn, self.game.moves)
                if winReward is not None:
                    totalReward += winReward
            else:
                # if no move reward was found, then there was no valid reward, so set the reward to None
                totalReward = None
        # if a move cannot be made, ensure win conditions are checked
        else:
            self.game.checkWinConditions()

        # put the game back to it's original state
        self.game = oldGame
        self.gameEnv.game = oldGame
        self.current = oldCurrent

        # return the final reward
        return totalReward

    def stateToPiece(self, s, pos):
        """
        Given a state, and coordinates, obtain the piece located on that position
        :param s: The state
        :param pos: A 2-tuple (x, y) of the position coordinate on the grid
        :return: The place on the grid, either None for empty square, or a 2-tuple of (ally, king)
        """

        x, y = pos
        return s[x + y * self.game.width]

    def canTakeAction(self, action):
        return self.game.canPlay(self.current, moveIntToBoolList(action), self.game.redTurn)

    def takeAction(self, action):
        if action is None:
            return
        bins = moveIntToBoolList(action)
        c = self.current
        if c is not None:
            self.game.play(c, bins)

    def performAction(self, qModel):
        self.gameEnv.performAction(self.gameNetwork)
        net = self.toNetInput()
        if net is not None:
            self.takeAction(qModel.chooseAction(net, self.canTakeAction))

    def trainMove(self):
        """
        Make a move in the game, and train the network based on that move
        :return The action taken by the PieceNetwork, None if no action can be taken
        """
        state = self.currentState().makeCopy()
        gameNetInput = self.gameEnv.toNetInput()
        action = self.gameNetwork.chooseAction(gameNetInput, takeAction=self.gameEnv.canTakeAction)
        if action is not None:
            self.gameNetwork.train(state, action, self.gameEnv.canTakeAction)
        else:
            return None

        self.gameEnv.performAction(self.gameNetwork)

        netInput = self.toNetInput()
        # do nothing if there is no valid input
        if netInput is not None:
            action = self.internalNetwork.chooseAction(netInput, takeAction=self.canTakeAction)
            self.internalNetwork.train(state, action, takeAction=self.canTakeAction)
            return action
        return None

    def playGame(self, printReward=False):
        """
        Play one game of checkers, and train the Q model stored in this environment
        :param printReward: True to print the reward obtained each time a move is made, False otherwise, default False
        :return: A 4-tuple, (redTotal, blackTotal, redMoves, blackMoves),
            he total reward from playing the game from either side, and number of moves in the game for either side
        """

        self.game.resetGame()

        redTotal, blackTotal, redMoves, blackMoves = 0, 0, 0, 0

        # play the game until it's over
        while self.game.win == E_PLAYING:
            turn = self.game.redTurn
            reward = self.playGameMove(printReward)
            if reward is None:
                break
            else:
                if turn:
                    redTotal += reward
                    redMoves += 1
                else:
                    blackTotal += reward
                    blackMoves += 1

        return redTotal, blackTotal, redMoves, blackMoves

    def playGameMove(self, printReward):
        """
        Utility used by play game. Make a single move in the process of playing the game, and train
            the network for making that move
        :param printReward: True to print thr reward gained from this move, False otherwise
        :return: The reward gained from this move
        """

        # make a copy the current state used for determining reward
        state = self.currentState()

        # train the GameEnvironment and make a move, get the the action taken
        action = self.trainMove()

        # if no action is found, then the game is over, end the game
        if action is None:
            return None
        # otherwise, perform the action by training with it
        else:
            # find the reward for the action
            reward = self.rewardFunc(state, action)
            if printReward:
                print("Reward this turn: " + str(reward))

            return reward

    def decayNetworks(self):
        """
        Apply the decay to both networks
        """
        self.internalNetwork.decayRates()
        self.gameNetwork.decayRates()

    def saveNetworks(self, pieceName, networkName):
        """
        Save both of the QNetwork models used by this PieceEnvironment.
        Files are saved relative to Constants.NETWORK_SAVES
        :param pieceName: The file name for the internalNetwork
        :param networkName: The file name for the gameNetwork
        :return True if the files were saved, False otherwise
        """

        if not path.isdir(NETWORK_SAVES):
            os.mkdir(NETWORK_SAVES)
        self.internalNetwork.net.save(NETWORK_SAVES + "/" + pieceName)
        self.gameNetwork.net.save(NETWORK_SAVES + "/" + networkName)

        return True

    def loadNetworks(self, pieceName, networkName):
        """
        Load in both of the QNetwork models used by this PieceEnvironment.
        Files are saved relative to Constants.NETWORK_SAVES
        :param pieceName: The file name for the internalNetwork
        :param networkName: The file name for the gameNetwork
        :return True if the files were loaded, False otherwise
        """
        try:
            self.internalNetwork.net = load_model(NETWORK_SAVES + "/" + pieceName)
            self.gameNetwork.net = load_model(NETWORK_SAVES + "/" + networkName)
            return True
        except (ImportError, IOError, OSError):
            return False


def moveReward(state, position, modifiers):
    """
    Helper method for rewardFunc. Determines the amount of reward when a piece moves
    :param state: The current state of the game
    :param position: The position of the piece to move
    :param modifiers: The modifiers defining how the piece moves
    :return: The total reward gained from moving, None if no valid pieces were given
    """

    reward = 0
    newPos = movePos(position, modifiers)
    x, y = position

    selectPos = state.gridPos(x, y, state.redTurn)
    # if there is no valid piece to move, then return no reward
    if selectPos is None:
        return None
    else:
        ally, king = selectPos

    # if it's a jump, add capture reward for appropriate piece
    if modifiers[2]:
        capturedPos = movePos(position, (modifiers[0], modifiers[1], False))
        x, y = capturedPos
        captured = state.gridPos(x, y, state.redTurn)
        if ally:
            reward += Q_PIECE_REWARD_K_CAPTURE if captured[1] else Q_PIECE_REWARD_N_CAPTURE
        else:
            reward += Q_PIECE_REWARD_K_CAPTURED if captured[1] else Q_PIECE_REWARD_N_CAPTURED

    # add movement reward if it is an ally piece
    else:
        reward += Q_PIECE_REWARD_MOVE if ally else Q_PIECE_REWARD_ENEMY_MOVE

    # add reward if the piece is kinged, meaning the piece is currently not a king, and it reaches the end
    if not king and newPos[1] == 0:
        reward += Q_PIECE_REWARD_KING if ally else Q_PIECE_REWARD_KINGED

    return reward


def endGameReward(win, redSide, moves):
    """
    Determine the reward for ending the game
    :param win: The Game win state
    :param redSide: True if from red's perspective, False otherwise.
        Meaning if red is playing, and red wins, then the reward is for winning,
        but if black wins, the reward is for losing
    :param moves: The number of moves last made
    :return: The reward for ending the game, None if the game is not over
    """
    # if the game is not over, no reward
    if win == E_PLAYING:
        return Q_PIECE_REWARD_PLAYING

    # find the reward for number of moves made
    reward = moves * Q_PIECE_REWARD_MOVES_FACTOR

    # if the game is a draw, return draw reward
    if isDraw(win):
        reward += Q_PIECE_REWARD_DRAW

    # if red won and red was playing, or black won and black was playing, add win reward
    elif redSide and win == E_RED_WIN or not redSide and win == E_BLACK_WIN:
        reward += Q_PIECE_REWARD_WIN

    # if red won and black was playing, or black won and red was playing, add lose reward
    elif redSide and win == E_BLACK_WIN or not redSide and win == E_RED_WIN:
        reward += Q_PIECE_REWARD_LOSE

    return reward


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

    def networkInputs(self):
        return self.game.area() * Q_GAME_NUM_GRIDS

    def toNetInput(self):
        return gameToNetInput(self.game, None)

    def currentState(self):
        return self.game

    def numStates(self):
        return self.networkInputs()

    def rewardFunc(self, s, a):
        # save current value for game
        oldCurrent = self.pieceEnv.current
        self.pieceEnv.current = self.game.singlePos(a)

        high = 0
        # get the values of each of the possible actions
        actions = self.pieceEnv.internalNetwork.getOutputs()[0]
        # for each action, if it can be taken, add that Q value to the total for the reward
        #   otherwise, add the punishment value for taking that action
        for i, act in enumerate(actions):
            if self.pieceEnv.canTakeAction(i):
                high += act
            else:
                high += Q_REWARD_INVALID_ACTION

        # reset current for game
        self.pieceEnv.current = oldCurrent
        return Q_GAME_REWARD_NO_ACTIONS if high is None else high

    def canTakeAction(self, action):
        x, y = self.game.singlePos(action)
        return self.game.canMovePos((x, y), self.game.redTurn)

    def performAction(self, qModel):
        action = qModel.chooseAction(self.toNetInput(), self.canTakeAction)
        self.takeAction(action)

    def takeAction(self, action):
        # convert the action into coordinates for a piece to move
        if action is not None:
            self.pieceEnv.current = self.game.singlePos(action)
        else:
            self.pieceEnv.current = None


def gameToNetInput(g, current):
    """
    Convert a Checkers Game object into a numpy array used for input of a Network for PieceEnvironment
    :param g: The Game object
    :param current: A 2-tuple (x, y) of the location of the piece that will be moved next.
        None to not include the grids representing controlled pieces
    :return: The numpy array
    """

    # TODO this code is probably a source of slowness in the runtime, find a way to reduce this runtime

    gridCount = Q_GAME_NUM_GRIDS if current is None else Q_PIECE_NUM_GRIDS
    if Q_USE_CONVOLUTIONAL_LAYERS:
        states = np.zeros((1, g.height, g.width, gridCount))
        grid = g.currentGrid()
        for j, r in enumerate(grid):
            for i, s in enumerate(r):
                if s is not None:
                    states[0][j][i][netInputIndex(s, current, i, j)] = 1
        return states
    else:
        # get the state of the environment
        state = g.toList()

        # set up an array which can be fed into a network
        size = g.area()
        states = np.zeros((1, size * gridCount), dtype=np.int)
        # go through each element in the state, and set the input array position, corresponding to the
        #   index of the state and condition of the state
        for i, s in enumerate(state):
            x, y = g.singlePos(i)
            if s is not None:
                states[0][netInputIndex(s, current, x, y) * size + y * g.width + x] = 1
        return states


def netInputIndex(s, current, x, y):
    """
    Helper function for gameToNetInput. Get the index of the list to update
    :param s: The piece at the position being looked at
    :param current: The currently selected piece, None if no piece is selected
    :param x: The x coordinate of the position being looked at
    :param y: The y coordinate of the position being looked at
    :return: The index of the list where this piece will be placed in the net input
    """
    # if the piece is an ally
    if s[0]:
        # if the piece is the one selected by Environment
        if current is not None and (x, y) == current:
            return 5 if s[1] else 4
        # if it's a normal piece
        else:
            return 1 if s[1] else 0
    else:
        return 3 if s[1] else 2
