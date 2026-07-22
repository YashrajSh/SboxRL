import numpy as np
import random
from src.analyser import SBoxAnalyser

def refine(target_sbox, iterations=100000):
    analyser = SBoxAnalyser(n=8)
    
                                   
    unique = list(set(target_sbox))
    missing = list(set(range(256)) - set(unique))
    random.shuffle(missing)
    
    sbox = target_sbox[:]
    seen = set()
    for i in range(256):
        if sbox[i] in seen:
            sbox[i] = missing.pop()
        seen.add(sbox[i])
    
                                          
    best_sbox = np.array(sbox)
    _, best_nl, best_du = analyser.get_p_norm_cost(best_sbox)
    
    print(f"Starting Hill Climb. Initial NL: {best_nl}, DU: {best_du}")
    
    for i in range(iterations):
        idx1, idx2 = random.sample(range(256), 2)
              
        best_sbox[idx1], best_sbox[idx2] = best_sbox[idx2], best_sbox[idx1]
        
        _, nl, du = analyser.get_p_norm_cost(best_sbox)
        
                                                     
        if nl > best_nl or (nl == best_nl and du < best_du):
            best_nl = nl
            best_du = du
            if i % 1000 == 0:
                print(f"Iteration {i}: NL {nl}, DU {du}")
        else:
                         
            best_sbox[idx1], best_sbox[idx2] = best_sbox[idx2], best_sbox[idx1]
            
    return best_sbox, best_nl, best_du