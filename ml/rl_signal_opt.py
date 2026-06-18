"""
Minimal RL environment placeholder for traffic signal optimization.
This provides a Gymnasium-compatible environment for Stable Baselines 3.
"""
import numpy as np
import gymnasium as gym
from gymnasium import spaces

class TrafficSignalEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, intersections=1, max_steps=100):
        super().__init__()
        self.intersections = intersections
        self.max_steps = max_steps
        self.current_step = 0
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(intersections, 3),
            dtype=np.float32
        )
        self.action_space = spaces.Discrete(3)
        self.state = np.zeros((intersections, 3), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.state = np.zeros((self.intersections, 3), dtype=np.float32)
        return self.state, {}

    def step(self, action):
        self.current_step += 1
        self.state = self.state + np.random.randn(*self.state.shape).astype(np.float32)
        reward = -np.random.rand()
        terminated = self.current_step >= self.max_steps
        truncated = False
        info = {'action': int(action)}
        return self.state, float(reward), terminated, truncated, info

    def render(self):
        print('Step', self.current_step, 'State', self.state)

if __name__ == '__main__':
    env = TrafficSignalEnv()
    obs, _ = env.reset()
    for _ in range(10):
        action = env.action_space.sample()
        obs, r, terminated, truncated, _ = env.step(action)
        print('action', action, 'reward', r, 'done', terminated or truncated)
        if terminated or truncated:
            obs, _ = env.reset()
