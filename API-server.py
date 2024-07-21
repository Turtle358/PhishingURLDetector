from main import Model
from flask import Flask, request, jsonify
import tensorflow as tf
import pandas as pd


class webServer:
    def __init__(self):
        self.app = Flask(__name__)
        if len(tf.config.experimental.list_physical_devices('GPU')):
            device = "/GPU:0"
        else:
            device = "/CPU:0"
        self.model = Model(device, data=pd.read_csv("./phishing_site_urls.csv"))

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
        prediction = str(prediction*100)
        output = {
            'prediction': prediction,
            'danger': danger
        }
        return output

    def run(self):
        self.app.run(debug=True)


if __name__ == "__main__":
    server = webServer()
    server.run()