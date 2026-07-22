import torch
from stable_baselines3 import PPO
from src.sbox_env import HybridSBoxEnv

limit = 255                  
try:
    model = PPO.load(f"hybrid_sbox_limit_{limit}")
    env = HybridSBoxEnv(rule_limit=limit)
    obs, _ = env.reset()
    
    found = False
    print(f"Checking {limit} range for 1000 samples...")

    for i in range(1000):
        action, _ = model.predict(obs, deterministic=False)                             
        obs, reward, done, _, info = env.step(action)
        
        if info['u'] == 32:
            sbox = env.engine.generate_sbox(env.rules)
            print("\n" + ""*10)
            print("SUCCESS! BIJECTIVE S-BOX FOUND")
            print(f"Rules: {env.rules}")
            print(f"Nonlinearity (NL): {info.get('nl', 'Calculating...')}")
            print(f"S-Box Table: {list(sbox)}")
            print(""*10)
            found = True
            break
            
    if not found:
        print(f" No bijective S-box found in the {limit} range yet. Try the 255 range!")

except FileNotFoundError:
    print(f"No model found for limit {limit}.")