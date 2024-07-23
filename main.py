from sklearn.utils import shuffle
import tensorflow as tf
import pandas as pd
import numpy as np
import pyfiglet
import tarfile
import shutil
import os


class Model:
    def __init__(self, device, data=None):
        self.device = device
        # data['Label'] = data["Label"].apply(lambda x: 1 if x == "bad" else 0)
        data['TLDLegitimateProb'] = pd.to_numeric(data["TLDLegitimateProb"], errors='coerce')

        # Drop rows with NaN values in 'numeric_column'
        data.dropna(subset=['TLDLegitimateProb'], inplace=True)
        data["TLDLegitimateProb"] = 1 - data["TLDLegitimateProb"]
        data['TLDLegitimateProb'] = data['TLDLegitimateProb'].astype(float).round().astype(int)
        data = shuffle(data)
        data["URL"].replace("https://", "").replace("http//", "").replace("www.", "")
        self.maxLen = 100
        # Tokeniser
        self.tokeniser = tf.keras.preprocessing.text.Tokenizer()
        self.tokeniser.fit_on_texts(data["URL"])
        self.sequences = self.tokeniser.texts_to_sequences(data["URL"])
        if os.path.exists("./model.keras"):
            self.model = tf.keras.models.load_model("./model.keras")
            print("Model loaded")
        elif data is not None:
            with tf.device(self.device):
                print("Training new model")
                self.model = tf.keras.models.Sequential([
                    tf.keras.layers.Embedding(input_dim=len(self.tokeniser.word_index) + 1, output_dim=128),
                    tf.keras.layers.LSTM(128, dropout=0.2, recurrent_dropout=0.2),
                    tf.keras.layers.Dense(1, activation='sigmoid')
                ])
                self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        else:
            raise Exception("No data provided/ no model found")

    def training(self, epochs):
        X = tf.keras.preprocessing.sequence.pad_sequences(self.sequences, maxlen=self.maxLen)
        y = np.array(data["TLDLegitimateProb"])

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
        if prediction >= 0.9:
            danger = "Highly likely Scam"
        elif prediction > 0.5:
            danger = "Likely Scam"
        else:
            danger = "Likely Safe"
        return prediction[0][0], danger


if __name__ == "__main__":
    if not os.path.exists("./PhiUSIIL_Phishing_URL_Dataset.csv"):
        print("Decompressing file")
        with tarfile.open("./dataset.tar.gz", 'r:gz') as tar:
            tar.extractall(path="./")
    if len(tf.config.experimental.list_physical_devices('GPU')):
        device = "/GPU:0"
        print(pyfiglet.figlet_format("GPU"))
    else:
        device = "/CPU:0"
        print(pyfiglet.figlet_format("CPU"))
    data = pd.read_csv("./PhiUSIIL_Phishing_URL_Dataset.csv")
    model = Model(device, data)
    epochs = int(input("How many epochs would you like to train? "))
    epochs5 = epochs // 5
    epochsRemainder = epochs % 5
    for i in range(epochs5):
        print(f"Chunk {i+1} of {epochs5 + (1 if epochsRemainder else 0)}")
        model.training(epochs=5)
        if not os.path.exists("./models"):
            os.mkdir("./models")
        print(f"Creating snapshot for model to be saved in ./models/model_{i}.keras")
        shutil.copy("./model.keras", f"./models/model_{i}.keras")
    model.training(epochs=epochsRemainder)
