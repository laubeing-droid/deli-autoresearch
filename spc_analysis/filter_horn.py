import json, sys, os
from collections import Counter

with open(r"D:\Claude\数学证明自动研究\spc_analysis\output\extracted_rules.json", encoding='utf-8') as f:
    data = json.load(f)

rules = data['rules']
# Filter: has_condition AND has conclusion_type
filtered = [r for r in rules if r['has_condition'] and r['conclusion_type']]
print(f"Condition + Conclusion rules: {len(filtered)} / {len(rules)}")

types = Counter(r['conclusion_type'] for r in filtered)
print(f"By type: {dict(types)}")

# Top sources
sources = Counter(r['source'] for r in filtered)
for s, c in sources.most_common(8):
    print(f"  {s[:50]}: {c}")

# Save filtered
out_path = r"D:\Claude\数学证明自动研究\spc_analysis\output\filtered_horn_rules.json"
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump({"total": len(filtered), "rules": filtered[:200]}, f, ensure_ascii=False, indent=2)
print(f"\nSaved {min(len(filtered),200)} rules to {out_path}")

# Show samples with text
print("\n=== Horn-like Rule Samples ===")
for r in filtered[:6]:
    print(f"\n[{r['conclusion_type'].upper()}] {r['source'][:30]} p{r['page']}")
    print(f"  {r['text'][:300]}")