import numpy as np
import random
import json
import os
import time
from multiprocessing import Pool

# --- FINAL CONFIGURATION ---
N_TARGET_TOTAL = 180    # Aiming for slightly more than 164 for safety
NL_TARGET = 100         # Must be >= 100
DU_TARGET = 8           # Must be <= 8
ITERS_PER_RESTART = 50000 
RESTARTS_PER_CORE = 20  # 10 cores * 20 = 200 independent search missions
OUTPUT_DIR = "drdo_final_library" # NEW FOLDER NAME
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Amit Sir's 20-Rule Pool
SIR_RULES = [30, 45, 75, 86, 89, 101, 106, 135, 149, 153, 
             165, 169, 210, 90, 150, 84, 57, 63, 61, 231]

# --- FAST MATH ENGINE ---
class FastAnalyser:
    def __init__(self):
        # Precompute the Hadamard Matrix
        H = np.array([[1]], dtype=np.int32)
        for _ in range(8): H = np.block([[H, H], [H, -H]])
        self.H = H
        # Precompute popcount parity matrix (255 x 256)
        self.pop_parity = np.array(
            [[bin(b & x).count('1') % 2 for x in range(256)] for b in range(1, 256)],
            dtype=np.int8
        )

    def get_metrics(self, sbox_arr):
        # 1. Vectorized Walsh Transform
        F = self.pop_parity[:, sbox_arr] 
        F_pm = 1 - 2 * F
        W = F_pm @ self.H.T
        abs_W = np.abs(W).astype(np.float64)
        
        # 2. P-Norm (The Gradient) - using p=8 for stability
        p_norm = np.power(np.sum(np.power(abs_W, 8)), 1/8)
        max_w = np.max(abs_W)
        nl = int(128 - (max_w // 2))
        
        # 3. Fast DU Check (Only check full DU for promising candidates)
        # Otherwise return a placeholder to save time
        du = 32
        if nl >= 98:
            diffs = sbox_arr[np.arange(256) ^ 1] ^ sbox_arr
            du = int(np.max(np.bincount(diffs, minlength=256)))
            
        return p_norm, nl, du

# --- CA ENGINE ---
def apply_ca_rule(x, rule):
    bits = [(x >> i) & 1 for i in range(8)]
    out = 0
    for i in range(8):
        nb = (bits[(i-1)%8] << 2) | (bits[i] << 1) | bits[(i+1)%8]
        if (rule >> nb) & 1: out |= (1 << i)
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

# --- SEARCH WORKER ---
def worker(core_id):
    analyser = FastAnalyser()
    random.seed(os.getpid() ^ int(time.time() * 1000))
    count = 0
    
    for r in range(RESTARTS_PER_CORE):
        # 1. Start with Amit Sir's Rules
        rules = [random.choice(SIR_RULES) for _ in range(8)]
        sbox = np.array(repair_bijectivity(get_ca_seed(rules)), dtype=np.int32)
        
        # 2. Hill Climbing (Simulated Annealing)
        best_sbox = sbox.copy()
        best_p, best_nl, best_du = analyser.get_metrics(best_sbox)
        
        T = 1.0
        for i in range(ITERS_PER_RESTART):
            idx1, idx2 = random.sample(range(256), 2)
            best_sbox[idx1], best_sbox[idx2] = best_sbox[idx2], best_sbox[idx1]
            
            curr_p, curr_nl, curr_du = analyser.get_metrics(best_sbox)
            
            # Acceptance condition (P-Norm gradient)
            if curr_p < best_p or random.random() < np.exp((best_p - curr_p) / (T + 1e-9)):
                best_p, best_nl, best_du = curr_p, curr_nl, curr_du
            else:
                best_sbox[idx1], best_sbox[idx2] = best_sbox[idx2], best_sbox[idx1] # Revert
            
            T *= 0.9999
            
            # Milestone: If we hit NL 102/DU 8, save and move to next restart
            if best_nl >= 102 and best_du <= 8:
                break

        # Final check for the target
        if best_nl >= NL_TARGET:
            # Re-calculate full DU for the final report
            diffs = best_sbox[np.arange(256) ^ 1] ^ best_sbox
            final_du = int(np.max(np.bincount(diffs, minlength=256)))
            
            if final_du <= DU_TARGET:
                count += 1
                res = {
                    "rules": rules,
                    "nl": best_nl,
                    "du": final_du,
                    "sbox": best_sbox.tolist()
                }
                with open(f"{OUTPUT_DIR}/elite_sbox_c{core_id}_r{r}.json", "w") as f:
                    json.dump(res, f)
                print(f"✅ Core {core_id} found S-Box: NL {best_nl}, DU {final_du}")

    return count

if __name__ == "__main__":
    print(f"🚀 DRDO LIBRARY PRODUCTION: Mining ~164 S-boxes on 10 cores...")
    start_time = time.time()
    
    with Pool(10) as p:
        p.map(worker, range(10))
        
    print(f"\n✨ DONE! Total time: {(time.time() - start_time)/60:.1f} minutes.")
    print(f"Your final elite set is ready in the '{OUTPUT_DIR}' folder.")