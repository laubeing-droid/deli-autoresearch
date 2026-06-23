"""Run extracted SPC Horn rules through juris-calculus grounded_extension."""
import json, sys, os
sys.path.insert(0, r"D:\Codex\juris-calculus")
from compiler_core.argumentation import grounded_extension

OUT_DIR = r"D:\Claude\数学证明自动研究\spc_analysis\output"
with open(os.path.join(OUT_DIR, "filtered_horn_rules.json"), encoding='utf-8') as f:
    data = json.load(f)

rules = data['rules']
results = []
stats = {"total": 0, "converged": 0, "truncated": 0, "accepted_count": 0, "undecided_count": 0}

for i, rule in enumerate(rules[:50]):  # First 50 for validation
    text = rule['text']
    ctype = rule['conclusion_type']
    
    # Build simple AAF: premise attacks conclusion, obligation/premise interaction
    claims = [
        {"id": "PREMISE", "text": text[:100]},
        {"id": "CONCLUSION", "text": f"[{ctype.upper()}] {text[:80]}"},
    ]
    
    # Obligation rules: premise implies conclusion
    # Prohibition rules: premise attacks forbidden action
    # Permission rules: premise permits action (no attack)
    if ctype == 'prohibition':
        attacks = [("PREMISE", "CONCLUSION")]
    elif ctype == 'obligation':
        attacks = []
    else:  # permission
        attacks = []
    
    try:
        result = grounded_extension(claims, attacks)
        results.append({
            "rule_id": i,
            "source": rule['source'],
            "page": rule['page'],
            "type": ctype,
            "text": text[:200],
            "grounded_accepted": result.get("accepted", []),
            "grounded_rejected": result.get("rejected", []),
            "grounded_undecided": result.get("undecided", []),
            "converged": result.get("convergent", False),
            "truncated": result.get("truncated", False),
            "iterations": result.get("iterations", 0),
            "derived_bound": result.get("derived_bound", 0),
        })
        stats["total"] += 1
        if result.get("convergent"):
            stats["converged"] += 1
        if result.get("truncated"):
            stats["truncated"] += 1
        stats["accepted_count"] += len(result.get("accepted", []))
        stats["undecided_count"] += len(result.get("undecided", []))
    except Exception as e:
        results.append({"rule_id": i, "error": str(e)})

# Save results
with open(os.path.join(OUT_DIR, "juris_validation_results.json"), "w", encoding='utf-8') as f:
    json.dump({"stats": stats, "results": results}, f, ensure_ascii=False, indent=2)

print(f"Validated {stats['total']} rules")
print(f"Converged: {stats['converged']}/{stats['total']}")
print(f"Truncated: {stats['truncated']}")
print(f"Avg accepted per rule: {stats['accepted_count']/stats['total']:.1f}" if stats['total']>0 else "N/A")
print(f"Avg undecided per rule: {stats['undecided_count']/stats['total']:.1f}" if stats['total']>0 else "N/A")

# Show samples
print("\n=== Validation Samples ===")
for r in results[:8]:
    if 'error' in r:
        print(f"  R{r['rule_id']}: ERROR {r['error'][:80]}")
    else:
        print(f"  R{r['rule_id']} [{r['type']}]: IN={r['grounded_accepted']} OUT={r['grounded_rejected']} conv={r['converged']}")