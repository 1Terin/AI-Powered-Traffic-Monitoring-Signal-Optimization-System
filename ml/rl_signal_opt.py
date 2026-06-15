"""
Minimal RL environment placeholder for traffic signal optimization.
This provides an OpenAI Gym-style environment stub.
"""
import numpy as np

class TrafficSignalEnv:
    def __init__(self, intersections=1):
        self.intersections = intersections
        self.observation_space = np.zeros((intersections, 3))
        self.action_space = [0,1,2]  # example: switch phase

    def reset(self):
        return self.observation_space

    def step(self, action):
        # stub: return next_obs, reward, done, info
        next_obs = self.observation_space + np.random.randn(*self.observation_space.shape)
        reward = -np.random.rand()
        done = False
        return next_obs, reward, done, {}

if __name__ == '__main__':
    env = TrafficSignalEnv()
    obs = env.reset()
    for _ in range(10):
        action = np.random.choice(env.action_space)
        obs, r, d, _ = env.step(action)
        print('action', action, 'reward', r)
