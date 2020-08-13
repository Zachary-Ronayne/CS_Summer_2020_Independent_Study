from learning.QLearn import *


class ConvNetwork(Network):
    """
    A convolutional Q Network specifically made for use with the Checkers model
    """

    def __init__(self, actions, environment, game, channels, inner=None,
                 learnRate=0.5, discountRate=0.5, explorationRate=0.5):
        self.game = game
        self.channels = channels
        super().__init__(actions, environment, inner, learnRate, discountRate, explorationRate)

    def initNetwork(self):
        # determine the dimensions of the sizes of each filter
        convSizes = [(3, 2)] * (self.game.width - 2)
        convSizes.append((4, 2))

        # create a list of layers, the first layer, ie the input layer, has a specified input_shape
        layers = [keras.layers.Conv2D(self.actions, c, activation="sigmoid",
                                      use_bias=True, data_format='channels_last',
                                      input_shape=(self.game.height, self.game.width, self.channels),
                                      kernel_initializer=tf.keras.initializers.RandomUniform(-1, 1, None),
                                      bias_initializer=tf.keras.initializers.RandomUniform(-1, 1, None))
                  if i == 0 else

                  keras.layers.Conv2D(self.inner[i], c, activation="sigmoid",
                                      use_bias=True, data_format='channels_last',
                                      kernel_initializer=tf.keras.initializers.RandomUniform(-1, 1, None),
                                      bias_initializer=tf.keras.initializers.RandomUniform(-1, 1, None))

                  for i, c in enumerate(convSizes)]

        # create the output layer
        layers.append(keras.layers.Dense(self.actions, activation="linear", use_bias=True))

        # create the network object
        self.net = keras.Sequential(layers)

        # compile and finish building network
        self.net.compile(optimizer=self.optimizer,
                         loss=LOSS_FUNCTION())

    def getActions(self, s):
        # get the actions
        actions = self.net(s)
        # convert the actions to a list
        return actions[0][0][0]

    def getOutputs(self):
        """
        Get the output values of the model
        :return: The output values as a numpy array
        """
        return self.net(self.getInputs())[0][0]
