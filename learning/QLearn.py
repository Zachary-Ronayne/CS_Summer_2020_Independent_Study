from tensorflow import keras
import tensorflow as tf
import tensorflow.python as tfp

import random
import abc

from Constants import *


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
            action = random.randint(0, self.actions - 1)

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
    def train(self, state, action):
        """
        Modify the QModel to change based on the given states and actions. In the process of training,
            one step in the environment should be taken
        :param state: the state of the environment
        :param action: the action to take
        """


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

    def train(self, state, action):
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

    def getActions(self, s):
        return [self.qTable[s, i] for i in range(self.actions)]


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
        self.inputs = None
        self.weights = None
        self.q_out = None
        self.predict = None
        self.next_Q = None
        self.loss = None
        self.trainer = None
        self.updateModel = None
        self.Q_output = None

        self.initNetwork()

    def initNetwork(self):
        """
        Initialize the network to an unlearned, default state
        """

        """
        tf.compat.v1.disable_eager_execution()

        tfp.reset_default_graph()
        self.inputs = tfp.placeholder(shape=(1, self.states), dtype=tf.float32)
        self.weights = tfp.Variable(initial_value=np.zeros((self.states, self.actions)),
                                    shape=(self.states, self.actions), dtype=tf.float32)

        self.q_out = tfp.matmul(self.inputs, self.weights)
        self.predict = tfp.argmax(self.q_out, 1)

        self.next_Q = tfp.placeholder(shape=(1, self.actions), dtype=tf.float32)
        self.Q_output = tfp.Variable(initial_value=np.zeros((1, self.actions)),
                                     shape=(1, self.actions), dtype=tf.float32)

        self.loss = tfp.reduce_sum(tf.square(self.next_Q - self.Q_output))
        self.trainer = tfp.train.GradientDescentOptimizer(learning_rate=self.learnRate)
        self.updateModel = self.trainer.minimize(self.loss)
        """

        # create a list of layers, initialized with the input layer as the input shape
        layers = [keras.layers.Dense(self.inner[0], activation="sigmoid", use_bias=True,
                                     input_shape=(self.states,))]

        # add all remaining hidden layers
        for lay in self.inner[1:]:
            layers.append(keras.layers.Dense(lay, activation="sigmoid", use_bias=True))

        # TODO play with activation functions
        # create the output layer
        layers.append(keras.layers.Dense(self.actions, activation="linear", use_bias=True))

        # create the network object
        self.net = keras.Sequential(layers)

        # compile and finish building network
        # TODO should Adam be used here?
        self.net.compile(optimizer=keras.optimizers.Adam(learning_rate=self.learnRate), loss="categorical_crossentropy")

    def train(self, state, action):
        # TODO fix book implementation
        # TODO use discount rate?

        """
        init = tfp.global_variables_initializer()

        with tfp.Session() as sess:
            sess.run(init)

            action, q = sess.run([self.predict, self.q_out], feed_dict={
                self.inputs: np.identity(self.states)[state:state + 1]
            })

            if np.random.rand(1) < self.explorationRate:
                action[0] = random.randint(0, self.actions - 1)

            reward = self.environment.rewardFunc(state, action[0])
            self.environment.takeAction(action[0])
            next_state = self.environment.currentState()

            curr_q = sess.run(self.q_out, feed_dict={
                self.inputs: np.identity(self.states)[next_state:next_state+1]
            })

            self.Q_output = curr_q

            max_next_q = np.max(curr_q)
            target_q = q
            target_q[0, action[0]] = reward + self.learnRate * max_next_q

            info, new_weights = sess.run([self.loss, self.weights], feed_dict={
                self.inputs: np.identity(self.states)[state:state + 1],
                self.next_Q: tfp.Variable(initial_value=target_q, shape=target_q.shape, dtype=tf.float32)
            })

            self.weights = new_weights
            """
        # get the state of the game before the move happens
        inputs = self.getInputs()

        # get the outputs of the network at the current state
        # this means finding the Q values for each action in the current state
        outputs = self.getOutputs()

        # get the reward for taking the given action in the given state
        reward = self.environment.rewardFunc(state, action)

        # make next step in environment, meaning take the action
        self.environment.takeAction(action)

        # find Q values for that next state
        nextOutputs = self.getOutputs()

        # set the training output data values, copying the previous predictions
        expectedOut = outputs

        # set the calculated Q value for the specific action taken
        expectedOut[0, action] = reward + self.learnRate * np.max(nextOutputs)

        # train the network on the newly expected Q values
        self.net.fit(inputs, expectedOut, batch_size=None, verbose=0, use_multiprocessing=True)

    def getOutputs(self):
        """
        Get the output values of the model
        :return: The output values as a numpy array
        """
        return self.net.predict(self.getInputs(), verbose=0)

    def getInputs(self):
        """
        Get the inputs for the network
        :return: The inputs as a numpy array to be fed into the network. All elements are 0,
            except for the element of the current state, which is 1
        """
        inputs = np.zeros((1, self.states))
        inputs[0][self.environment.currentState()] = 1
        return inputs

    def getActions(self, s):
        # get the actions
        actions = self.getOutputs()
        # convert the actions to a list
        return [a for a in actions[0]]


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
    def currentState(self):
        """
        Get the current state of this model
        :return: the state
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
        :return The reward type for taking that action
        """
        return 0


class DummyGame(Environment):

    def __init__(self, grid, rewards=None, pos=(0, 0)):
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

        # TODO make this some kind of setting for how much the rewards are reduced and using tanh
        # self.rewards = np.tanh([0.05 * r for r in self.rewards])

        self.defaultPos = pos
        self.x, self.y = pos

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
        return self.gridP(self.x, self.y)

    def stateSize(self):
        return 5 * self.width() * self.height()

    def toState(self):
        # create an array of appropriate size
        arr = np.zeros((self.stateSize(),))
        size = self.width() * self.height()

        # there are NUM_ACTIONS possibilities for each grid position
        for c in range(NUM_ACTIONS):
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
        Play the game using the given QModel
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

        # run the model until a set number of moves, or the game ends
        while not square == WIN and not square == DEAD and moves < MAX_MOVES:
            # get the state before making an action
            state = self.state(self.x, self.y)

            # pick a direction
            action = qModel.chooseAction(state)

            # update the QModel with training
            if learn:
                qModel.train(state, action)

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
