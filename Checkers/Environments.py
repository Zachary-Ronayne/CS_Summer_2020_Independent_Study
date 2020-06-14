from learning.QLearn import *
from Checkers.Game import *
if USE_TENSOR_FLOW:
    from tensorflow.keras.models import load_model

import os.path as path
import os

# constants for Q Learning models
# number of grids for input of a neural network for the game
Q_GAME_NUM_GRIDS = 4

# reward for when the game cannot select any pieces to move
Q_GAME_REWARD_NO_ACTIONS = 0

# number of grids for input of a neural network for a piece in the game
Q_PIECE_NUM_GRIDS = 6
# the total number of actions a piece can take
Q_PIECE_NUM_ACTIONS = 8

# reward when an ally piece moves
Q_PIECE_REWARD_MOVE = 1
# reward when an enemy piece moves
Q_PIECE_REWARD_ENEMY_MOVE = 0
# reward when a normal enemy piece is captured
Q_PIECE_REWARD_N_CAPTURE = 8
# reward when a king enemy piece is captured
Q_PIECE_REWARD_K_CAPTURE = 12
# reward when a normal ally piece is captured
Q_PIECE_REWARD_N_CAPTURED = -3
# reward when a king ally piece is captured
Q_PIECE_REWARD_K_CAPTURED = -6
# reward when an ally piece becomes a king
Q_PIECE_REWARD_KING = 5
# reward when an enemy piece becomes a king
Q_PIECE_REWARD_KINGED = -2
# reward for winning the game
Q_PIECE_REWARD_WIN = 100
# reward for losing the game
Q_PIECE_REWARD_LOSE = -200
# reward for drawing the game
Q_PIECE_REWARD_DRAW = -50
# reward for the game being still in progress
Q_PIECE_REWARD_PLAYING = 0
# this value is multiplied by the total number of moves, and added to the reward when the game ends
Q_PIECE_REWARD_MOVES_FACTOR = -1


class PieceEnvironment(Environment):
    """
    An Environment used to determine where a piece should move to.
    This Environment is incompatible with a QTable.
    This environment considers the move they take, and the next opponent move when determining rewards
    """

    def __init__(self, game, current=None, gameInner=None, pieceInner=None):
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
        """
        self.game = game
        self.gameEnv = GameEnvironment(self.game, self)
        self.gameNetwork = Network(self.game.area(), self.gameEnv,
                                   inner=[] if gameInner is None else gameInner)

        self.internalNetwork = Network(Q_PIECE_NUM_ACTIONS, self,
                                       inner=[] if pieceInner is None else pieceInner)

        self.current = current

    def networkInputs(self):
        return self.game.area() * Q_PIECE_NUM_GRIDS

    def toNetInput(self):
        if self.current is None:
            return None
        return gameToNetInput(self.game, self.current)

    def currentState(self):
        return self.game.toList()

    def numStates(self):
        return self.networkInputs()

    def rewardFunc(self, s, a):
        # TODO reward function is applying the reward for losing way too often
        #   probably need to rework how the function gives reward,
        #   making sure it's consistent regardless of which side is played from
        #  reward for losing a game should only apply at most once per game
        #   because once that action happens, then there can be no more rewards
        #  It looks like the big negative numbers don't happen where there is a draw

        oldGame = self.game

        totalReward = 0

        # determine the modifiers for the given action
        modifiers = moveIntToBoolList(a)

        # get the position of the piece to move
        piecePos = self.current

        # find the reward for the ally moving
        totalReward += self.moveReward(s, piecePos, modifiers)

        # make the move in a copy of the game
        redTurn = self.game.redTurn
        newGame = self.game.makeCopy()

        newGame.play(piecePos, modifiers)

        # if the game ends, add reward
        winReward = endGameReward(newGame.win, redTurn, newGame.moves)
        if winReward is not None:
            return totalReward + winReward

        # calculate reward for the enemy move?
        #   this should be from the perspective of the opponent
        #   assuming they take the same action that this environment would?
        #   So how to know what the next move would be?

        # determine which enemy piece will move
        # save the old game and current values
        self.game = newGame
        self.gameEnv.game = newGame
        oldCurrent = piecePos
        # find the actual position
        self.gameEnv.performAction(self.gameNetwork)
        piecePos = self.current

        # determine the direction that piece will move
        # find the actual action
        action = self.internalNetwork.chooseAction(self.toNetInput(), takeAction=self.canTakeAction)
        # find the modifiers for the action

        # if no action can be taken, then the game must be over, so do not take another move
        if action is not None:
            modifiers = moveIntToBoolList(action)

            # add the reward for the enemy moving
            totalReward += self.moveReward(self.currentState(), piecePos, modifiers)
            # make the enemy move
            self.game.play(piecePos, modifiers)

            # if the game ends, add reward
            winReward = endGameReward(self.game.win, redTurn, self.game.moves)
            if winReward is not None:
                totalReward += winReward

        # put the game object back to normal
        self.game = oldGame
        self.gameEnv.game = oldGame
        self.current = oldCurrent

        return totalReward

    def moveReward(self, state, position, modifiers):
        """
        Helper method for rewardFunc. Determines the amount of reward when a piece moves
        :param state: The current state of the game
        :param position: The position of the piece to move
        :param modifiers: The modifiers defining how the piece moves
        :return: The total reward gained from moving
        """
        reward = 0
        newPos = movePos(position, modifiers)
        ally, king = self.stateToPiece(state, position)

        # if it's a jump, add capture reward for appropriate piece
        if modifiers[2]:
            capturedPos = movePos(position, (modifiers[0], modifiers[1], False))
            captured = self.stateToPiece(state, capturedPos)
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
        return self.game.canPlay(self.current, moveIntToBoolList(action))

    def takeAction(self, action):
        if action is None:
            return
        bins = moveIntToBoolList(action)
        c = self.current
        if c is not None:
            self.game.play(c, bins)

    def performAction(self, qModel):
        self.gameEnv.performAction(self.gameNetwork)
        self.takeAction(qModel.chooseAction(self.toNetInput(), self.canTakeAction))

    def trainMove(self):
        """
        Make a move in the game, and train the network based on that move
        """
        self.gameEnv.performAction(self.gameNetwork)
        state = self.currentState()
        netInput = self.toNetInput()
        # do nothing if there is no valid input
        if netInput is not None:
            action = self.internalNetwork.chooseAction(netInput, takeAction=self.canTakeAction)
            self.internalNetwork.train(state, action, takeAction=self.canTakeAction)

    def playGame(self, printReward=False):
        """
        Play one game of checkers, and train the Q model stored in this environment
        :param printReward: True to print the reward obtained each time a move is made, False otherwise, default False
        :return: A 2-tuple, (total, moves), the total reward from playing the game, and number of moves in the game
        """

        self.game.resetGame()

        total = 0

        # play the game until it's over
        while self.game.win == E_PLAYING:

            # select a piece for the AI to play
            self.gameEnv.performAction(self.gameNetwork)

            # get the current state
            state = self.currentState()

            # end the game if there is no valid input for the neural network
            netInput = self.toNetInput()
            if netInput is None:
                break

            # determine the action for that piece to take
            action = self.internalNetwork.chooseAction(netInput, takeAction=self.canTakeAction)

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
                self.internalNetwork.train(state, action, takeAction=self.canTakeAction)

        moves = self.game.moves

        return total, moves

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
    if win == E_DRAW:
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
        return self.game.toList()

    def numStates(self):
        return self.networkInputs()

    def rewardFunc(self, s, a):
        pos = self.game.singlePos(a)

        # Take all possible actions from pos, and return the one with the highest Q value
        actions = self.game.calculateMoves(pos)
        high = None
        for act in actions:
            if act is not None:
                reward = self.pieceEnv.rewardFunc(s, act)
                if high is None or high < reward:
                    high = reward
        return Q_GAME_REWARD_NO_ACTIONS if high is None else high

    def canTakeAction(self, action):
        x, y = self.game.singlePos(action)
        return self.game.canMovePos((x, y))

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

    # get the state of the environment
    state = g.toList()

    # set up an array which can be fed into a network
    size = g.area()
    gridCount = Q_GAME_NUM_GRIDS if current is None else Q_PIECE_NUM_GRIDS
    states = np.zeros((1, size * gridCount), dtype=np.int)
    # go through each element in the state, and set the input array position, corresponding to the
    #   index of the state and condition of the state
    for i, s in enumerate(state):
        x, y = g.singlePos(i)
        if s is not None:
            # if the piece is an ally
            if s[0]:
                # if the piece is the one selected by Environment
                if current is not None and (x, y) == current:
                    index = 5 if s[1] else 4
                # if it's a normal piece
                else:
                    index = 1 if s[1] else 0
            else:
                index = 3 if s[1] else 2
            states[0][index * size + y * g.width + x] = 1
    return states
