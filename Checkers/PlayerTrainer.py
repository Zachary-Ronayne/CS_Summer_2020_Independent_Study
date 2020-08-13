from Checkers.Environments import *


class PlayerTrainer:
    """
    An object that handles training a Checkers Game Network based on given moves. This is intended for
    use with giving player moves, so that the AI can learn based on moves a player uses.
    """

    def __init__(self, environment, redSide):
        """
        Create a PlayerTrainer and put it in it's default state.
        :param environment: The environment for this PlayerTrainer to use, must be a PieceEnvironment
        :param redSide: True if this PlayerTrainer plays from red side, False for black side
        """
        self.environment = environment
        self.redSide = redSide
        self.game = self.environment.game

        self.savedStates = None
        self.savedActions = None
        self.totalReward = []
        self.reset()

    def reset(self):
        """
        Reset this PlayerTrainer to a state where it is ready to play moves from itself
        :return:
        """
        self.savedStates = None
        self.savedActions = None
        self.totalReward = []

    def makeMove(self, pieceAction, gameAction):
        """
        Using the environment of this PlayerTrainer, make a move in the checkers game,
        using the given actions.
        Will do nothing if the game is not under this PlayerTrainer's turn
        :param pieceAction: The integer determining left, forward, and jump. Or None to pick an action
        :param gameAction: The integer determining the space to move. Or None to pick an action
        """
        self.savedActions = []
        self.savedStates = []
        self.totalReward = []

        # continue to get reward until it is the opponent's turn, or the game ends
        while self.game.redTurn == self.redSide and self.game.win == E_PLAYING:
            # if the actions are none, then pick new ones
            if pieceAction is None or gameAction is None:
                gameAction = self.environment.gameEnv.selectAction()
                pieceAction = self.environment.selectAction()

            # make a copy of the current state, and save it for training later
            self.savedStates.append(self.game.makeCopy())
            # save the actions made
            self.savedActions.append((pieceAction, gameAction))
            # set the piece which will be selected
            self.environment.current = self.game.singlePos(gameAction)

            # add the reward for making that one move
            self.totalReward.append(
                (self.environment.oneActionReward(self.game.makeCopy(), pieceAction, self.redSide),
                 self.environment.gameEnv.rewardFunc(self.game, gameAction))
            )

            # make that move in the game
            self.environment.takeAction(pieceAction)

            # set the actions to none for the next iteration
            pieceAction, gameAction = None, None

    def makeOpponentMove(self, pos, modifiers):
        """
        Record a move that the opponent will make. Should call this until it is this object's turn.
        Will do nothing if it is not the opponent's turn.
        This does not actually make a move for the opponent.
        :param pos: A 2-tuple of (x, y) of the game coordinates to play
        :param modifiers: A 3-tuple of boolean modifiers (left, forward, jump)
        """
        # only record the move if it was valid for the opponent to make a move
        if not self.game.redTurn == self.redSide:
            # save the current for the environment to the position where the move is made
            self.environment.current = pos
            # add the reward for that move being made
            r = self.environment.oneActionReward(
                self.game.makeCopy(), boolListToInt(modifiers), not self.game.redTurn
            )

            # add that reward to all moves made by this PlayerTrainer
            for i, rew in enumerate(self.totalReward):
                self.totalReward[i] = (rew[0] + 0 if r is None else r, rew[1])

    def train(self):
        """
        Using the collected data from player and opponent moves, train this AI appropriately.
        Does nothing if moves have not been given for both players
        """

        # check to see if training is valid
        if not self.game.redTurn == self.redSide or self.savedStates is None:
            return

        for a, s, r in zip(self.savedActions, self.savedStates, self.totalReward):
            # train both networks
            pieceA, gameA = a
            pieceR, gameR = r
            self.environment.trainMove(pieceA, gameA, pieceR, gameR, s)

        # reset values keeping track of states
        self.reset()
