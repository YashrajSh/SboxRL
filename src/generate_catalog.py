import numpy as np
import os

def is_semi_bent_4n(rule_number):
    """
    Checks if a 4-neighborhood CA rule is Semi-Bent and Balanced.
    """
                                  
    bin_rule = [int(x) for x in np.binary_repr(rule_number, width=16)[::-1]]
    
                                                                            
    if sum(bin_rule) != 8:
        return False

                                                         
    f = [1 - 2*b for b in bin_rule]
    
                                      
    def fwht(a):
        if len(a) == 1: return a
        half = len(a) // 2
        left = fwht(a[0:half])
        right = fwht(a[half:])
        return np.concatenate([left + right, left - right])
    
    wht = fwht(np.array(f))
    
                                                     
                                              
    abs_wht = np.abs(wht)
    unique_vals = set(abs_wht)
    
    return unique_vals == {0, 8}

if __name__ == "__main__":
    print("Step 1: Scanning all 65,536 rules for Semi-Bent properties...")
    catalog = []
    
                                         
    for r in range(65536):
        if is_semi_bent_4n(r):
            catalog.append(r)
        
        if r % 10000 == 0:
            print(f"Progress: {r}/65536 rules checked...")

    print(f"Done! Found {len(catalog)} Semi-Bent rules.")
    
                                                           
    save_path = os.path.join("src", "semi_bent_catalog.npy")
    np.save(save_path, np.array(catalog))
    print(f"Catalog saved to {save_path}")