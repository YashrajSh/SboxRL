import numpy as np

class SBoxAnalyser:
    def __init__(self, n=8):
        self.n = 8
        self.size = 256
        self.H = self._hadamard_matrix(8).astype(np.int32)
        self.pop_parity = np.array(
            [[bin(b & x).count('1') % 2 for x in range(256)] for b in range(1, 256)],
            dtype=np.int32
        )

    def _hadamard_matrix(self, n):
        H = np.array([[1]], dtype=np.int32)
        for _ in range(n):
            H = np.block([[H, H], [H, -H]])
        return H

    def get_p_norm_metrics(self, sbox, p=8):
        sbox_arr = np.asarray(sbox, dtype=np.int32)
        F = self.pop_parity[:, sbox_arr] 
        F_pm = 1 - 2 * F
        W = F_pm @ self.H.T
        abs_W = np.abs(W).astype(np.float64)
        
        # P-Norm provides the gradient for RL
        p_norm = np.power(np.sum(np.power(abs_W, p)), 1/p)
        max_w = np.max(abs_W)
        nl = int(128 - (max_w // 2))
        
        # Fast DU check
        diffs = sbox_arr[np.arange(256) ^ 1] ^ sbox_arr
        du = int(np.max(np.bincount(diffs, minlength=256)))
            
        return p_norm, nl, du