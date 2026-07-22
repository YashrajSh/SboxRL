from src.ca_engine import CAEngine
from src.analyser import SBoxAnalyzer

engine = CAEngine(5)
analyzer = SBoxAnalyzer(5)

                                        
                                                     
my_rules = [30, 150, 86, 105, 120] 

sbox = engine.generate_sbox(my_rules)
bijective = analyzer.is_bijective(sbox)
nl = analyzer.calculate_nonlinearity(sbox)
du = analyzer.calculate_du(sbox)

print(f"S-Box generated: {sbox[:10]}...")                 
print(f"Is Bijective? {bijective}")
print(f"Non-linearity: {nl}")
print(f"Differential Uniformity: {du}")