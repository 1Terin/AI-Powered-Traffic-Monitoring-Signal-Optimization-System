"""
Minimal LSTM time-series trainer for traffic flow prediction.
Requires: tensorflow, pandas, numpy
"""
import os
import numpy as np
import pandas as pd

try:
    import tensorflow as tf
    from tensorflow.keras import layers
except Exception:
    tf = None

DATA_CSV = os.path.join(os.path.dirname(__file__), '..', 'data_import', 'datasets', 'smart_traffic_management.csv')

def build_model(input_shape):
    model = tf.keras.Sequential([
        layers.Input(shape=input_shape),
        layers.LSTM(64, return_sequences=True),
        layers.LSTM(32),
        layers.Dense(16, activation='relu'),
        layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

if __name__ == '__main__':
    if tf is None:
        print('TensorFlow not installed. Install with `pip install tensorflow`')
        exit(1)

    if not os.path.exists(DATA_CSV):
        print('Dataset not found at', DATA_CSV)
        exit(1)

    df = pd.read_csv(DATA_CSV)
    # example: assume df has a 'vehicle_count' column
    series = df['vehicleCount' if 'vehicleCount' in df.columns else df.columns[0]].values.astype(float)
    seq_len = 10
    X, y = [], []
    for i in range(len(series) - seq_len):
        X.append(series[i:i+seq_len])
        y.append(series[i+seq_len])
    X = np.array(X)[..., None]
    y = np.array(y)

    model = build_model(X.shape[1:])
    model.fit(X, y, epochs=5, batch_size=32)
    model.save('lstm_traffic_model.h5')
    print('Training finished, model saved to lstm_traffic_model.h5')
