import numpy as np

class HybridCAEngine:
    def __init__(self, n=8):
        self.n = n

    def apply_hybrid_rule(self, state, rules):
        new_state = 0
        for i in range(self.n):
            left  = (state >> ((i - 1) % self.n)) & 1
            mid   = (state >> i) & 1
            right = (state >> ((i + 1) % self.n)) & 1
            idx = (left << 2) | (mid << 1) | right
            bit_out = (rules[i] >> idx) & 1
            new_state |= (bit_out << i)
        return new_state

    def generate_sbox(self, rules, seed=0x01):
        prev, curr = 0x00, seed
        trajectory = []
        visited_pairs = set()
        
        for _ in range(256):
                                                               
            state_pair = (curr << 8) | prev
            if state_pair in visited_pairs:
                break
            visited_pairs.add(state_pair)
            
            trajectory.append(curr)
            f_out = self.apply_hybrid_rule(curr, rules)
            nxt = f_out ^ prev
            prev, curr = curr, nxt
            
        return trajectory, len(set(trajectory))