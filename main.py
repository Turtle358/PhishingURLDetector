import pandas as pd
import numpy as np
import tensorflow as tf
import os


class Model:
    def __init__(self, data, device):
        self.device = device
        data['Label'] = data["Label"].apply(lambda x: 1 if x == "bad" else 0)
        self.maxLen = 100
        # Tokeniser
        self.tokeniser = tf.keras.preprocessing.text.Tokenizer()
        self.tokeniser.fit_on_texts(data["URL"])
        self.sequences = self.tokeniser.texts_to_sequences(data["URL"])
        if os.path.exists("./model.keras"):
            self.model = tf.keras.models.load_model("./model.keras")
        else:
            with tf.device(self.device):
                self.model = tf.keras.models.Sequential([
                    tf.keras.layers.Embedding(input_dim=len(self.tokeniser.word_index) + 1, output_dim=128,
                                              input_length=self.maxLen),
                    tf.keras.layers.LSTM(128, dropout=0.2, recurrent_dropout=0.2),
                    tf.keras.layers.Dense(1, activation='sigmoid')
                ])
                self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    def training(self, epochs):
        X = tf.keras.preprocessing.sequence.pad_sequences(self.sequences, maxlen=self.maxLen)
        y = np.array(data["Label"])

        splitRatio = 0.8
        splitIndex = int(len(X) * splitRatio)
        XTrain, XTest = X[:splitIndex], X[splitIndex:]
        yTrain, yTest = y[:splitIndex], y[splitIndex:]

        with tf.device(self.device):
            self.model.fit(XTrain, yTrain, epochs=epochs, batch_size=64, validation_split=0.1)

        loss, accuracy = self.model.evaluate(XTest, yTest)
        print(f"Loss: {loss:.4f}, Accuracy: {accuracy:.4f}")
        self.model.save("model.keras")

    def predict(self, url):
        seq = self.tokeniser.texts_to_sequences([url])
        padded = tf.keras.preprocessing.sequence.pad_sequences(seq, maxlen=self.maxLen)
        with tf.device(self.device):
            prediction = self.model.predict(padded)
        return prediction


if __name__ == "__main__":
    print(tf.config.list_physical_devices('GPU'))
    if len(tf.config.experimental.list_physical_devices('GPU')):
        device = "/GPU:0"
    else:
        device = "/CPU:0"
    print(device)
    data = pd.read_csv("./phishing_site_urls.csv")
    model = Model(data, device)
    model.training(epochs=int(input("Enter how many epochs to train: ")))
