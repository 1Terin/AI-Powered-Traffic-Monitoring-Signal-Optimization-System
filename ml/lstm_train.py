"""LSTM trainer script.
Usage: python ml/lstm_train.py --data path/to.csv --model-out lstm_traffic_model.h5
If no data is available or pandas is missing, it falls back to synthetic training.
"""
import argparse
import os

import numpy as np

try:
    import tensorflow as tf
    from tensorflow.keras.layers import Dense, LSTM
    from tensorflow.keras.models import Sequential
except Exception:
    tf = None


def build_model(seq_len, lstm_units=32):
    model = Sequential([
        LSTM(lstm_units, input_shape=(seq_len, 1)),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model


def make_sequences(series, seq_len):
    X, y = [], []
    for i in range(len(series) - seq_len):
        X.append(series[i:i + seq_len])
        y.append(series[i + seq_len])
    X = np.array(X)[..., None]
    y = np.array(y)
    return X, y


def train_on_synthetic(out_path, seq_len=12, epochs=5, batch=32):
    print('Training on synthetic data...')
    X = np.random.rand(512, seq_len, 1).astype('float32')
    y = X.mean(axis=1).astype('float32')
    model = build_model(seq_len)
    model.fit(X, y, epochs=epochs, batch_size=batch, verbose=1)
    model.save(out_path)
    print('Saved synthetic model to', out_path)


def train_on_csv(path, out_path, seq_len=12, epochs=10, batch=32):
    try:
        import pandas as pd
    except Exception:
        print('pandas not installed; falling back to synthetic training')
        return train_on_synthetic(out_path, seq_len=seq_len, epochs=epochs, batch=batch)

    print('Loading dataset from', path)
    df = pd.read_csv(path)
    col = 'vehicleCount' if 'vehicleCount' in df.columns else None
    if col is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            print('No numeric columns found; falling back to synthetic training')
            return train_on_synthetic(out_path, seq_len=seq_len, epochs=epochs, batch=batch)
        col = numeric_cols[0]

    series = df[col].values.astype(float)
    X, y = make_sequences(series, seq_len)
    if len(X) < 10:
        print('Not enough data for sequence training; using synthetic instead')
        return train_on_synthetic(out_path, seq_len=seq_len, epochs=epochs, batch=batch)

    model = build_model(seq_len)
    model.fit(X, y, validation_split=0.2, epochs=epochs, batch_size=batch, verbose=1)
    model.save(out_path)
    print(f'Saved trained model to {out_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default=os.path.join('data_import', 'datasets', 'smart_traffic_management.csv'))
    parser.add_argument('--seq-len', type=int, default=12)
    parser.add_argument('--epochs', type=int, default=5)
    parser.add_argument('--batch', type=int, default=32)
    parser.add_argument('--model-out', default='lstm_traffic_model.h5')
    args = parser.parse_args()

    if tf is None:
        print('TensorFlow is not installed. Install with `pip install tensorflow-cpu` or use the inference image.')
        exit(1)

    if args.data and os.path.exists(args.data):
        train_on_csv(args.data, args.model_out, seq_len=args.seq_len, epochs=args.epochs, batch=args.batch)
    else:
        train_on_synthetic(args.model_out, seq_len=args.seq_len, epochs=args.epochs, batch=args.batch)
