from main import Model
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf


class WebServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)

        # Detect device
        device = "/GPU:0" if tf.config.experimental.list_physical_devices('GPU') else "/CPU:0"
        print("Initialising model and loading saved state...")
        self.model = Model(device, data=None)

        self.app.route("/process", methods=["POST"])(self.process)

    def process(self):
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No URL provided'}), 400

        url = data['text']
        result = self.processData(url)
        return jsonify(result)

    def processData(self, url):
        predictionVal, dangerMsg = self.model.predict(url)#
        percentage = round(float(predictionVal) * 100, 2)

        print(f"URL: {url} | Score: {percentage}% | Status: {dangerMsg}")

        return {
            'prediction': str(percentage),
            'worstCase': percentage,
            'danger': dangerMsg
        }

    def run(self):
        self.app.run(debug=True, port=5000)


if __name__ == "__main__":
    server = WebServer()
    server.run()