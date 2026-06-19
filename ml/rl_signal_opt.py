"""
Gymnasium environment for adaptive traffic signal optimization.
State: [queue_length, avg_speed, pollution_index]
Actions: 0=green, 1=yellow, 2=red
"""
import numpy as np
import gymnasium as gym
from gymnasium import spaces


class TrafficSignalEnv(gym.Env):
    metadata = {'render_modes': ['human']}

    def __init__(self, intersections=1, max_steps=100):
        super().__init__()
        self.intersections = intersections
        self.max_steps = max_steps
        self.current_step = 0
        self.observation_space = spaces.Box(
            low=0,
            high=np.array([100.0, 120.0, 300.0], dtype=np.float32),
            shape=(3,),
            dtype=np.float32
        )
        self.action_space = spaces.Discrete(3)
        self.state = np.zeros(3, dtype=np.float32)
        self.phase_durations = {0: 45, 1: 5, 2: 30}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.state = np.array([
            self.np_random.uniform(5, 30),
            self.np_random.uniform(20, 60),
            self.np_random.uniform(30, 100)
        ], dtype=np.float32)
        return self.state, {}

    def step(self, action):
        self.current_step += 1
        action = int(action) % 3
        queue, speed, pollution = self.state

        arrivals = self.np_random.uniform(2, 12)
        if action == 0:
            queue = max(0, queue + arrivals - self.np_random.uniform(8, 18))
            speed = min(120, speed + self.np_random.uniform(0, 4))
        elif action == 1:
            queue = max(0, queue + arrivals - self.np_random.uniform(2, 6))
            speed = max(5, speed - self.np_random.uniform(0, 3))
        else:
            queue = min(100, queue + arrivals + self.np_random.uniform(0, 6))
            speed = max(5, speed - self.np_random.uniform(2, 8))

        pollution = min(300, pollution + queue * 0.05 + self.np_random.uniform(-2, 4))
        self.state = np.array([queue, speed, pollution], dtype=np.float32)

        reward = -(queue * 0.5 + pollution * 0.01) + (speed * 0.02)
        terminated = self.current_step >= self.max_steps
        truncated = False
        info = {
            'action': action,
            'queue': float(queue),
            'duration': self.phase_durations[action]
        }
        return self.state, float(reward), terminated, truncated, info

    def render(self):
        print('Step', self.current_step, 'State', self.state)


if __name__ == '__main__':
    env = TrafficSignalEnv()
    obs, _ = env.reset()
    for _ in range(10):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        print('action', action, 'reward', reward, 'info', info)
        if terminated or truncated:
            obs, _ = env.reset()
