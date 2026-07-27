import os
import json
import numpy as np
from src.analyser import SBoxAnalyser

# --- CONFIGURATION ---
RESULTS_DIR = "drdo_elite_results"

def verify_all_results():
    analyser = SBoxAnalyser(n=8)
    # Get all json files from the results folder
    files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('.json')]
    
    if not files:
        print(f"❌ No files found in {RESULTS_DIR}")
        return

    print(f"🔍 Found {len(files)} S-box files. Starting mathematical audit...")
    
    validated_results = []
    seen_tables = set()

    for filename in files:
        path = os.path.join(RESULTS_DIR, filename)
        with open(path, 'r') as f:
            data = json.load(f)
        
        # FIX: Check for both 'sbox' and 'table' keys
        table = data.get('sbox') or data.get('table')
        
        if table is None:
            print(f"⚠️ Warning: {filename} is missing the S-box table. Skipping.")
            continue
            
        # Use tuple to check for exact duplicates (deduplication)
        table_tuple = tuple(table)
        if table_tuple in seen_tables:
            continue
        seen_tables.add(table_tuple)
        
        # RE-VERIFY (Amit Sir's Strict Audit)
        is_bijective = (len(set(table)) == 256)
        
        # Use the full analyze method to get real NL and DU
        # (This ensures the report is 100% accurate)
        nl, du, _ = analyser.analyze(table)
        
        validated_results.append({
            "filename": filename,
            "rules": data.get('rules') or data.get('seed_rules'),
            "nl": nl,
            "du": du,
            "bijective": is_bijective
        })

    # SORT by NL (Highest first) then DU (Lowest first)
    validated_results.sort(key=lambda x: (-x['nl'], x['du']))

    print("\n" + "█"*85)
    print("🇮🇳  DRDO FINAL S-BOX AUDIT SUMMARY")
    print("█"*85)
    print(f"{'Rank':<4} | {'NL':<4} | {'DU':<4} | {'Bijective':<10} | {'Rules'}")
    print("-" * 85)
    
    for i, res in enumerate(validated_results):
        rank = i + 1
        bij_str = "✅ YES" if res['bijective'] else "❌ NO"
        # Print first 32 only to keep screen clean, but we save all
        if rank <= 40:
            print(f"{rank:<4} | {res['nl']:<4} | {res['du']:<4} | {bij_str:<10} | {res['rules']}")
    
    print("█" * 85)
    print(f"\nTotal Unique Elite S-boxes discovered: {len(validated_results)}")
    
    # Save the Final TOP 32 for Sir
    top_32 = validated_results[:32]
    with open("DRDO_TOP_32_REPORT.json", "w") as f:
        json.dump(top_32, f, indent=4)
        
    print(f"📄 Full report for top 32 saved to: DRDO_TOP_32_REPORT.json")

if __name__ == "__main__":
    verify_all_results()