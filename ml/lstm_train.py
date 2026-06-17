"""
Minimal LSTM time-series trainer for traffic flow prediction.
Usage examples:
python ml/lstm_train.py --data data_import/datasets/smart_traffic_management.csv --seq-len 12 --epochs 20
"""
import os
import argparse
import numpy as np
import pandas as pd

try:
    import tensorflow as tf
    from tensorflow.keras import layers, callbacks
except Exception:
    tf = None


def build_model(input_shape, lstm_units=64, dense_units=16):
    model = tf.keras.Sequential([
        layers.Input(shape=input_shape),
        layers.LSTM(lstm_units, return_sequences=True),
        layers.LSTM(max(16, lstm_units // 2)),
        layers.Dense(dense_units, activation='relu'),
        layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model


def make_sequences(series, seq_len):
    X, y = [], []
    for i in range(len(series) - seq_len):
        X.append(series[i:i + seq_len])
        y.append(series[i + seq_len])
    X = np.array(X)[..., None]
    y = np.array(y)
    return X, y


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default=os.path.join('data_import', 'datasets', 'smart_traffic_management.csv'))
    parser.add_argument('--seq-len', type=int, default=10)
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch', type=int, default=32)
    parser.add_argument('--val-split', type=float, default=0.2)
    parser.add_argument('--model-out', default='lstm_traffic_model.h5')
    parser.add_argument('--lstm-units', type=int, default=64)
    parser.add_argument('--dense-units', type=int, default=16)
    args = parser.parse_args()

    if tf is None:
        print('TensorFlow not installed. Install with `pip install tensorflow`')
        exit(1)

    if not os.path.exists(args.data):
        print('Dataset not found at', args.data)
        exit(1)

    df = pd.read_csv(args.data)
    # heuristics: find a numeric column for vehicle counts
    col = 'vehicleCount' if 'vehicleCount' in df.columns else None
    if col is None:
        # pick first numeric column
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            print('No numeric columns found in dataset')
            exit(1)
        col = numeric_cols[0]

    series = df[col].values.astype(float)
    X, y = make_sequences(series, args.seq_len)

    val_split = int(len(X) * (1 - args.val_split))
    X_train, X_val = X[:val_split], X[val_split:]
    y_train, y_val = y[:val_split], y[val_split:]

    model = build_model(X.shape[1:], lstm_units=args.lstm_units, dense_units=args.dense_units)

    es = callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=args.epochs, batch_size=args.batch, callbacks=[es])

    model.save(args.model_out)
    print(f'Training finished, model saved to {args.model_out}')
