import numpy as np
import random
from stable_baselines3 import PPO
from src.sbox_env import SBoxEnv
from src.analyser import SBoxAnalyser

def repair_bijectivity(trajectory):
    unique_found = []
    seen = set()
    for x in trajectory:
        if x not in seen:
            unique_found.append(x)
            seen.add(x)
    missing = list(set(range(256)) - seen)
    random.shuffle(missing)
    return unique_found + missing

def hill_climb_refinement(sbox, iterations=100000):
    analyser = SBoxAnalyser(n=8)
    best_sbox = np.array(sbox, dtype=np.int32)
                         
    best_cost, best_nl, _ = analyser.get_p_norm_cost(best_sbox)
    best_du = analyser.calculate_du(best_sbox)
    
    print(f" Hill Climb Started. Initial NL: {best_nl}, DU: {best_du}")
    
    for i in range(iterations):
        idx1, idx2 = random.sample(range(256), 2)
                    
        best_sbox[idx1], best_sbox[idx2] = best_sbox[idx2], best_sbox[idx1]
        
                                                   
        curr_cost, curr_nl, _ = analyser.get_p_norm_cost(best_sbox)
        
                                                
        if curr_nl > best_nl or (curr_nl == best_nl and curr_cost < best_cost):
            curr_du = analyser.calculate_du(best_sbox)
            
                                                                                
            if curr_nl > best_nl or (curr_nl == best_nl and curr_du <= best_du):
                best_nl = curr_nl
                best_du = curr_du
                best_cost = curr_cost
                if i % 1000 == 0 or curr_nl > best_nl:
                    print(f" Step {i}: NL improved to {best_nl}, DU is {best_du}")
            else:
                best_sbox[idx1], best_sbox[idx2] = best_sbox[idx2], best_sbox[idx1]
        else:
                         
            best_sbox[idx1], best_sbox[idx2] = best_sbox[idx2], best_sbox[idx1]
            
    return best_sbox, best_nl, best_du

if __name__ == "__main__":
    model = PPO.load("rvm_stable_model")
    env = SBoxEnv()
    
    best_nl_found = 0
    best_candidate_sbox = []
    winning_rules = []

    print(" Extracting logic from PPO...")
    for _ in range(50):
        obs, _ = env.reset()
        action, _ = model.predict(obs, deterministic=False)
        obs, reward, term, trunc, info = env.step(action)
        
        if info['nl'] > best_nl_found:
            best_nl_found = info['nl']
            winning_rules = [int("".join(map(str, env.rule_bits[i*8 : (i+1)*8])), 2) for i in range(8)]
            trajectory, _ = env.engine.generate_sbox(winning_rules)
            best_candidate_sbox = repair_bijectivity(trajectory)

    print(f" Starting refinement from NL {best_nl_found}...")
    final_sbox, final_nl, final_du = hill_climb_refinement(best_candidate_sbox)

    print("\n" + ""*60)
    print(""*60)
    print(f"Final NL:         {final_nl} (Target > 100)")
    print(f"Final DU:         {final_du} (Target 4-8)")
    print("-" * 60)
    print("S-BOX TABLE:")
    print(list(final_sbox))
    print(""*60)