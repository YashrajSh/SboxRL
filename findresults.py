import numpy as np
import json
import os
from stable_baselines3 import PPO
from src.sbox_env import HybridSBoxEnv
from src.analyser import SBoxAnalyser

# 1. Setup
MODEL_PATH = "drdo_reversible_final" # Change to your latest model name
os.makedirs("amit_sir_deliverables", exist_ok=True)
env = HybridSBoxEnv()
analyser = SBoxAnalyser(n=8)
model = PPO.load(MODEL_PATH)

print("🔍 Harvesting S-boxes from RL Model...")

found_winners = []
seen_rule_sets = set()

# We run 1000 trials to find different combinations the AI learned
for trial in range(1000):
    obs, _ = env.reset()
    # Use deterministic=False to get variety
    action, _ = model.predict(obs, deterministic=False)
    obs, reward, terminated, truncated, info = env.step(action)
    
    # Get the rules found in this trial
    current_rules = [env.sir_rules[i] for i in env.state]
    rule_key = tuple(sorted(current_rules)) # To ensure we don't save duplicates
    
    # Logic check:
    # 1. Did it produce 256 unique values? (Maximal Cycle)
    if info['u'] == 256:
        # Generate actual trajectory
        traj, _ = env.engine.get_trajectory(current_rules)
        
        # 2. Check Cryptographic Strength
        nl, du, _ = env.analyser.analyze(traj)
        
        if nl >= 96 and rule_key not in seen_rule_sets:
            seen_rule_sets.add(rule_key)
            winner = {
                "rules": current_rules,
                "nl": nl,
                "du": du,
                "table": traj
            }
            found_winners.append(winner)
            
            # Save individual file
            filename = f"amit_sir_deliverables/sbox_nl{nl}_du{du}_{len(found_winners)}.json"
            with open(filename, "w") as f:
                json.dump(winner, f)
                
            print(f"✅ Found Winner #{len(found_winners)}: NL={nl}, DU={du}")

    if (trial + 1) % 100 == 0:
        print(f"   Checked {trial+1} samples...")

# --- FINAL SUMMARY ---
print("\n" + "="*50)
print("  DRDO FINAL HARVEST SUMMARY")
print("="*50)
print(f"Total Unique S-boxes Found: {len(found_winners)}")
print(f"Saved to: ./amit_sir_deliverables/")
print("="*50)

if len(found_winners) >= 6:
    print("\n🔥 GREAT RESULT! ")
else:
    print("\n⚠️  Only found a few. Consider training for 500k more steps.")