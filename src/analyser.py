import numpy as np

class SBoxAnalyser:
    def __init__(self, n=8):
        self.n = 8
        self.size = 256
        self.H = self._hadamard_matrix(8).astype(np.int32)
                                      
        self.pop_parity = np.array(
            [[bin(b & x).count('1') % 2 for x in range(256)] for b in range(256)],
            dtype=np.int8
        )

    def _hadamard_matrix(self, n):
        H = np.array([[1]], dtype=np.int32)
        for _ in range(n):
            H = np.block([[H, H], [H, -H]])
        return H

    def analyze(self, sbox):
        """Returns (NL, DU, Max_Walsh)"""
        sbox_arr = np.asarray(sbox, dtype=np.int32)[:256]
        F = self.pop_parity[1:, sbox_arr] 
        F_pm = 1 - 2 * F
        W = np.matmul(F_pm, self.H)
        max_w = np.max(np.abs(W))
        nl = int(128 - (max_w // 2))
        du = self.calculate_du(sbox_arr)
        return nl, du, int(max_w)

    def get_p_norm_cost(self, sbox):
        """Stable cost function for RL and Hill Climbing"""
        sbox_arr = np.asarray(sbox, dtype=np.int32)[:256]
        F = self.pop_parity[1:, sbox_arr] 
        F_pm = (1 - 2 * F).astype(np.int32)
        W = F_pm @ self.H.T
        abs_W = np.abs(W).astype(np.float64)
        
        max_w = np.max(abs_W)
                                        
        lse_cost = max_w + np.log(np.sum(np.exp(abs_W - max_w)) + 1e-9)
        nl = int(128 - (max_w // 2))
        return lse_cost, nl, 0                                 

    def calculate_du(self, sbox):
        """Full Differential Uniformity calculation"""
        sbox_arr = np.asarray(sbox, dtype=np.int32)[:256]
        max_du = 0
        for a in range(1, 256):
            diffs = sbox_arr[np.arange(256) ^ a] ^ sbox_arr
            counts = np.bincount(diffs, minlength=256)
            max_du = max(max_du, counts.max())
        return int(max_du)