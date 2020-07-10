import numpy as np

from Constants import *

if USE_TENSOR_FLOW:
    from tensorflow import keras
    import tensorflow as tf

    tf.CUDA_VISIBLE_DEVICES = 0, 1

import random
import abc


class QModel:
    """
    A generic object for creating a QModel.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, states, actions, environment, learnRate=0.1, discountRate=0.5, explorationRate=0.5):
        """
        Create a QModel with the given parameters
        :param states: The number of states
        :param actions: The number of actions, None if this model does not use states
        :param environment: The environment to use with this table for determining when actions can happen,
        and potential reward
        :param learnRate: The learning rate of the table
        :param discountRate: The discount rate of the table
        """
        self.states = states
        self.actions = actions

        self.environment = environment

        self.learnRate = learnRate
        self.discountRate = discountRate
        self.explorationRate = explorationRate

    def chooseAction(self, state, takeAction=None):
        """
        Choose an action to take, based on the current state.
            Can randomly be either the highest valued action, or a random action, depending on explorationRate
        :param state: The current state of the model
        :param takeAction: A function that determines if a particular action can be taken. None to not use.
            Must return True if the action can be taken, False otherwise.
            The function should take only one parameter, the action to be taken.
            It is assumed that at least one action can always be taken.
        :return: The action to take, None if no action can be taken
        """
        # get a list of all the rewards for each action in the current state
        actions = self.getActions(state)

        if takeAction is None:
            # randomly choose to either pick the index of the action with the highest value,
            #   or a random new action, thus selecting the direction
            if random.random() > self.explorationRate:
                action = actions.index(max(actions))
            else:
                action = random.randint(0, self.actions - 1)
        else:
            # get a list of all the valid actions
            actions = chooseElements(actions, keep=takeAction)
            if len(actions) == 0:
                return None

            # randomly choose to pick a random action, or the best available action
            if random.random() > self.explorationRate:
                # find the remaining action with the highest reward
                action = chooseHighestFromTuple(actions)[0]
            else:
                # randomly select an index of the remaining actions, then select the ID of that action
                action = actions[random.randint(0, len(actions) - 1)][0]

        return action

    def randomValidAction(self):
        """
        Pick a random valid action that can be taken by this QModel
        :return: The action as a numerical ID, or None if no action is possible
        """
        a = [0] * self.actions
        a = chooseElements(a, self.environment.canTakeAction)
        return None if a is None or len(a) == 0 else a[random.randint(0, len(a) - 1)][0]

    @abc.abstractmethod
    def getActions(self, s):
        """
        Get a list of all the q values for each action, based on the current state,
            in appropriate order based on action indexes
        :param s: The current state
        :return: The list of q values
        """
        return []

    @abc.abstractmethod
    def train(self, state, action, takeAction=None):
        """
        Modify the QModel to change based on the given states and actions. In the process of training,
            one step in the environment should be taken
        :param state: the state of the environment
        :param action: the action to take
        :param takeAction: A function that determines if a particular action can be taken. None to not use.
            Must return True if the action can be taken, False otherwise.
            The function should take only one parameter, the action to be taken.
            It is assumed that at least one action can always be taken.
        :return True if the function happened successfully, False otherwise
        """

    @abc.abstractmethod
    def updateLearningRate(self, newRate):
        """
        Update the learning rate of this QModel, this should also update any other objects that use a learning rate
        :param newRate: The new learning rate
        """

    @abc.abstractmethod
    def usesNetwork(self):
        """
        Determine if this QModel uses a Network input to choose an action
        :return: True if it uses a Network input, False if it uses a numerical input
        """
        return False


class Table(QModel):
    """
    A Q model that learns based on a Q Table
    """

    def __init__(self, actions, environment, learnRate=0.5, discountRate=0.5, explorationRate=0.5):
        """
        Create a Q table that will keep track of all of the Q values for actions and states
        :param actions: The number of actions
        :param environment: The model to use with this table for determining when actions can happen,
            and potential reward. This environment determines the number of states used by this table
        :param learnRate: The learning rate of the table
        :param discountRate: The discount rate of the table
        """
        super().__init__(environment.numStates(), actions, environment, learnRate, discountRate, explorationRate)

        self.qTable = None
        self.reset()

    def reset(self):
        """
        Reset the QTable to all zeros
        """
        self.qTable = np.zeros((self.states, self.actions))

    def train(self, state, action, takeAction=None):
        """
        Note: This implementation does not use takeAction
        """
        # take the action
        self.environment.takeAction(action)

        # get the new state after that action
        newState = self.environment.currentState()

        # apply bellman function to update QTable
        if SIMPLE_BELLMAN:
            # simplified bellman function
            self.qTable[state, action] = self.learnRate * (self.environment.rewardFunc(state, action) +
                                                           self.environment.maxState(newState, action))
        else:
            # complex bellman function
            self.qTable[state, action] = self.qTable[state, action] + self.learnRate * (
                    self.environment.rewardFunc(state, action) - self.qTable[state, action] +
                    self.discountRate * (max(self.qTable[newState]))
            )

        return True

    def getActions(self, s):
        return [self.qTable[s, i] for i in range(self.actions)]

    def updateLearningRate(self, newRate):
        self.learnRate = newRate

    def usesNetwork(self):
        return False


class Network(QModel):
    """
    A Q learning model that learns based on a feed forward neural network
    """

    def __init__(self, actions, environment, inner=None, learnRate=0.5, discountRate=0.5, explorationRate=0.5):
        """
        Create a Network for Q learning for training a model
        :param actions: The number of actions
        :param environment: The environment to use with this table for determining when actions can happen,
            and potential reward. This environment determines the number of states used by the network
        :param inner: The inner layers of the Network, None to have no inner layers, default None.
            Should only be positive integers
        :param learnRate: The learning rate of the Network
        :param discountRate: The discount rate of the Network
        :param explorationRate: The probability that a random action will be taken, rather than the optimal one
        """
        super().__init__(environment.networkInputs(), actions, environment, learnRate, discountRate, explorationRate)

        if inner is None:
            inner = []
        self.inner = inner

        self.net = None
        self.optimizer = None
        self.updateLearningRate(learnRate)

        self.initNetwork()

    def initNetwork(self):
        """
        Initialize the network to an unlearned, default state
        """

        # create a list of layers, initialized with the input layer as the input shape
        layers = [keras.layers.Dense(self.states, activation="sigmoid", use_bias=True,
                                     input_shape=(self.states,))]

        # add all remaining hidden layers
        if len(self.inner) > 0:
            for lay in self.inner:
                layers.append(keras.layers.Dense(lay, activation="sigmoid", use_bias=True))

        # create the output layer
        layers.append(keras.layers.Dense(self.actions, activation="linear", use_bias=True))

        # create the network object
        self.net = keras.Sequential(layers)

        # compile and finish building network
        self.net.compile(optimizer=self.optimizer,
                         loss=keras.losses.MeanSquaredError())

    def train(self, state, action, takeAction=None):
        # get the state of the game before the move happens
        inputs = self.getInputs()

        # get the outputs of the network at the current state
        # this means finding the Q values for each action in the current state
        outputs = np.array(self.getOutputs())

        # get the reward for taking the given action in the given state
        reward = self.environment.rewardFunc(state, action)

        # make next step in environment, meaning take the action
        self.environment.takeAction(action)

        # find Q values for that next state
        nextOutputs = self.getOutputs()

        # set the training output data values, copying the previous predictions
        expectedOut = outputs

        success = True

        # set the calculated Q value for the specific action taken
        # choose the highest reward
        if takeAction is None:
            maxOutput = np.max(nextOutputs)
        # otherwise, choose the highest reward with the action that can be taken
        else:
            availableActions = chooseElements(nextOutputs[0], takeAction)
            # if no actions are available, then return
            if len(availableActions) == 0:
                maxOutput = self.environment.rewardFunc(state, action)
                success = False
            else:
                maxOutput = chooseHighestFromTuple(availableActions)[1]

        if SIMPLE_BELLMAN:
            expectedOut[0, action] = reward + maxOutput * self.learnRate
        else:
            expectedOut[0, action] = expectedOut[0, action] + self.learnRate * (
                reward - expectedOut[0, action] +
                self.discountRate * maxOutput)

        # train the network on the newly expected Q values
        self.net.fit(inputs, expectedOut, verbose=0, use_multiprocessing=True, epochs=1, batch_size=None)

        # return that the training happened successfully
        return success

    def trainMultiple(self, inputs, outputs):
        """
        Train this Network based on a list of lists of input
        :param inputs: The input data
        :param outputs: The expected output data
        """
        self.net.fit(np.array(inputs), np.array(outputs),
                     verbose=0, use_multiprocessing=True, epochs=10, batch_size=None)

    def getOutputs(self):
        """
        Get the output values of the model
        :return: The output values as a numpy array
        """
        return self.net(self.getInputs())

    def getInputs(self):
        """
        Get the inputs for the network
        :return: The inputs as a numpy array to be fed into the network. All elements are 0,
            except for the element of the current state, which is 1
        """
        return self.environment.toNetInput()

    def getActions(self, s):
        # get the actions
        actions = self.net.predict(s, verbose=0)
        # convert the actions to a list
        return [a for a in actions[0]]

    def updateLearningRate(self, newRate):
        self.learnRate = newRate
        self.optimizer = keras.optimizers.RMSprop(learning_rate=self.learnRate)

    def usesNetwork(self):
        return True


class Environment:
    """
    A generic object for an environment.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def networkInputs(self):
        """
        Get the number of values used for input for a network
        :return: The number of values
        """
        return 0

    @abc.abstractmethod
    def toNetInput(self):
        """
        Convert the model into a 1D numpy array that can be fed into a network as inputs
        :return: the inputs
        """
        return np.zeros((1, 0))

    @abc.abstractmethod
    def currentState(self):
        """
        Get the current state of this model
        :return: the state
        """
        return 0

    @abc.abstractmethod
    def numStates(self):
        """
        Get the number of states in this environment
        :return: The number of states
        """
        return 0

    @abc.abstractmethod
    def rewardFunc(self, s, a):
        """
        Determine the reward for the given action during the given state
        :param s: The current state
        :param a: The current action
        :return: The reward
        """
        return 0

    @ abc.abstractmethod
    def takeAction(self, action):
        """
        Take the given action in the environment
        :param action: The action to take
        """

    @abc.abstractmethod
    def canTakeAction(self, action):
        """
        Determine if the given action can be taken, based on the current state of the Environment
        :param action: The action trying to be taken
        :return: True if the action can be taken, False otherwise
        """

    @abc.abstractmethod
    def performAction(self, qModel):
        """
        Using the given QModel, perform an action in this environment
        :param qModel: The QModel to use
        :return:
        """


class DummyGame(Environment):

    def __init__(self, grid, rewards=None, pos=(0, 0), sizeStates=True):
        """
        Create a dummy game for Q learning. This is a grid where moving to a new square gives different reward.
            Moving from one square to another is reduces reward
        :param grid: A 2D numpy array containing the values for entering the corresponding square.
        :param rewards: A list of the rewards for a corresponding action, none for default values,
            [move, good, bad, dead, win, do nothing]
        :param pos: A 2-tuple, (x, y), the starting position in the grid, default: (0, 0)
        :param sizeStates: True if the a state should just be based on the size of the grid, one state for each
            position of the game. Basically a normal way of using the states.
            False if a state should be a part of the grid, and the number of different grid types.
            Basically creating inputs of a grid of ones or zeros for each possible action.
            Default True

        """
        self.grid = grid
        self.sizeStates = sizeStates

        self.rewards = rewards
        if self.rewards is None:
            self.rewards = [D_MOVE, D_GOOD, D_BAD, D_DEAD, D_WIN, D_DO_NOTHING]

        self.defaultPos = pos
        self.x, self.y = pos

        self.moveHistory = []

    def pos(self, s):
        """
        Convert a state to a coordinate in the grid
        :param s: The state
        :return: A 2-tuple of (x, y) of the position
        """
        x = s % self.width()
        y = s // self.width()
        return x, y

    def state(self, x, y):
        """
        Convert grid coordinates to their corresponding state
        :param x: The x coordinate
        :param y: The y coordinate
        :return: The state
        """
        return x + y * self.width()

    def currentState(self):
        return self.state(self.x, self.y)

    def width(self):
        """
        Get the width of the grid
        :return: The width
        """
        return len(self.grid[0])

    def height(self):
        """
        Get the height of the grid
        :return: The height
        """
        return len(self.grid)

    def gridP(self, x, y):
        """
        Get the grid value at the given position
        :param x: The x position
        :param y: The y position
        :return: The grid value
        """
        return self.grid[y, x]

    def setGrid(self, x, y, a):
        """
        Set the given grid position to the given value
        :param x: The x position
        :param y: The y position
        :param a: The given value
        """
        self.grid[y, x] = a

    def takeAction(self, direction):
        """
        Move in the given direction if possible
        :param direction: The direction to move in, 0 = up, 1 = right, 2 = down, 3 = left
        :return: The new grid reward type if the move was successful, the type for doing nothing otherwise
        """
        oldX, oldY = self.x, self.y

        if direction == LEFT and self.x > 0:
            self.x -= 1
        if direction == RIGHT and self.x < self.width() - 1:
            self.x += 1
        if direction == UP and self.y > 0:
            self.y -= 1
        if direction == DOWN and self.y < self.height() - 1:
            self.y += 1

        if oldX == self.x and oldY == self.y:
            return CANT_MOVE

    def networkInputs(self):
        s = self.width() * self.height()
        return s if self.sizeStates else 5 * s

    def toNetInput(self):
        if self.sizeStates:
            inputs = np.zeros((1, self.numStates()))
            inputs[0][self.currentState()] = 1
            return inputs
        else:
            # create an array of appropriate size
            arr = np.zeros((1, self.networkInputs()))
            size = self.width() * self.height()

            # there are NUM_ACTIONS possibilities for each grid position
            for c in range(NUM_REWARD_SQUARES):
                # go through each row
                for i, y in enumerate(self.grid):
                    # go through each position in the row
                    for j, x in enumerate(y):
                        # get the position in the array
                        pos = c * size + i * self.width() + j
                        # if the id of the grid position matches the current grid position,
                        #   set the array to 1, 0 otherwise
                        arr[0][pos] = 1 if x == c else 0
            return arr

    def numStates(self):
        s = self.width() * self.height()
        if self.sizeStates:
            return s
        return s * NUM_ACTIONS

    def rewardFunc(self, s, a):
        # can't move, punish for corresponding punishment for not moving
        if a == CANT_MOVE:
            return self.rewards[DO_NOTHING]

        # get the position
        x, y = self.pos(s)

        # determine new grid position based on action
        if a == UP:
            y -= 1
        elif a == DOWN:
            y += 1
        elif a == LEFT:
            x -= 1
        elif a == RIGHT:
            x += 1

        # if the action moved outside the grid, return the reward for do nothing
        if x < 0 or x > self.width() - 1 or y < 0 or y > self.height() - 1:
            return self.rewards[DO_NOTHING]

        # return the reward in the square, along with the cost of moving
        return self.rewards[self.gridP(x, y)] - MOVE_COST

    def canTakeAction(self, action):
        canMove = not (
                action == CANT_MOVE or
                (action == UP and self.y < 1) or
                (action == DOWN and self.y > self.height() - 2) or
                (action == LEFT and self.x < 1) or
                (action == RIGHT and self.x > self.width() - 2)
        )

        if TRACK_MOVE_HISTORY:
            if not canMove:
                return canMove

            pos = [self.x, self.y]
            if action == UP:
                pos[1] -= 1
            elif action == DOWN:
                pos[1] += 1
            elif action == LEFT:
                pos[0] -= 1
            elif action == RIGHT:
                pos[0] += 1
            for h in self.moveHistory:
                if h[0] == pos[0] and h[1] == pos[1]:
                    return False
            return True

        else:
            return canMove

    def performAction(self, qModel):
        action = qModel.chooseAction(self.currentState(), takeAction=self.canTakeAction)
        self.takeAction(action)

    def reset(self):
        """
        Reset the game to a default state
        """
        self.x, self.y = self.defaultPos
        self.moveHistory = []

    def playGame(self, qModel, learn=False, printPos=False):
        """
        Play the game using the given QModel
        :param qModel: The table or network to use for making decisions
        :param learn: True to also update the given qTable as this model learns, False otherwise, default False
        :param printPos: True if the position should be printed after each move, False otherwise, default False
        :return: The total reward gained from playing the game
        """

        # reset them model
        self.reset()
        moves = 0
        total = 0

        square = self.gridP(self.x, self.y)

        # run the model until a set number of moves, or the game ends
        while not square == WIN and not square == DEAD and moves < MAX_MOVES:
            # add to the move history
            if TRACK_MOVE_HISTORY:
                self.moveHistory.append((self.x, self.y))

            # get the state before making an action
            state = self.state(self.x, self.y)

            # pick a direction
            if ENABLE_DO_NOTHING:
                takeA = None
            else:
                takeA = self.canTakeAction
            action = qModel.chooseAction(
                self.toNetInput() if qModel.usesNetwork() else state,
                takeAction=takeA)

            if action is not None:
                # update the QModel with training
                if learn:
                    if not qModel.train(state, action, takeAction=takeA):
                        return total + self.rewardFunc(state, action) + D_STUCK

                # play the game normally
                else:
                    self.takeAction(action)

                # add to the total reward
                total += self.rewardFunc(state, action)

                # print the position
                if printPos:
                    print("(x: " + str(self.x) + ", y: " + str(self.y) + ")")

            # determine the value of the current grid square and account for making a move
            square = self.gridP(self.x, self.y)
            moves += 1

        return total


def chooseElements(arr, keep):
    """
    Take a list of elements, and remove certain elements determined by keep.
    :param arr: The list of elements
    :param keep: A function returning True if an element in keep should be kept, False otherwise
    :return: The list of elements with only valid elements
    """
    return [(i, a) for i, a in enumerate(arr) if keep(i)]


def chooseHighestFromTuple(arr):
    """
    Pick the id of the highest element of a list of tuples of the form (id, key),
        where they key determines which value is the highest
    :param arr: The array of elements
    :return: A tuple of the form (id, key) of the element with the highest key
    """
    high = 0
    for i, a in enumerate(arr):
        if a[1] > arr[high][1]:
            high = i
    return arr[high]
