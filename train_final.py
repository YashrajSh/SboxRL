import torch
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecMonitor
from src.sbox_env import SBoxEnv

def make_env(rank):
    def _init():
        return gym.wrappers.TimeLimit(SBoxEnv(), max_episode_steps=20)
    return _init

if __name__ == "__main__":
                               
    num_cpu = 8 
    env = SubprocVecEnv([make_env(i) for i in range(num_cpu)])
    env = VecMonitor(env)

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=2e-4,                                     
        n_steps=512,                                                       
        batch_size=64,
        ent_coef=0.1,
        device="cpu"
    )

    print(" PHASE A: Stable RVM Search on 8-bit Reversible CA")
    model.learn(total_timesteps=1000000)
    model.save("rvm_stable_model")