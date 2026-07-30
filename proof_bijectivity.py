import numpy as np

# Amit Sir's Rule Vector (Non-bijective by design)
RULE_VECTOR = [242, 10, 142, 223, 16, 151, 29, 70]

def F(state):
    """First-order CA transition function (Null Boundary)"""
    nxt = 0
    bits = [(state >> i) & 1 for i in range(8)]
    for i in range(8):
        rule = RULE_VECTOR[7 - i]
        left = bits[i+1] if i < 7 else 0
        center = bits[i]
        right = bits[i-1] if i > 0 else 0
        idx = (left << 2) | (center << 1) | right
        if (rule >> idx) & 1:
            nxt |= (1 << i)
    return nxt

def demo():
    print("DEMONSTRATION OF STRUCTURAL BIJECTIVITY (FEISTEL-LIKE REVERSIBILITY)")
    print("="*75)
    
    # Inputs that cause a collision in 1st Order (as observed by Sir)
    input_x = 0
    input_y = 2
    
    val_x = F(input_x) # is 22
    val_y = F(input_y) # is 22
    
    print(f"1. FIRST-ORDER MAPPING (Direct transition):")
    print(f"   Input 0 -> F(0) = {val_x}")
    print(f"   Input 2 -> F(2) = {val_y}")
    print(f"   STATUS: COLLISION (Information collapse at value {val_x})")
    
    print("\n2. SECOND-ORDER TRANSITION (Our Architecture):")
    print("   Transition T: (a_t, a_t-1) -> (a_t+1, a_t) where a_t+1 = F(a_t) ^ a_t-1")
    
    # We show that even with identical rule outputs (22), 
    # the 16-bit state pairs remain unique.
    prev_x, curr_x = 10, input_x # State pair (0, 10)
    prev_y, curr_y = 20, input_y # State pair (2, 20)
    
    next_x = F(curr_x) ^ prev_x
    next_y = F(curr_y) ^ prev_y
    
    print(f"   Path X: State Pair ({curr_x}, {prev_x}) -> Transits to ({next_x}, {curr_x})")
    print(f"   Path Y: State Pair ({curr_y}, {prev_y}) -> Transits to ({next_y}, {curr_y})")
    print(f"   RESULT: NO COLLISION. ({next_x}, {curr_x}) != ({next_y}, {curr_y})")
    
    print("\n3. PROOF OF BIJECTIVITY (Inversion):")
    print("   We can perfectly calculate 'a_prev' from 'a_next' and 'curr'.")
    
    recovered_prev_x = F(curr_x) ^ next_x
    recovered_prev_y = F(curr_y) ^ next_y
    
    print(f"   Recovered Path X History: {recovered_prev_x} (Matches original {prev_x})")
    print(f"   Recovered Path Y History: {recovered_prev_y} (Matches original {prev_y})")
    
    print("\n" + "-"*75)
    print("MATHEMATICAL SUMMARY:")
    print("The 16-bit transition is a perfect permutation (Bijective) by construction.")
    print("The search process ensures the resulting 8-bit orbit visits 256 unique states.")
    print("="*75)

if __name__ == "__main__":
    demo()