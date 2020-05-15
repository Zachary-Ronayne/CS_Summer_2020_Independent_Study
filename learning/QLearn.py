import numpy as np

import random

from Constants import *


class Table:

    def __init__(self, states, actions, rewardFunc, model, learnRate=1, discountRate=0.5):
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
                    self.rewardFunc(oldS, oldA)
                    + self.discountRate * (self.model.maxState(s, a)) - self.qTable[oldS, oldA]
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
        y = s // len(self.grid[0])
        return x, y

    def state(self, x, y):
        """
        Convert grid coordinates to their corresponding state
        :param x: The x coordinate
        :param y: The y coordinate
        :return: The state
        """
        return x + y * len(self.grid)

    def maxState(self, s, a):
        """
        Get the maximum reward that can be achieved from the current state to the next
        :param s: The new state
        :param a: The new action
        :return: The maximum reward
        """

        x, y = self.pos(s)

        # test code, seeing if changing direction based on action makes a difference
        """
        if a == UP:
            y -= 1
        elif a == DOWN:
            y += 1
        elif a == LEFT:
            x -= 1
        elif a == RIGHT:
            x += 1
        """

        values = []
        if x > 0:
            values.append(self.rewards[self.grid[y, x - 1]])
        if x < len(self.grid[0]) - 1:
            values.append(self.rewards[self.grid[y, x + 1]])
        if y > 0:
            values.append(self.rewards[self.grid[y - 1, x]])
        if y < len(self.grid) - 1:
            values.append(self.rewards[self.grid[y + 1, x]])

        if len(values) > 0:
            return max(values)
        else:
            return self.rewards[DO_NOTHING]

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
        return self.grid[self.x, self.y]

    def rewardFunc(self, s, a):
        # can't move, punish for corresponding punishment for not moving
        if a == CANT_MOVE:
            return self.rewards[DO_NOTHING]

        # get the position
        x, y = self.pos(s)

        # determine new grid position based on action
        if s == UP:
            y -= 1
        elif s == DOWN:
            y += 1
        elif s == LEFT:
            x -= 1
        elif s == RIGHT:
            x += 1

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

        state = self.state(self.x, self.y)
        action = CANT_MOVE

        # run the model until 100 moves, or it ends the game
        while moves < MAX_MOVES:
            oldState, oldAction = state, action

            # get the state
            state = self.state(self.x, self.y)

            # pick a direction
            actions = [qTable.qTable[state, i] for i in range(4)]

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

            square = self.grid[self.x, self.y]
            moves += 1

            total += qTable.rewardFunc(state, action)

            # update the QTable
            if learn:
                qTable.updateTable(oldState, oldAction, state, action)

            # print the position
            if printPos:
                print(str(self.x) + " " + str(self.y))

            # if an ending square is reached, apply that reward
            if square == WIN:
                total += self.rewards[WIN]
                break
            elif square == DEAD:
                total += self.rewards[DEAD]
                break

        return total
