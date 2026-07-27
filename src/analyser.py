import numpy as np

class SBoxAnalyser:
    def __init__(self, n=8):
        self.n = n
        self.size = 2**n
        self.H = self._hadamard_matrix(n).astype(np.int32)
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
        """Returns (Non-linearity, Differential Uniformity, Max-Walsh)"""
        sbox_arr = np.asarray(sbox, dtype=np.int32)[:256]
        # Walsh Transform
        F = self.pop_parity[1:, sbox_arr] 
        F_pm = 1 - 2 * F
        W = np.matmul(F_pm, self.H)
        max_w = np.max(np.abs(W))
        nl = int(128 - (max_w // 2))
        
        # Differential Uniformity
        max_du = 0
        for a in range(1, 256):
            diffs = sbox_arr[np.arange(256) ^ a] ^ sbox_arr
            counts = np.bincount(diffs, minlength=256)
            max_du = max(max_du, counts.max())
            
        return nl, int(max_du), int(max_w)