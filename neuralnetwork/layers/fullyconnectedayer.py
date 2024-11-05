from neuralnetwork.layers.layer import Layer
from neuralnetwork.neuron.neuron import Neuron
import numpy as np
from typing import Optional
from neuralnetwork.optimizers.optimizer import Optimizer
from neuralnetwork.optimizers.sgd import SGD
from neuralnetwork.activations.activation import Activation
from neuralnetwork.activations.relu import ReLU


class FullyConnectedLayer(Layer):
    def __init__(
        self,
        n_inputs: int,
        n_neurons: int,
        activation: Optional[Activation] = ReLU,
        optimizer: Optional[Optimizer] = SGD,
    ):
        super().__init__(activation, optimizer)
        self.n_inputs = n_inputs
        self.n_neurons = n_neurons
        self.initialize_params()

    def initialize_params(self):
        """
        Initializes Neurons with random weights and biases following the Normal Distr.
        """
        self.neurons = [Neuron(self.n_inputs) for _ in range(self.n_neurons)]

    def forward_propagation(self, inputs):
        """
        inputs:
            An array of features (should be a numpy array)

        Returns:
            An array of the output values from each neuron in the layer.

        Function:
            Performs forward propagation by calculating the weighted sum for each neuron
        and applying the activation function
        """
        self.inputs = inputs
        activation_outputs = []

        for neuron in self.neurons:
            weighted_sum = neuron.calculate_neuron_weighted_sum(inputs)
            output = self.activation.apply(weighted_sum)
            activation_outputs.append(output)

        return np.array(activation_outputs)

    def calculate_loss(self, pred_y: np.ndarray, y_orig: np.ndarray):
        """
        Takes in the labels predicted and original labels.

        Calculates the loss as a mean sq error
        """
        mse = np.mean((pred_y - y_orig) ** 2)
        return mse

    # TODO: We assume a MSE loss. When we implement CE we can update to include CE_WRT_Y_PRED
    def calc_gradient_wrt_y_pred(self, y_pred, y_orig):
        """
        Calculates the gradient of the MSE loss wrt y_pred.
        This is the output from the final layer.

        Params:
            y_pred = predicted label y
            y_orig = original label y

        Returns:
            Gradient of the loss wrt y_pred
        """
        return 2 * (y_pred - y_orig) / self.n_inputs

    def calc_gradient_wrt_z(self, weighted_sum, y_pred, y_orig):

        # (∂L/∂y_pred):
        dl_dy = self.calc_gradient_wrt_y_pred(y_pred, y_orig)

        # (∂L/∂a)
        dl_da = self.activation.derivative(weighted_sum)

        dl_dz = dl_da * dl_dy
        return dl_dz

    def calc_gradient_wrt_w(self, dl_dz, inputs):
        n_neurons = dl_dz.shape[0]
        n_inputs = inputs.shape[0]
        dL_dw = np.zeros((n_neurons, n_inputs))

        for j in range(n_neurons):
            for i in range(n_inputs):
                dL_dw[j, i] = dl_dz[j] * inputs[i]

        return dL_dw

    def calc_gradient_wrt_b(self, dl_dz):
        dl_db = dl_dz
        return dl_db

    def back_propagation(self, y_orig, y_pred):
        # gradient wrt y_pred
        dl_dy = self.calc_gradient_wrt_y_pred(y_pred, y_orig)
        grads_and_vars = []

        for i, neuron in enumerate(self.neurons):
            dl_dz = self.calc_gradient_wrt_z(neuron.weighted_sum, y_pred[i], y_orig[i])

            # weights, bias
            dl_dw = dl_dz * self.inputs
            dl_db = dl_dz

            grads_and_vars.append((dl_dw, neuron.weights))
            grads_and_vars.append((dl_db, neuron.bias))

        # pass to optimizer

        self.optimizer.apply_gradients(grads_and_vars)
