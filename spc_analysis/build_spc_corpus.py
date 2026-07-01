"""Generate SPC real-data golden corpus for juris-calculus."""
import json, sys, os
from pathlib import Path

WORKSPACE_ROOT = Path(os.environ.get("DELI_WORKSPACE_ROOT", Path(__file__).resolve().parents[1])).resolve()
JC_ROOT = Path(os.environ.get("JURIS_CALCULUS_ROOT", WORKSPACE_ROOT.parent / "juris-calculus")).resolve()
sys.path.insert(0, str(JC_ROOT))
from compiler_core.argumentation import grounded_extension

OUT_DIR = str(WORKSPACE_ROOT / "spc_analysis" / "output")
CORPUS_DIR = str(JC_ROOT / "data" / "spc_golden_corpus")
os.makedirs(CORPUS_DIR, exist_ok=True)

with open(os.path.join(OUT_DIR, "filtered_horn_rules.json"), encoding='utf-8') as f:
    data = json.load(f)

rules = data['rules']
corpus_entries = []

# Group rules by source for organized corpus
for i, rule in enumerate(rules):
    text = rule['text']
    ctype = rule['conclusion_type']
    
    claims = [
        {"id": "PREMISE", "text": text[:100]},
        {"id": "CONCLUSION", "text": f"[{ctype.upper()}] {text[:80]}"},
    ]
    attacks = [("PREMISE", "CONCLUSION")] if ctype == 'prohibition' else []
    
    try:
        result = grounded_extension(claims, attacks)
        entry = {
            "rule_id": f"SPC-{i:04d}",
            "source": rule['source'],
            "source_page": rule['page'],
            "rule_type": ctype,
            "rule_text": text,
            "claims": claims,
            "attacks": attacks,
            "grounded_in": result.get("accepted", []),
            "grounded_out": result.get("rejected", []),
            "grounded_undec": result.get("undecided", []),
            "iterations": result.get("iterations", 0),
            "derived_bound": result.get("derived_bound", 0),
            "converged": result.get("convergent", False),
            "truncated": result.get("truncated", False),
            "trust_projection": {
                c: "TRUSTED" if c in result.get("accepted",[]) else "CONTESTED" 
                for c in [x['id'] for x in claims]
            },
        }
        corpus_entries.append(entry)
    except Exception as e:
        print(f"SKIP R{i}: {e}")

# Save individual files and manifest
for entry in corpus_entries:
    fname = f"{entry['rule_id']}.json"
    with open(os.path.join(CORPUS_DIR, fname), 'w', encoding='utf-8') as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)

# Manifest
manifest = {
    "corpus_name": "SPC Real Legal Rules Golden Corpus",
    "source": "SPC Adjudication Rules Database (OCR)",
    "total_rules": len(corpus_entries),
    "generated": "2026-06-23",
    "rule_types": {},
    "sources": {},
    "coverage": {
        "converged": sum(1 for e in corpus_entries if e['converged']),
        "truncated": sum(1 for e in corpus_entries if e['truncated']),
        "total": len(corpus_entries),
    },
}
for e in corpus_entries:
    manifest["rule_types"][e['rule_type']] = manifest["rule_types"].get(e['rule_type'], 0) + 1
    src = e['source'][:40]
    manifest["sources"][src] = manifest["sources"].get(src, 0) + 1

with open(os.path.join(CORPUS_DIR, "MANIFEST.json"), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"Generated {len(corpus_entries)} SPC golden corpus entries")
print(f"Converged: {manifest['coverage']['converged']}/{len(corpus_entries)}")
print(f"By type: {manifest['rule_types']}")
print(f"Saved to: {CORPUS_DIR}")
