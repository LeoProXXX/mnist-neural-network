import numpy as np
import time
from calculator import Calculator
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import classification_report


class NeuralNet:
    def __init__(self, sizes, epochs=10, l_rate=0.001):
        self.sizes = sizes
        self.epochs = epochs
        self.l_rate = l_rate

        self.params = self.initialize_parameters()

    def initialize_parameters(self):
        input_layer = self.sizes[0]
        hidden_1 = self.sizes[1]
        output_layer = self.sizes[2]

        params = {
            'W1': np.random.randn(hidden_1, input_layer) / np.sqrt(hidden_1),
            'W2': np.random.randn(output_layer, hidden_1) / np.sqrt(output_layer),
        }

        return params

    def forward_propagation(self, x_train):
        params = self.params

        # input layer activations becomes sample
        params['A0'] = x_train

        # input layer to hidden layer 1
        params['Z1'] = np.dot(params["W1"], params['A0'])
        params['A1'] = Calculator.sigmoid(params['Z1'])

        # hidden layer 2 to output layer
        params['Z2'] = np.dot(params["W2"], params['A1'])
        params['A2'] = Calculator.softmax(params['Z2'])

        return params['A2']

    def backward_propagation(self, y_train, output):
        params = self.params
        change_w = {}

        # Calculate W2 update
        error = 2 * (output - y_train) / output.shape[0] * Calculator.softmax_der(params['Z2'])
        change_w['W2'] = np.outer(error, params['A1'])

        # Calculate W1 update
        error = np.dot(params['W2'].T, error) * Calculator.sigmoid_der(params['Z1'])
        change_w['W1'] = np.outer(error, params['A0'])

        return change_w

    def update_parameters(self, changes_to_w):
        for key, value in changes_to_w.items():
            self.params[key] -= self.l_rate * value

    def compute_accuracy(self, x_val, y_val):
        predictions = []

        for x, y in zip(x_val, y_val):
            output = self.forward_propagation(x)
            pred = np.argmax(output)
            predictions.append(pred == np.argmax(y))

        return np.mean(predictions)

    def compute_metrics(self, x_val, y_val):
        y_pred = []
        y_true = []

        for x, y in zip(x_val, y_val):
            output = self.forward_propagation(x)
            pred = np.argmax(output)
            y_pred.append(pred)
            y_true.append(np.argmax(y))

        return {'precyzja_makro': precision_score(y_true, y_pred, average='macro'),
                'czulosc_makro': recall_score(y_true, y_pred, average='macro'),
                'dokladnosc': accuracy_score(y_true, y_pred),
                'raport': classification_report(y_true, y_pred),
                'macierz_bledow': confusion_matrix(y_true, y_pred)}

    def get_properly_classified_and_misclassified_images(self, x_val, y_val):
        properly_classified = []
        misclassified = []

        for x, y in zip(x_val, y_val):
            output = self.forward_propagation(x)
            pred = np.argmax(output)
            if pred == np.argmax(y):
                properly_classified.append(x)
            else:
                misclassified.append(x)

        return properly_classified, misclassified

    def train(self, x_train, y_train, x_val, y_val):
        start_time = time.time()
        for iteration in range(self.epochs):
            for x, y in zip(x_train, y_train):
                output = self.forward_propagation(x)
                changes_to_w = self.backward_propagation(y, output)
                self.update_parameters(changes_to_w)

            accuracy = self.compute_accuracy(x_val, y_val)
            print('Epoch: {0}, Time Spent: {1:.2f}s, Accuracy: {2:.2f}%'.format(
                iteration + 1, time.time() - start_time, accuracy * 100
            ))
