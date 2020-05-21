import numpy as np
import tensorflow as tf
from tensorflow import keras

import random
import abc

from Constants import *


class QModel:
    """
    A generic object for creating a QModel.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, states, actions, environment, learnRate=0.5, discountRate=0.5, explorationRate=0.5):
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

    def chooseAction(self, state):
        """
        Choose an action to take, based on the current state.
            Can randomly be either the highest valued action, or a random action, depending on explorationRate
        :param state: The current state of the model
        :return: The action to take
        """
        # get a list of all the rewards for each action in the current state
        actions = self.getActions(state)

        # randomly choose to either pick the index of the action with the highest value,
        #   or a random new action, thus selecting the direction
        if random.random() > self.explorationRate:
            action = actions.index(max(actions))
        else:
            action = random.randint(0, self.actions)

        return action

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
    def train(self, oldS, oldA, s, a):
        """
        Modify the QModel to change based on the given states and actions
        :param oldS: the old state
        :param oldA: the old action
        :param s: The next state to go to
        :param a: The action taken
        """
        pass


class Table(QModel):
    """
    A Q model that learns based on a Q Table
    """

    def __init__(self, states, actions, environment, learnRate=0.5, discountRate=0.5, explorationRate=0.5):
        """
        Create a Q table that will keep track of all of the Q values for actions and states
        :param states: The number of states
        :param actions: The number of actions
        :param environment: The model to use with this table for determining when actions can happen,
            and potential reward
        :param learnRate: The learning rate of the table
        :param discountRate: The discount rate of the table
        """
        super().__init__(states, actions, environment, learnRate, discountRate, explorationRate)

        self.qTable = None
        self.reset()

    def reset(self):
        """
        Reset the QTable to all zeros
        """
        self.qTable = np.zeros((self.states, self.actions))

    def train(self, oldS, oldA, s, a):
        if SIMPLE_BELLMAN:
            # simplified bellman function
            self.qTable[oldS, oldA] = self.learnRate * (self.environment.rewardFunc(oldS, oldA) +
                                                        self.environment.maxState(s, a))
        else:
            # complex bellman function
            self.qTable[oldS, oldA] = self.qTable[oldS, oldA] + self.learnRate * (
                    self.environment.rewardFunc(oldS, oldA) - self.qTable[oldS, oldA] +
                    self.discountRate * (max(self.qTable[s]))
            )

    def getActions(self, s):
        return [self.qTable[s, i] for i in range(4)]


class Network(QModel):
    """
    A Q learning model that learns based on a feed forward neural network
    """

    def __init__(self, states, actions, environment, inner=None, learnRate=0.5, discountRate=0.5, explorationRate=0.5):
        """
        Create a Network for Q learning for training a model
        :param states: The number of states
        :param actions: The number of actions
        :param environment: The environment to use with this table for determining when actions can happen,
            and potential reward
        :param inner: The inner layers of the Network, None to have no inner layers, default None.
            Should only be positive integers
        :param learnRate: The learning rate of the table
        :param discountRate: The discount rate of the table
        """
        super().__init__(states, actions, environment, learnRate, discountRate, explorationRate)

        if inner is None:
            inner = []
        self.inner = inner
        self.net = None
        self.initNetwork()

    def initNetwork(self):
        """
        Initialize the network to an unlearned, default state
        """

        # TODO use learning rate and discount rate

        # TODO fix this error message by reworking code
        # WARNING:tensorflow:From C:\Users\zrona\.Zachary\Python Programs\CS_Summer_2020_Independent_Study
        # \venv\lib\site-packages\tensorflow\python\ops\resource_variable_ops.py:1666:
        # calling BaseResourceVariable.__init__ (from tensorflow.python.ops.resource_variable_ops) with
        # constraint is deprecated and will be removed in a future version.
        # Instructions for updating:
        # If using Keras pass *_constraint arguments to layers.

        # turn off eager mode
        tf.compat.v1.disable_eager_execution()

        # create input layer
        layers = [keras.layers.InputLayer(input_shape=(self.environment.stateSize(),))]

        # add all hidden layers
        for lay in self.inner:
            # create the layer
            layer = keras.layers.Dense(lay, activation="sigmoid", use_bias=True)
            # add the layer
            layers.append(layer)

        # TODO test this out with using a linear activation function, see if it can make it work
        #   also look at the actual outputs it gives, and see what happens
        # create the output layer
        layer = keras.layers.Dense(self.actions, activation="sigmoid", use_bias=True)
        # add the layer
        layers.append(layer)

        # put the final network together
        self.net = keras.Sequential(layers)

        # TODO why are the outputs all nan?

        # account for the size of the output layer
        biases = self.inner
        biases.append(self.actions)

        # set all weights amd biases to zero
        for bias, lay in zip(biases, layers[1:]):
            lay.set_weights([
                np.zeros(np.array(lay.get_weights()[0]).shape),
                np.zeros((bias,))
            ])

        # finalize the network
        self.net.compile(optimizer="SGD", loss="categorical_crossentropy")

    def train(self, oldS, oldA, s, a):
        # get the outputs and inputs based on the current state for the current
        inputs = self.getInputs()
        outputs = self.getOutputs()

        # add the appropriate reward values to the expected output
        # TODO is this an effective training strategy? Probably not
        add = np.zeros((self.actions,))
        for i in range(self.actions):
            add[i] = self.environment.rewardFunc(s, i)
        outputs += add

        # TODO does this actually train the model?
        self.net.fit(inputs, outputs, batch_size=1, verbose=0, use_multiprocessing=True)

    def getOutputs(self):
        """
        Get the output values of the model
        :return: The output values as a numpy array
        """
        return self.net.predict(self.getInputs(), verbose=0)

    def getInputs(self):
        """
        Get the inputs for the network
        :return: The inputs as a numpy array to be fed into the network
        """
        inputs = np.zeros((1, self.environment.stateSize()))
        inputs[0] = self.environment.toState()
        return inputs

    def getActions(self, s):
        # get the actions
        actions = self.getOutputs()
        # convert the actions to a list
        return [a for a in actions]


class Environment:
    """
    A generic object for an environment.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def stateSize(self):
        """
        Get the number of values used for input for a network
        :return: The number of values
        """
        return 0

    @abc.abstractmethod
    def toState(self):
        """
        Convert the model into a 1D numpy array that can be fed into a network as inputs
        :return: the inputs
        """
        return np.zeros((0,))

    @abc.abstractmethod
    def rewardFunc(self, s, a):
        """
        Determine the reward for the given action during the given state
        :param s: The current state
        :param a: The current action
        :return: The reward
        """
        return 0


class DummyGame(Environment):

    def __init__(self, grid, rewards=None, pos=(0, 0), explorationRate=0.5):
        """
        Create a dummy game for Q learning. This is a grid where moving to a new square gives different reward.
            Moving from one square to another is reduces reward
        :param grid: A 2D numpy array containing the values for entering the corresponding square.
        :param rewards: A list of the rewards for a corresponding action, none for default values,
            [move, good, bad, dead, win, do nothing]
        :param pos: A 2-tuple, (x, y), the starting position in the grid, default: (0, 0)
        """
        self.grid = grid

        self.rewards = rewards
        if self.rewards is None:
            self.rewards = [D_MOVE, D_GOOD, D_BAD, D_DEAD, D_WIN, D_DO_NOTHING]

        self.defaultPos = pos
        self.x, self.y = pos

        self.explorationRate = explorationRate

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
        """
        Get the current state of this model
        :return: the state
        """
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

    def move(self, direction):
        """
        Move in the given direction if possible
        :param direction: The direction to move in, 0 = up, 1 = right, 2 = down, 3 = left
        :return: The new grid reward type if the move was successful, None otherwise
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
            return None
        return self.gridP(self.x, self.y)

    def stateSize(self):
        return 5 * self.width() * self.height()

    def toState(self):
        # create an array of appropriate size
        arr = np.zeros((self.stateSize(),))
        size = self.width() * self.height()

        # there are 5 possibilities for each grid position
        for c in range(5):
            # go through each row
            for i, y in enumerate(self.grid):
                # go through each position in the row
                for j, x in enumerate(y):
                    # get the position in the array
                    pos = c * size + i * self.width() + j
                    # if the id of the grid position matches the current grid position,
                    #   set the array to 1, 0 otherwise
                    arr[pos] = 1 if x == c else 0
        return arr

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

    def playGame(self, qModel, learn=False, printPos=False):
        """
        Play the game using the given QTable
        :param qModel: The table or network to use for making decisions
        :param learn: True to also update the given qTable as this model learns, False otherwise, default False
        :param printPos: True if the position should be printed after each move, False otherwise, default False
        :return: The total reward gained from playing the game
        """

        # reset them model
        self.x, self.y = self.defaultPos
        moves = 0
        total = 0

        square = self.gridP(self.x, self.y)

        # run the model until 100 moves, or it ends the game
        while not square == WIN and not square == DEAD and moves < MAX_MOVES:
            # get the state before making an action
            state = self.state(self.x, self.y)

            # save the old state
            oldState = state

            # pick a direction
            direction = qModel.chooseAction(state)

            # move and update game ending conditions
            # also get the direction
            if self.move(direction) is None:
                action = CANT_MOVE
            else:
                action = direction

            # get the new state after moving
            state = self.state(self.x, self.y)

            # add to the total reward
            total += self.rewardFunc(oldState, action)

            # update the QModel
            if learn:
                qModel.train(oldState, action, state, action)

            # print the position
            if printPos:
                print("(x: " + str(self.x) + ", y: " + str(self.y) + ")")

            # determine the value of the current grid square and account for making a move
            square = self.gridP(self.x, self.y)
            moves += 1

        return total
