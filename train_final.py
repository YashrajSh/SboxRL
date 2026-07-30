from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecMonitor
import gymnasium as gym
from src.sbox_env import SBoxEnv

def make_env(rank):
    def _init():
        return gym.wrappers.TimeLimit(SBoxEnv(), max_episode_steps=50)
    return _init

if __name__ == "__main__":
    num_cpu = 10 
    env = SubprocVecEnv([make_env(i) for i in range(num_cpu)])
    env = VecMonitor(env)

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=1024,
        batch_size=128,
        ent_coef=0.1,
        device="cpu"
    )

    print("🚀 DRDO Mission: Training 4-Round One-Shot S-Box...")
    model.learn(total_timesteps=1000000)
    model.save("drdo_oneshot_elite")