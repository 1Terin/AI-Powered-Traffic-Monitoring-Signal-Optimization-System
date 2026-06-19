"""
Dataset import helper for Kaggle traffic datasets and local demo data generation.
"""
import argparse
import os
import subprocess
import sys

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), 'datasets')
os.makedirs(DATA_DIR, exist_ok=True)

DATASETS = {
    'smart_traffic_management': {
        'filename': 'smart_traffic_management.csv',
        'kaggle': 'smmmmmmmmmmmm/smart-traffic-management-dataset'
    },
    'real_environment_images': {
        'filename': 'real_env_images.zip',
        'kaggle': 'hanif535/real-environment-vehicle-images'
    },
    'smart_traffic_monitoring': {
        'filename': 'smart_traffic_monitoring.csv',
        'kaggle': 'programmer3/smart-traffic-monitoring-dataset'
    },
    'perception_adaptive': {
        'filename': 'perception_adaptive_traffic.csv',
        'external': 'https://rosap.ntl.bts.gov/view/dot/84510'
    }
}


def load_csv(name):
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}. Download from Kaggle and place it there.")
    return pd.read_csv(path)


def download_with_kaggle(dataset_slug, target_name):
    output_path = os.path.join(DATA_DIR, target_name)
    if os.path.exists(output_path):
        print(f'Skipping {target_name}; already exists.')
        return output_path

    try:
        subprocess.run(
            ['kaggle', 'datasets', 'download', '-d', dataset_slug, '-p', DATA_DIR, '--unzip'],
            check=True
        )
        print(f'Downloaded {dataset_slug} into {DATA_DIR}')
        return output_path
    except FileNotFoundError:
        print('Kaggle CLI not installed. Install with: pip install kaggle')
    except subprocess.CalledProcessError as exc:
        print(f'Kaggle download failed for {dataset_slug}:', exc)
    return None


def ensure_demo_dataset():
    demo_script = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'create_demo_dataset.py')
    demo_path = os.path.join(DATA_DIR, 'demo_traffic.csv')
    if os.path.exists(demo_path):
        return demo_path
    if os.path.exists(demo_script):
        subprocess.run([sys.executable, demo_script], check=False)
    return demo_path if os.path.exists(demo_path) else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true', help='Attempt Kaggle downloads when credentials are configured')
    args = parser.parse_args()

    print('Dataset inventory:')
    for key, meta in DATASETS.items():
        path = os.path.join(DATA_DIR, meta['filename'])
        status = 'exists' if os.path.exists(path) else 'missing'
        print(f'- {key}: {path} ({status})')
        if args.download and status == 'missing' and meta.get('kaggle'):
            download_with_kaggle(meta['kaggle'], meta['filename'])

    demo_path = ensure_demo_dataset()
    if demo_path:
        print(f'Demo dataset ready at {demo_path}')


if __name__ == '__main__':
    main()
