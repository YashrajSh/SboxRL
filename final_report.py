from src.analyser import SBoxAnalyser
from src.ca_engine import HybridCAEngine
import numpy as np

                    
winning_rules = [105, 105, 108, 105, 53]

engine = HybridCAEngine(n=5)
analyser = SBoxAnalyser(n=5)

sbox = engine.generate_sbox(winning_rules)

print("="*40)
print("       OFFICIAL S-BOX REPORT")
print("="*40)
print(f"Rules: {winning_rules}")
print(f"S-Box: {list(sbox)}")
print("-"*40)

                      
is_bij = analyser.is_bijective(sbox)
print(f"Bijective:        {is_bij}")

                                
nl = analyser.calculate_nonlinearity(sbox)
print(f"Non-linearity:    {nl}")

                                          
du = analyser.calculate_du(sbox)
print(f"Diff. Uniformity: {du}")
print("="*40)