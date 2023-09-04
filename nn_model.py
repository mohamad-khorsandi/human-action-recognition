import os.path

import joblib
from keras.optimizers import Adam
from matplotlib import pyplot as plt
from sklearn import svm

from sklearn.metrics import accuracy_score, confusion_matrix
import seaborn as sns
from tensorflow import keras
from tensorflow.keras import layers


class NNModel:
    def __init__(self, model):
        self._model = model
        self.accuracy = None
        self.conf_mat = None

    @classmethod
    def for_inference(cls, model_file_name):
        return NNModel(joblib.load(model_file_name))

    @classmethod
    def for_train(cls):
        model = keras.Sequential([
            layers.Input(shape=(34,)),

            layers.Dense(64, activation='relu'),
            layers.Dense(32, activation='relu'),

            layers.Dense(3, activation='softmax')
        ])

        model.compile(optimizer=Adam(learning_rate=0.001),
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])

        return NNModel(model)

    def fit(self, x_train, y_train):
        self._model.fit(x_train, y_train, epochs=10, batch_size=32)

    def save(self, base_dir):
        path = os.path.join(base_dir, f'mlp{self.accuracy:.2f}')
        self._model.save(path)

    def predict(self, x_test):
        return self._model.predict(x_test)

    def evaluate(self, x_test, y_test, class_names):
        y_pred = self.predict(x_test)
        self.accuracy = accuracy_score(y_test, y_pred)
        print("Accuracy:", self.accuracy)

        self.conf_mat = confusion_matrix(y_test, y_pred)
        sns.heatmap(self.conf_mat, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.show()

