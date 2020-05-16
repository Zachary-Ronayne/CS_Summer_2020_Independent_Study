import numpy as np

import random

from Constants import *


class Table:

    def __init__(self, states, actions, rewardFunc, model, learnRate=0.5, discountRate=0.5):
        """
        Create a Q table that will keep track of all of the Q values for actions and states
        :param states: The number of states
        :param actions: The number of actions
        :param model: The model to use with this table for determining when actions can happen, and potential reward
        :param rewardFunc: A function with two numerical parameters determining the reinforcement
            value for the given state and action. First parameter is state, second parameter is action
        :param learnRate: The learning rate of the table
        :param discountRate: The discount rate of the table
        """
        self.states = states
        self.actions = actions

        self.rewardFunc = rewardFunc

        self.learnRate = learnRate
        self.discountRate = discountRate

        self.qTable = None
        self.reset()

        self.currentState = 0
        self.currentAction = 0

        self.model = model

    def reset(self):
        """
        Reset the QTable to all zeros
        """
        self.qTable = np.zeros((self.states, self.actions))

    def updateTable(self, oldS, oldA, s, a):
        """
        Go from the current state to the next state
        :param oldS: the old state
        :param oldA: the old action
        :param s: The next state to go to
        :param a: The action taken
        """

        if SIMPLE_BELLMAN:
            # simplified bellman function
            self.qTable[oldS, oldA] = self.learnRate * (self.rewardFunc(oldS, oldA) + self.model.maxState(s, a))
        else:
            # complex bellman function
            self.qTable[oldS, oldA] = self.qTable[oldS, oldA] + self.learnRate * (
                    self.rewardFunc(oldS, oldA) - self.qTable[oldS, oldA] +
                    self.discountRate * (max(self.qTable[s]))
            )


class DummyModel:

    def __init__(self, grid, rewards=None, pos=(0, 0), explorationRate=0.5):
        """
        Create a dummy model for Q learning. This is a grid where moving to a new square gives different reward.
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
        x = s % len(self.grid[0])
        y = s // len(self.grid)
        return x, y

    def state(self, x, y):
        """
        Convert grid coordinates to their corresponding state
        :param x: The x coordinate
        :param y: The y coordinate
        :return: The state
        """
        return x + y * len(self.grid)

    def move(self, direction):
        """
        Move in the given direction if possible
        :param direction: The direction to move in, 0 = up, 1 = right, 2 = down, 3 = left
        :return: The new grid reward type if the move was successful, None otherwise
        """
        oldX, oldY = self.x, self.y

        if direction == LEFT and self.x > 0:
            self.x -= 1
        if direction == RIGHT and self.x < len(self.grid[0]) - 1:
            self.x += 1
        if direction == UP and self.y > 0:
            self.y -= 1
        if direction == DOWN and self.y < len(self.grid) - 1:
            self.y += 1

        if oldX == self.x and oldY == self.y:
            return None
        return self.grid[self.y, self.x]

    def rewardFunc(self, s, a):
        """
        Determine the reward for the given action during the given state
        :param s: The current state
        :param a: The current action
        :return: The reward
        """
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
        if x < 0 or x > len(self.grid[0]) - 1 or y < 0 or y > len(self.grid) - 1:
            return self.rewards[DO_NOTHING]

        # return the reward in the square, along with the cost of moving
        return self.rewards[self.grid[y, x]] - MOVE_COST

    def playGame(self, qTable, learn=False, printPos=False):
        """
        Play the game using the given QTable
        :param qTable: The table to use for making decisions
        :param learn: True to also update the given qTable as this model learns, False otherwise, default False
        :param printPos: True if the position should be printed after each move, False otherwise, default False
        :return: The total reward gained from playing the game
        """

        # reset them model
        self.x, self.y = self.defaultPos
        moves = 0
        total = 0

        square = self.grid[self.x, self.y]

        # run the model until 100 moves, or it ends the game
        while not square == WIN and not square == DEAD and moves < MAX_MOVES:
            # get the state before making an action
            state = self.state(self.x, self.y)

            # save the old state and action
            oldState = state

            # pick a direction
            # make a list of all the rewards for each action in the current state
            actions = [qTable.qTable[state, i] for i in range(4)]

            # randomly choose to either pick the index of the action with the highest value,
            #   or a random new action, thus selecting the direction
            if random.random() > self.explorationRate:
                direction = actions.index(max(actions))
            else:
                direction = random.randint(0, 3)

            # move and update game ending conditions
            # also get the direction
            if self.move(direction) is None:
                action = CANT_MOVE
            else:
                action = direction

            # get the new state after moving
            state = self.state(self.x, self.y)

            # add to the total reward
            total += qTable.rewardFunc(oldState, action)

            # update the QTable
            if learn:
                qTable.updateTable(oldState, action, state, action)

            # print the position
            if printPos:
                print("(x: " + str(self.x) + ", y: " + str(self.y) + ")")

            # determine the value of the current grid square and account for making a move
            square = self.grid[self.y, self.x]
            moves += 1

        return total
