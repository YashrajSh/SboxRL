import numpy as np
import random
import math
import json
import os
import time
from multiprocessing import Pool

# --- CONFIGURATION ---
NL_TARGET = 102
DU_TARGET = 8
ITERS_PER_CHAIN = 60000
RESTARTS_PER_CORE = 20
OUTPUT_DIR = "drdo_elite_results"
P_NORM = 8

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- FAST MATH ENGINE (THE M5 ACCELERATOR) ---
class FastAnalyser:
    def __init__(self):
        self.H = self._hadamard_matrix(8).astype(np.int32)
        # Precompute popcount parity matrix (255 x 256)
        self.pop_parity = np.array(
            [[bin(b & x).count('1') % 2 for x in range(256)] for b in range(1, 256)],
            dtype=np.int8
        )

    def _hadamard_matrix(self, n):
        H = np.array([[1]], dtype=np.int32)
        for _ in range(n):
            H = np.block([[H, H], [H, -H]])
        return H

    def get_score(self, sbox):
        sbox_arr = np.asarray(sbox, dtype=np.int32)
        # 1. Vectorized Walsh Transform
        F = self.pop_parity[:, sbox_arr] 
        F_pm = 1 - 2 * F
        W = F_pm @ self.H.T
        abs_W = np.abs(W).astype(np.float64)
        
        # 2. P-Norm (The Gradient)
        p_norm = np.power(np.sum(np.power(abs_W, P_NORM)), 1/P_NORM)
        max_w = np.max(abs_W)
        nl = int(128 - (max_w // 2))
        
        # 3. Fast DU
        diffs = sbox_arr[np.arange(256) ^ 1] ^ sbox_arr
        du = int(np.max(np.bincount(diffs, minlength=256)))
        
        # Cost function: Lower is better
        cost = p_norm + (10.0 * max(0, du - DU_TARGET))
        return cost, nl, du

# --- CA GENERATOR ---
def apply_ca_rule(x, rule):
    bits = [(x >> i) & 1 for i in range(8)]
    out = 0
    for i in range(8):
        nb = (bits[(i-1)%8], bits[i], bits[(i+1)%8])
        idx = nb[0]*4 + nb[1]*2 + nb[2]
        out |= ((rule >> idx) & 1) << i
    return out

def get_ca_seed(rules):
    # Second-order: a_{t+1} = F(a_t) ^ a_{t-1}
    table = np.arange(256, dtype=np.uint8)
    for r in rules:
        table = np.array([apply_ca_rule(int(x), r) for x in table], dtype=np.uint8)
    
    prev, curr = 0x00, 0x01
    traj = []
    for _ in range(256):
        traj.append(curr)
        nxt = int(table[curr]) ^ prev
        prev, curr = curr, nxt
    return traj

def repair_bijectivity(traj):
    seen = set()
    result = []
    for x in traj:
        if x not in seen:
            result.append(x)
            seen.add(x)
    missing = list(set(range(256)) - seen)
    random.shuffle(missing)
    return result + missing

# --- THE WORKER UNIT ---
def worker_task(worker_id):
    analyser = FastAnalyser()
    local_found = []
    
    for r in range(RESTARTS_PER_CORE):
        # 1. Generate Seed
        rules = [random.randint(0, 255) for _ in range(8)]
        sbox = repair_bijectivity(get_ca_seed(rules))
        
        # 2. Hill Climb (Annealing)
        best_sbox = np.array(sbox, dtype=np.int32)
        best_cost, best_nl, best_du = analyser.get_score(best_sbox)
        
        T = 1.0
        for i in range(ITERS_PER_CHAIN):
            idx1, idx2 = random.sample(range(256), 2)
            # Swap
            best_sbox[idx1], best_sbox[idx2] = best_sbox[idx2], best_sbox[idx1]
            
            curr_cost, curr_nl, curr_du = analyser.get_score(best_sbox)
            
            # Acceptance logic
            if curr_cost < best_cost or random.random() < math.exp((best_cost - curr_cost) / (T + 1e-9)):
                best_cost, best_nl, best_du = curr_cost, curr_nl, curr_du
            else:
                # Revert
                best_sbox[idx1], best_sbox[idx2] = best_sbox[idx2], best_sbox[idx1]
            
            T *= 0.9999
            
            # Check for Elite Success
            if best_nl >= NL_TARGET and best_du <= DU_TARGET:
                print(f"🔥 [Core {worker_id}] ELITE FOUND: NL {best_nl}, DU {best_du}")
                res = {
                    "rules": rules,
                    "nl": best_nl,
                    "du": best_du,
                    "sbox": best_sbox.tolist(),
                    "note": "CA-seeded, bijectivity-repaired, refined via hill-climbing"
                }
                local_found.append(res)
                # Save immediately
                with open(f"{OUTPUT_DIR}/sbox_nl{best_nl}_core{worker_id}_{r}.json", "w") as f:
                    json.dump(res, f)
                break # Move to next restart
                
    return local_found

if __name__ == "__main__":
    print(f"🚀 DRDO Elite Factory: Launching 10-core parallel search...")
    start = time.time()
    
    with Pool(10) as p:
        results = p.map(worker_task, range(10))
    
    flat_results = [item for sublist in results for item in sublist]
    print(f"\n✅ Done! Total Elite S-boxes found: {len(flat_results)}")
    print(f"Total Time: {(time.time() - start)/60:.1f} minutes.")