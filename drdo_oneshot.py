import numpy as np
from src.analyser import SBoxAnalyser

# Your elite Rule Vector (or any from your library)
RULE_VECTOR = [242, 10, 142, 223, 16, 151, 29, 70]

def F_layer_4bit(nibble, rules):
    """
    4-bit Hybrid CA function F. 
    Sir asked for the expression; here it is bitwise.
    """
    nxt = 0
    # We only use the first 4 rules for the 4-bit nibble
    for i in range(4):
        # 3-neighborhood logic on 4 bits
        left   = (nibble >> ((i + 1) % 4)) & 1
        center = (nibble >> i) & 1
        right  = (nibble >> ((i - 1) % 4)) & 1
        
        idx = (left << 2) | (center << 1) | right
        if (rules[i] >> idx) & 1:
            nxt |= (1 << i)
    return nxt

def generate_oneshot_sbox(rules):
    sbox = np.zeros(256, dtype=np.int32)
    for x in range(256):
        # 1. Split 8-bit input into 4-bit L and R
        L = (x >> 4) & 0x0F
        R = x & 0x0F
        
        # 2. Apply One-Cycle Reversible Structure (Feistel Step)
        # a_next = F(a_curr) ^ a_prev
        # Here: a_prev = L, a_curr = R
        f_out = F_layer_4bit(R, rules)
        new_R = f_out ^ L
        new_L = R
        
        # 3. Combine to 8-bit output
        sbox[x] = (new_L << 4) | new_R
    return sbox

if __name__ == "__main__":
    analyser = SBoxAnalyser(n=8)
    sbox = generate_oneshot_sbox(RULE_VECTOR)
    
    print("--- DRDO ONE-SHOT REVERSIBLE S-BOX ---")
    print(f"Rules: {RULE_VECTOR[:4]} (applied to 4-bit nibbles)")
    
    # Verify Bijectivity
    unique = len(set(sbox))
    print(f"Bijectivity: {unique}/256 unique values found. ✅")
    
    # Calculate Metrics
    nl, du, _ = analyser.analyze(sbox)
    print(f"Non-linearity: {nl}")
    print(f"Diff. Uniformity: {du}")

    # --- EXAMPLE FOR SIR ---
    test_val = 0x45 # Input 69
    L, R = (test_val >> 4), (test_val & 0x0F)
    f_val = F_layer_4bit(R, RULE_VECTOR)
    out = (R << 4) | (f_val ^ L)
    print(f"\nExample for Sir:")
    print(f"Input: {test_val} (L={L}, R={R})")
    print(f"F({R}) = {f_val}")
    print(f"Output: ({R} << 4) | ({f_val} ^ {L}) = {out}")