import numpy as np

class HybridCAEngine:
    def __init__(self, n=8):
        self.n = n # Total bits (8)

    def F_function(self, nibble, rules):
        """4-bit Hybrid CA Round Function"""
        nxt = 0
        for i in range(4):
            # 3-neighborhood on 4 bits
            idx = ((nibble >> ((i + 1) % 4)) & 1) << 2 | \
                  ((nibble >> i) & 1) << 1 | \
                  ((nibble >> ((i - 1) % 4)) & 1)
            if (rules[i] >> idx) & 1:
                nxt |= (1 << i)
        return nxt

    def generate_sbox(self, rules_8):
        """
        4-Round Feistel Network.
        Bijective by construction. One-shot execution.
        """
        sbox = np.zeros(256, dtype=np.int32)
        # We split the 8 rules provided by RL into two sets for the rounds
        rules_set_A = rules_8[0:4]
        rules_set_B = rules_8[4:8]

        for x in range(256):
            L = (x >> 4) & 0x0F
            R = x & 0x0F
            
            # Round 1
            f1 = self.F_function(R, rules_set_A)
            L, R = R, f1 ^ L
            # Round 2
            f2 = self.F_function(R, rules_set_B)
            L, R = R, f2 ^ L
            # Round 3
            f3 = self.F_function(R, rules_set_A)
            L, R = R, f3 ^ L
            # Round 4
            f4 = self.F_function(R, rules_set_B)
            L, R = R, f4 ^ L
            
            sbox[x] = (L << 4) | R
        return sbox