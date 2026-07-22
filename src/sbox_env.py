import gymnasium as gym
from gymnasium import spaces
import numpy as np
from src.ca_engine import HybridCAEngine 
from src.analyser import SBoxAnalyser

class SBoxEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.sir_rules = [30,45,75,86,89,101,106,135,149,153,165,169,210,90,150,84,57,63,61,231]
        self.num_avail = len(self.sir_rules)
        self.action_space = spaces.Discrete(64)
        self.observation_space = spaces.Box(low=0, high=1, shape=(65,), dtype=np.float32)
        
        self.engine = HybridCAEngine(n=8)
        self.analyser = SBoxAnalyser(n=8)
        self.rule_bits = np.random.randint(0, 2, size=(64,))
        self.best_nl = 0

    def _get_obs(self, u):
        return np.append(self.rule_bits, [u / 256.0]).astype(np.float32)

    def step(self, action):
        self.rule_bits[action] = 1 - self.rule_bits[action]
        rules = [int("".join(map(str, self.rule_bits[i*8:(i+1)*8])), 2) for i in range(8)]
        
        trajectory, unique_count = self.engine.generate_sbox(rules)
        
                                    
                                                             
        found = set(trajectory)
        missing = list(set(range(256)) - found)
                                                                        
        full_sbox = list(dict.fromkeys(trajectory)) + missing
        
                                  
        full_sbox = full_sbox[:256]

                                  
        lse_cost, nl, du = self.analyser.get_p_norm_cost(full_sbox)
        
                      
        reward = -lse_cost / 20.0
        reward += (unique_count / 256.0) * 5.0
        
        if unique_count == 256:
            reward += 10.0
            if nl >= 96: reward += 50.0
        
        self.best_nl = max(self.best_nl, nl)
        return self._get_obs(unique_count), float(reward), False, False, {"nl": nl, "cl": unique_count}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.rule_bits = np.random.randint(0, 2, size=(64,))
        self.best_nl = 0
        return self._get_obs(0), {}