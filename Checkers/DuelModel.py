from Checkers.Environments import *


class DuelModel:
    """
    A class used to contain two Environment models, one for each side of a checkers game
    """

    def __init__(self, game, rGameInner=None, rPieceInner=None, bGameInner=None, bPieceInner=None):
        """
        Create the DuelModel object
        :param game: The game to use for the object
        :param rGameInner: The inner layers for the red game network
        :param rPieceInner: The inner layers for the red piece network
        :param bGameInner: The inner layers for the black game network
        :param bPieceInner: The inner layers for the black piece network
        """
        self.redEnv = PieceEnvironment(game, gameInner=rGameInner, pieceInner=rPieceInner)
        self.blackEnv = PieceEnvironment(game, gameInner=bGameInner, pieceInner=bPieceInner, enemyEnv=self.redEnv)
        self.redEnv.enemyEnv = self.blackEnv
        self.game = game

    def currentEnvironment(self):
        """
        Get the Environment object for the current turn of the game
        :return: The Environment object
        """
        return self.redEnv if self.game.redTurn else self.blackEnv

    def playGame(self, printReward=False, defaultState=None):
        """
        Play a game of checkers using both models, training them separately
        :param printReward: True to print the reward each time one is obtained, False to not print, default False
        :param defaultState: A Game with the pieces in the state where they should start, red still always moves first.
            Use None to have a normal game. Default None
        :return: A 4 tuple (red reward, black reward, red move count, black move count)
        """

        self.game.resetGame()

        # TODO make this an option in the GUI, and move this method to Game
        if defaultState is not None:
            self.game.setBoard(defaultState.toList(), True)

        redTotal, blackTotal, redMoves, blackMoves = 0, 0, 0, 0

        # play the game until it's over
        while self.game.win == E_PLAYING:
            turn = self.game.redTurn
            reward = self.currentEnvironment().playGameMove(printReward)
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

    def decayModels(self):
        """
        Apply decay to the networks of both models
        """
        self.redEnv.decayNetworks()
        self.blackEnv.decayNetworks()

    def save(self, savePath, name):
        """
        Save all of the networks associated with this DuelModel
        :param savePath: The path, relative to saves, to save this DuelModel
        :param name: The base name to use for saving
        :return: True if the save was successful, False otherwise
        """

        redName = savePath + "/" + name + " red "
        blackName = savePath + "/" + name + " black "

        success = self.redEnv.saveNetworks(redName + PIECE_NETWORK_NAME, redName + GAME_NETWORK_NAME)
        success &= self.blackEnv.saveNetworks(blackName + PIECE_NETWORK_NAME, blackName + GAME_NETWORK_NAME)

        return success

    def load(self, loadPath, name):
        """
        Load all of the networks associated with this DuelModel
        :param loadPath: the path, relative to saves, where the DuelModel is saved
        :param name: The base name used to save the model
        :return: True if the load was successful, False otherwise
        """
        redName = loadPath + "/" + name + " red "
        blackName = loadPath + "/" + name + " black "

        success = self.redEnv.loadNetworks(redName + PIECE_NETWORK_NAME, redName + GAME_NETWORK_NAME)
        success &= self.blackEnv.loadNetworks(blackName + PIECE_NETWORK_NAME, blackName + GAME_NETWORK_NAME)

        return success

    def trainCollective(self, games, printMoves=False, printGames=False):
        """
        Play the game by making moves without learning anything from them initially.
        :param games: The number of games to make
        :param printMoves: True to print each move made during the training, False to not print, default False
        :param printGames: True to print when each game is done processing, False to not print, default False
        """

        if games == 0:
            return

        pieceStates = [[]] * 2
        gameStates = [[]] * 2
        pieceRewards = [[]] * 2
        gameRewards = [[]] * 2

        # TODO generally improve this code

        # do this games number of times
        for i in range(games):
            # reset the game
            self.game.resetGame()

            # play the game until it ends
            while self.game.win == E_PLAYING:
                env = self.currentEnvironment()
                turn = 0 if self.game.redTurn else 1

                # copy the current game state
                state = self.game

                # determine the states for network input
                gameInput = env.gameEnv.toNetInput()

                # pick a random valid action for the game network
                gameAction = env.gameNetwork.randomValidAction()
                # if there is not a valid action, end the game
                if gameAction is None:
                    break

                # take the game action
                env.gameEnv.takeAction(gameAction)
                pieceInput = env.toNetInput()

                # pick a random valid action for the piece network
                pieceAction = env.internalNetwork.randomValidAction()

                # if there is not a valid action, end the game
                if pieceAction is None:
                    break

                # save the states for network input
                pieceStates[turn].append(pieceInput[0])
                gameStates[turn].append(gameInput[0])

                # determine the action rewards, and save them
                reward = env.gameNetwork.getOutputs()
                reward[0][gameAction] = env.gameEnv.rewardFunc(state, gameAction)
                gameRewards[turn].append(reward[0])

                reward = env.internalNetwork.getOutputs()
                reward[0][pieceAction] = env.rewardFunc(state, pieceAction)
                pieceRewards[turn].append(reward[0])

                # take the piece action
                env.takeAction(pieceAction)

                if printMoves:
                    print("taken action", gameAction, pieceAction, "on game", i)
            if printGames:
                print("Game", i, "done")

        # after all moves have been made, run all data through training
        self.redEnv.internalNetwork.trainMultiple(pieceStates[0], pieceRewards[0])
        self.redEnv.gameNetwork.trainMultiple(gameStates[0], gameRewards[0])
        self.blackEnv.internalNetwork.trainMultiple(pieceStates[1], pieceRewards[1])
        self.blackEnv.gameNetwork.trainMultiple(gameStates[1], gameRewards[1])
