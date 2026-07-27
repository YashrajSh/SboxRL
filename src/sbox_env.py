import gymnasium as gym
from gymnasium import spaces
import numpy as np
from src.ca_engine import HybridCAEngine 
from src.analyser import SBoxAnalyser

class SBoxEnv(gym.Env):
    def __init__(self):
        super().__init__()
        # Rules pool from Amit Sir
        self.rules_pool = [30,45,75,86,89,101,106,135,149,153,165,169,210,90,150,84,57,63,61,231]
        
        # Action: [8 rules, Rotation k (0-7), Constant C (0-255)]
        self.action_space = spaces.MultiDiscrete([len(self.rules_pool)]*8 + [8, 256])
        
        # Obs: The 10 parameters + current NL
        self.observation_space = spaces.Box(low=0, high=255, shape=(11,), dtype=np.float32)
        
        self.engine = HybridCAEngine(n=8)
        self.analyser = SBoxAnalyser(n=8)
        self.state = np.zeros(10, dtype=np.int32)
        self.current_nl = 0

    def step(self, action):
        self.state = action
        rules = [self.rules_pool[i] for i in action[:8]]
        k = action[8]
        C = action[9]
        
        trajectory, cycle_len = self.engine.generate_sbox(rules, k, C)
        
        if cycle_len < 256:
            # GATED: Only reward cycle length progress
            reward = (cycle_len / 256.0)
            nl = 0
        else:
            # SUCCESS: We have a permutation! Optimize NL/DU
            p_norm, nl, du = self.analyser.get_p_norm_metrics(trajectory)
            # Claude's Reward: Minimize P-Norm
            reward = 100.0 - (p_norm / 10.0)
            if nl >= 100: reward += 500
            if du <= 6:   reward += 200

        self.current_nl = nl
        obs = np.append(self.state, [float(self.current_nl)]).astype(np.float32)
        return obs, float(reward), (nl >= 104), False, {"nl": nl, "cl": cycle_len}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = self.action_space.sample()
        return np.append(self.state, [0.0]).astype(np.float32), {}