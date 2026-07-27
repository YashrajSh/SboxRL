import numpy as np

class HybridCAEngine:
    def __init__(self, n=8):
        self.n = n

    def apply_hybrid_first_order(self, state, rules):
        """
        Calculates the next 8-bit state.
        Each bit i is updated using its own rule[i].
        """
        new_state = 0
        for i in range(self.n):
            # 3-neighborhood: (Left, Self, Right)
            idx = ((state >> ((i - 1) % self.n)) & 1) << 2 | \
                  ((state >> i) & 1) << 1 | \
                  ((state >> ((i + 1) % self.n)) & 1)
            # The i-th rule from the vector decides the i-th bit
            new_state |= ((rules[i] >> idx) & 1) << i
        return new_state

    def get_orbit(self, rules, seed=0x01):
        """
        Generates a trajectory of 256 states.
        Returns: (list of states, unique_count)
        """
        curr = seed
        trajectory = []
        unique_states = set()
        
        for _ in range(256):
            if curr in unique_states:
                break
            unique_states.add(curr)
            trajectory.append(curr)
            curr = self.apply_hybrid_first_order(curr, rules)
            
        return trajectory, len(unique_states)