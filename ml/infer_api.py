from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODEL_PATHS = [
    os.path.join(os.path.dirname(__file__), 'lstm_traffic_model.h5'),
    os.path.join(PROJECT_ROOT, 'lstm_traffic_model.h5'),
    os.path.join(os.getcwd(), 'lstm_traffic_model.h5')
]

def find_model_path():
    for p in MODEL_PATHS:
        if os.path.exists(p):
            return p
    return None

app = Flask(__name__)
CORS(app)

model = None
try:
    model_file = find_model_path()
    if model_file:
        from tensorflow.keras.models import load_model
        model = load_model(model_file, compile=False)
        print('Loaded model from', model_file)
    else:
        print('No LSTM model found in expected locations.')
except Exception as e:
    print('Failed to load model:', e)
    model = None


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'model_loaded': model is not None})


@app.route('/predict', methods=['POST'])
def predict():
    payload = request.get_json() or {}
    window = payload.get('window')
    if window is None:
        return jsonify({'error': 'window missing'}), 400

    arr = np.array(window, dtype=np.float32)
    # allow 1D (seq,) or 2D (seq, features)
    if arr.ndim == 1:
        arr = arr.reshape(1, arr.shape[0], 1)
    elif arr.ndim == 2:
        arr = arr.reshape(1, arr.shape[0], arr.shape[1])

    try:
        if model is None:
            # fallback: predict last value (identity) to avoid blocking
            pred = float(arr[0, -1, 0])
        else:
            out = model.predict(arr)
            pred = float(out.flatten()[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'prediction': pred})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
