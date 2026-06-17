"""
Train a PPO agent using Stable-Baselines3 on the TrafficSignalEnv provided in rl_signal_opt.py
Requires: stable-baselines3, gym, torch
"""
import argparse
import os

try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv
except Exception:
    PPO = None

from rl_signal_opt import TrafficSignalEnv


def make_env():
    return TrafficSignalEnv()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--timesteps', type=int, default=10000)
    parser.add_argument('--save-path', default='rl_signal_policy.zip')
    args = parser.parse_args()

    if PPO is None:
        print('stable-baselines3 not installed. Install with `pip install stable-baselines3`')
        exit(1)

    env = DummyVecEnv([make_env])
    model = PPO('MlpPolicy', env, verbose=1)
    model.learn(total_timesteps=args.timesteps)
    model.save(args.save_path)
    print('RL policy saved to', args.save_path)
