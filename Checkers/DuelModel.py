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
        self.blackEnv = PieceEnvironment(game, gameInner=bGameInner, pieceInner=bPieceInner)
        self.game = game

    def currentEnvironment(self):
        """
        Get the Environment object for the current turn of the game
        :return: The Environment object
        """
        return self.redEnv if self.game.redTurn else self.blackEnv

    def playGame(self, printReward=False):
        """
        Play a game of checkers using both models, training them separately
        :return:
        """

        self.game.resetGame()

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
