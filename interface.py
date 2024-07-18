import tensorflow as tf
import pandas as pd
from main import Model

if __name__ == '__main__':
    if len(tf.config.experimental.list_physical_devices('GPU')):
        device = "/GPU:0"
    else:
        device = "/CPU:0"
    model = Model(device=device, data=pd.read_csv("./phishing_site_urls.csv"))
    while True:
        print(model.predict(input("Please enter your url: ")))
