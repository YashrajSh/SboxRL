from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecMonitor
import gymnasium as gym
import json, os
from src.sbox_env import HybridSBoxEnv

def make_env(rank):
    def _init():
        return gym.wrappers.TimeLimit(HybridSBoxEnv(), max_episode_steps=30)
    return _init

if __name__ == "__main__":
    os.makedirs("pure_ca_winners", exist_ok=True)
    num_cpu = 10 
    env = SubprocVecEnv([make_env(i) for i in range(num_cpu)])
    env = VecMonitor(env)

    model = PPO("MlpPolicy", env, verbose=1, learning_rate=1e-3, ent_coef=0.1)

    print("🚀 Starting Pure CA Search (256-cycle goal)...")
    
    # We run in segments of 100k steps, then check for winners
    for i in range(10):
        model.learn(total_timesteps=100000)
        
        # Check current policy for a winner
        test_env = HybridSBoxEnv()
        obs, _ = test_env.reset()
        for _ in range(100):
            action, _ = model.predict(obs, deterministic=False)
            obs, reward, done, _, info = test_env.step(action)
            
            if info.get('u') == 256:
                # Potential Winner Found!
                traj, _ = test_env.engine.get_trajectory([test_env.sir_rules[r] for r in test_env.state])
                nl, du, _ = test_env.analyser.analyze(traj)
                
                if nl >= 98:
                    with open(f"pure_ca_winners/sbox_nl{nl}.json", "w") as f:
                        json.dump({"rules": [test_env.sir_rules[r] for r in test_env.state], "nl": nl, "du": du, "table": traj}, f)
                    print(f"SAVED WINNER: NL {nl}, DU {du}")