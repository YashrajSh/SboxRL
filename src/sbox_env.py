import gymnasium as gym
from gymnasium import spaces
import numpy as np
from src.ca_engine import HybridCAEngine 
from src.analyser import SBoxAnalyser

class SBoxEnv(gym.Env):
    def __init__(self):
        super().__init__()
        # Sir's Rules
        self.sir_rules = [30,45,75,86,89,101,106,135,149,153,165,169,210,90,150,84,57,63,61,231]
        self.num_avail = len(self.sir_rules)
        
        # Action: Pick 8 rules from the 20 available
        self.action_space = spaces.MultiDiscrete([self.num_avail] * 8)
        # Obs: The 8 current rules + best NL found
        self.observation_space = spaces.Box(low=0, high=255, shape=(9,), dtype=np.float32)
        
        self.engine = HybridCAEngine(n=8)
        self.analyser = SBoxAnalyser(n=8)
        self.state = np.random.randint(0, self.num_avail, size=(8,))
        self.best_nl = 0

    def step(self, action):
        self.state = action
        actual_rules = [self.sir_rules[i] for i in self.state]
        
        # Generate S-box in one functional call (Sir's request)
        sbox = self.engine.generate_sbox(actual_rules)
        
        # Calculate Strength
        p_norm, nl, du = self.analyser.get_p_norm_metrics(sbox)
        
        # Reward Logic: Minimize P-Norm (Max Walsh)
        reward = 100.0 - (p_norm / 5.0)
        
        # Massive Bonuses for DRDO Targets
        if nl >= 100: reward += 1000
        if du <= 8:   reward += 500

        self.best_nl = max(self.best_nl, nl)
        terminated = (nl >= 104 and du <= 6)
        
        obs = np.append(self.state, [float(self.best_nl / 128.0)])
        return obs.astype(np.float32), float(reward), terminated, False, {"nl": nl, "du": du}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.random.randint(0, self.num_avail, size=(8,))
        return np.append(self.state, [0.0]).astype(np.float32), {}