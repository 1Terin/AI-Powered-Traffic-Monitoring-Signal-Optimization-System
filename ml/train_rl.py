"""Reinforcement Learning traffic signal optimization with PPO and MQTT control."""
import argparse
import json
import os
import time

import numpy as np
from rl_signal_opt import TrafficSignalEnv

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

try:
    from stable_baselines3 import PPO
    SB3_AVAILABLE = True
except ImportError:
    SB3_AVAILABLE = False


PHASES = ['green', 'yellow', 'red']


def publish_signal_command(broker_url, intersection, phase, duration=30):
    if mqtt is None:
        print('MQTT unavailable; signal command:', intersection, phase, duration)
        return

    client = mqtt.Client()
    host = broker_url.replace('mqtt://', '').split(':')[0]
    port = 1883
    if ':' in broker_url.replace('mqtt://', ''):
        port = int(broker_url.replace('mqtt://', '').split(':')[1])
    client.connect(host, port)
    payload = {
        'intersection': intersection,
        'action': 'set_phase',
        'phase': phase,
        'duration': duration
    }
    client.publish('control/signals/commands', json.dumps(payload))
    client.disconnect()


def train_agent(env, timesteps=5000):
    if SB3_AVAILABLE:
        model = PPO('MlpPolicy', env, verbose=0)
        model.learn(total_timesteps=timesteps)
        return model
    return None


def run_random_policy(env, timesteps=1000):
    obs, _ = env.reset()
    total_reward = 0.0
    for _ in range(timesteps):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, _ = env.step(action)
        total_reward += reward
        if terminated or truncated:
            obs, _ = env.reset()
    return total_reward


def run_live_control(env, model, broker_url, intersection='A1', steps=100, interval=5):
    obs, _ = env.reset()
    print(f'Running live RL signal control for {intersection} via MQTT')
    for step in range(steps):
        if model is not None:
            action, _ = model.predict(obs, deterministic=True)
        else:
            action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        phase = PHASES[int(action) % len(PHASES)]
        duration = int(info.get('duration', 30))
        publish_signal_command(broker_url, intersection, phase, duration)
        print(f'step={step + 1} phase={phase} reward={reward:.2f} queue={info.get("queue", 0):.1f}')
        if terminated or truncated:
            obs, _ = env.reset()
        time.sleep(interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--timesteps', type=int, default=5000)
    parser.add_argument('--episodes', type=int, default=1)
    parser.add_argument('--live-steps', type=int, default=20)
    parser.add_argument('--interval', type=int, default=5)
    parser.add_argument('--intersection', default='A1')
    parser.add_argument('--mqtt', default=os.environ.get('MQTT_BROKER', 'mqtt://mqtt:1883'))
    args = parser.parse_args()

    env = TrafficSignalEnv(max_steps=100)
    model = None

    if SB3_AVAILABLE:
        print(f'Training PPO agent for {args.timesteps} timesteps...')
        model = train_agent(env, timesteps=args.timesteps)
        print('PPO training complete.')
    else:
        print('stable-baselines3 not installed; using random policy baseline.')
        for episode in range(args.episodes):
            total_reward = run_random_policy(env, timesteps=args.timesteps)
            print(f'Episode {episode + 1}/{args.episodes}: total_reward={total_reward:.2f}')

    run_live_control(
        env,
        model,
        args.mqtt,
        intersection=args.intersection,
        steps=args.live_steps,
        interval=args.interval
    )
