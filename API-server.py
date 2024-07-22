from main import Model
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import pandas as pd
import tarfile
import os


class WebServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS

        if len(tf.config.experimental.list_physical_devices('GPU')):
            device = "/GPU:0"
        else:
            device = "/CPU:0"
        if not os.path.exists("./PhiUSIIL_Phishing_URL_Dataset.csv"):
            print("Decompressing file")
            with tarfile.open("./dataset.tar.gz", 'r:gz') as tar:
                tar.extractall(path="./")
        self.model = Model(device, data=pd.read_csv("./PhiUSIIL_Phishing_URL_Dataset.csv"))

        # Define the route within the constructor
        self.app.route("/process", methods=["POST"])(self.process)

    def process(self):
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Invalid input'}), 400

        text = data['text']
        result = self.processData(text)
        return jsonify(result)

    def processData(self, text):
        prediction, danger = self.model.predict(text)
        prediction = str(round(prediction * 100, 2))
        output = {
            'prediction': prediction,
            'danger': danger
        }
        return output

    def run(self):
        self.app.run(debug=True)


if __name__ == "__main__":
    server = WebServer()
    server.run()
