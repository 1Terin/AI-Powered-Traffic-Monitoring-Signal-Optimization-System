"""
Small helper to download and preprocess listed datasets (user must provide Kaggle credentials).
This script is intentionally minimal: it outlines how to download and prepare CSV datasets for training.
"""
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), 'datasets')
os.makedirs(DATA_DIR, exist_ok=True)

# Placeholders: user should download datasets manually or provide Kaggle API tokens
DATASETS = {
    'smart_traffic_management': 'smart_traffic_management.csv',
    'real_environment_images': 'real_env_images.zip',
    'smart_traffic_monitoring': 'smart_traffic_monitoring.csv'
}

def load_csv(name):
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}. Download from Kaggle and place it there.")
    return pd.read_csv(path)

if __name__ == '__main__':
    print('Available datasets:')
    for k,v in DATASETS.items():
        p = os.path.join(DATA_DIR, v)
        print('-', k, '->', p, '(exists)' if os.path.exists(p) else '(missing)')
