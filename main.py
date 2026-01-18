from sklearn.utils import shuffle
import tensorflow as tf
import pandas as pd
import pyfiglet
import tarfile
import pickle
import os


class Model:
    def __init__(self, device, data=None):
        self.device = device
        self.maxLen = 100
        self.tokeniserPath = "./PhishingURLDetector/tokeniser.pickle"
        if os.path.exists(self.tokeniserPath):
            with open(self.tokeniserPath, 'rb') as handle:
                self.tokeniser = pickle.load(handle)
            print("Tokenizer loaded from disk")
        elif data is not None:
            self.tokeniser = tf.keras.preprocessing.text.Tokenizer(char_level=True, lower=True)
            print("Creating new Tokenizer...")
        else:
            raise Exception("No tokenizer found and no data to create one.")

        if data is not None:
            # Pre-processing and Normalisation
            data['TLDLegitimateProb'] = pd.to_numeric(data["TLDLegitimateProb"], errors='coerce')
            data.dropna(subset=['TLDLegitimateProb', 'URL'], inplace=True)

            # Ensure binary labels are strictly 0 or 1
            data["label"] = (1 - data["TLDLegitimateProb"]).apply(lambda x: 1 if x > 0.5 else 0)
            data['URL'] = self.normaliseStringSeries(data['URL'])
            data = shuffle(data)

            # Fit tokeniser if it was just created
            if not os.path.exists(self.tokeniserPath):
                self.tokeniser.fit_on_texts(data["URL"])
                # Save it immediately so prediction uses the SAME mapping
                if not os.path.exists("./PhishingURLDetector"): os.mkdir("./PhishingURLDetector")
                with open(self.tokeniserPath, 'wb') as handle:
                    pickle.dump(self.tokeniser, handle)

            sequences = self.tokeniser.texts_to_sequences(data["URL"])
            X = tf.keras.preprocessing.sequence.pad_sequences(sequences, maxlen=self.maxLen)
            y = data["label"].values

            split_idx = int(len(X) * 0.8)
            self.XTrain, self.XTest = X[:split_idx], X[split_idx:]
            self.yTrain, self.yTest = y[:split_idx], y[split_idx:]

        # Load or Build Model
        model_path = "./PhishingURLDetector/model.keras"
        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
            print("Model loaded from disk")
        elif data is not None:
            with tf.device(self.device):
                print("Building Hybrid CNN-LSTM Architecture")
                self.model = tf.keras.models.Sequential([
                    tf.keras.layers.Embedding(input_dim=len(self.tokeniser.word_index) + 1, output_dim=128),
                    tf.keras.layers.Conv1D(filters=64, kernel_size=5, activation='relu'),
                    tf.keras.layers.MaxPooling1D(pool_size=4),
                    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64, dropout=0.2)),
                    tf.keras.layers.Dense(64, activation='relu'),
                    tf.keras.layers.Dense(1, activation='sigmoid')
                ])
                # Lower learning rate helps prevent the "50% guess" weight collapse
                opt = tf.keras.optimizers.Adam(learning_rate=0.0005)
                self.model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])

    def normaliseStringSeries(self, series):
        return series.str.lower().str.replace('www.', '', regex=False).str.rstrip('/')

    def training(self, epochs):
        checkpoint = tf.keras.callbacks.ModelCheckpoint(
            filepath='./PhishingURLDetector/model_latest_checkpoint.keras',
            monitor='val_accuracy',
            save_best_only=True,
            mode='max'
        )

        with tf.device(self.device):
            self.model.fit(
                self.XTrain,
                self.yTrain,
                epochs=epochs,
                batch_size=64,
                validation_data=(self.XTest, self.yTest),
                callbacks=[checkpoint]
            )

        self.model.save("./PhishingURLDetector/model.keras")

    def predict(self, url):
        clean_url = normaliseSingleURL(url)
        # Now uses the saved vocabulary mapping
        seq = self.tokeniser.texts_to_sequences([clean_url])
        padded = tf.keras.preprocessing.sequence.pad_sequences(seq, maxlen=self.maxLen)

        with tf.device(self.device):
            prediction = self.model.predict(padded, verbose=0)[0][0]

        if prediction >= 0.8:
            danger = "Highly likely Scam"
        elif prediction > 0.5:
            danger = "Likely Scam"
        else:
            danger = "Likely Safe"
        return prediction, danger


def normaliseSingleURL(url):
    return url.lower().replace('www.', '').rstrip('/')


if __name__ == "__main__":
    # Standard setup logic
    if not os.path.exists("./PhiUSIIL_Phishing_URL_Dataset.csv"):
        if os.path.exists("./dataset.tar.gz"):
            with tarfile.open("./dataset.tar.gz", 'r:gz') as tar:
                tar.extractall(path="./")

    device = "/GPU:0" if tf.config.experimental.list_physical_devices('GPU') else "/CPU:0"
    print(pyfiglet.figlet_format(device.split(":")[0][1:]))

    raw_data = pd.read_csv("./PhiUSIIL_Phishing_URL_Dataset.csv")
    phish_model = Model(device, raw_data)

    user_epochs = int(input("Enter total training epochs: "))
    if user_epochs > 0:
        phish_model.training(epochs=user_epochs)
