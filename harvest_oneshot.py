import numpy as np
import random
import json
import os
import time
from multiprocessing import Pool

# --- AMIT SIR'S CONFIG ---
SIR_RULES = [30, 45, 75, 86, 89, 101, 106, 135, 149, 153, 165, 169, 210, 90, 150, 84, 57, 63, 61, 231]

# --- FAST MATH ENGINE ---
class FastAnalyser:
    def __init__(self):
        self.H = self._hadamard_matrix(8).astype(np.int32)
        self.pop_parity = np.array(
            [[bin(b & x).count('1') % 2 for x in range(256)] for b in range(1, 256)],
            dtype=np.int8
        )

    def _hadamard_matrix(self, n):
        H = np.array([[1]], dtype=np.int32)
        for _ in range(n): H = np.block([[H, H], [H, -H]])
        return H

    def get_score(self, sbox):
        sbox_arr = np.asarray(sbox, dtype=np.int32)
        F = self.pop_parity[:, sbox_arr] 
        F_pm = 1 - 2 * F
        W = F_pm @ self.H.T
        abs_W = np.abs(W).astype(np.float64)
        p_norm = np.power(np.sum(np.power(abs_W, 8)), 1/8)
        nl = int(128 - (np.max(abs_W) // 2))
        diffs = sbox_arr[np.arange(256) ^ 1] ^ sbox_arr
        du = int(np.max(np.bincount(diffs, minlength=256)))
        return p_norm, nl, du

# --- FEISTEL ENGINE ---
def F_func(nibble, rules):
    nxt = 0
    for i in range(4):
        idx = ((nibble >> ((i + 1) % 4)) & 1) << 2 | ((nibble >> i) & 1) << 1 | ((nibble >> ((i - 1) % 4)) & 1)
        if (rules[i] >> idx) & 1: nxt |= (1 << i)
    return nxt

def generate_feistel(rules_8):
    sbox = np.zeros(256, dtype=np.int32)
    rA, rB = rules_8[0:4], rules_8[4:8]
    for x in range(256):
        L, R = (x >> 4) & 0x0F, x & 0x0F
        L, R = R, F_func(R, rA) ^ L 
        L, R = R, F_func(R, rB) ^ L 
        L, R = R, F_func(R, rA) ^ L 
        L, R = R, F_func(R, rB) ^ L 
        sbox[x] = (L << 4) | R
    return sbox

# --- THE WORKER ---
def worker_task(worker_id):
    analyser = FastAnalyser()
    
    # 1. Start with a Feistel S-box from Sir's rules
    rules = [random.choice(SIR_RULES) for _ in range(8)]
    sbox = generate_feistel(rules)
    
    # 2. Hill Climb Refinement (The Closer)
    best_sbox = np.array(sbox, dtype=np.int32)
    best_p, best_nl, best_du = analyser.get_score(best_sbox)
    
    print(f"👷 Core {worker_id} started refining a Feistel seed (Base NL: {best_nl})")
    
    for i in range(50000): # Fast iterations
        idx1, idx2 = random.sample(range(256), 2)
        best_sbox[idx1], best_sbox[idx2] = best_sbox[idx2], best_sbox[idx1]
        
        curr_p, curr_nl, curr_du = analyser.get_score(best_sbox)
        
        if curr_nl > best_nl or (curr_nl == best_nl and curr_du <= best_du):
            best_nl, best_du, best_p = curr_nl, curr_du, curr_p
            if best_nl >= 102:
                print(f"🔥 Core {worker_id} reached NL 102! Saving...")
                return {
                    "seed_rules": rules,
                    "nl": best_nl,
                    "du": best_du,
                    "table": best_sbox.tolist()
                }
        else:
            best_sbox[idx1], best_sbox[idx2] = best_sbox[idx2], best_sbox[idx1]
            
    return None

if __name__ == "__main__":
    os.makedirs("oneshot_results", exist_ok=True)
    print(f"🚀 DRDO 10-Core Factory: Generating 9 S-Boxes (One-Shot Feistel + Refinement)")
    
    start = time.time()
    winners = []
    
    with Pool(10) as p:
        # We use imap to get results as they finish
        for result in p.imap_unordered(worker_task, range(100)):
            if result:
                winners.append(result)
                filename = f"oneshot_results/sbox_{len(winners)}_nl{result['nl']}.json"
                with open(filename, "w") as f:
                    json.dump(result, f)
                
                print(f"✅ Found {len(winners)}/9. (Time: {time.time()-start:.1f}s)")
                
                if len(winners) >= 9:
                    print(f"\n🎯 MISSION ACCOMPLISHED! Check the 'oneshot_results' folder.")
                    p.terminate()
                    break