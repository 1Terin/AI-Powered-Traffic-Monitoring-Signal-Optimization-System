import argparse
import numpy as np
import tensorflow as tf


def build_and_save(path):
    # tiny LSTM model for demo purposes
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(12, 1)),
        tf.keras.layers.LSTM(8, activation='tanh'),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')

    # train briefly on random data so weights aren't trivial
    x = np.random.rand(64, 12, 1).astype('float32')
    y = (x.sum(axis=1) / 12.0).astype('float32')
    model.fit(x, y, epochs=2, batch_size=16, verbose=0)

    model.save(path)
    print('Saved dummy model to', path)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', default='lstm_traffic_model.h5')
    args = p.parse_args()
    build_and_save(args.out)
