"""Extract Horn-like rules from SPC adjudication rules OCR data."""
import json, os, re, glob, sys
from pathlib import Path

def _spc_ocr_dir() -> Path:
    value = os.environ.get("SPC_OCR_JSON_DIR", "").strip()
    if not value:
        raise SystemExit("SPC_OCR_JSON_DIR must point to the SPC OCR JSON directory.")
    return Path(value).expanduser().resolve()


DATA_DIR = _spc_ocr_dir()
WORKSPACE_ROOT = Path(os.environ.get("DELI_WORKSPACE_ROOT", Path(__file__).resolve().parents[1])).resolve()
OUT_DIR = WORKSPACE_ROOT / "spc_analysis" / "output"
os.makedirs(OUT_DIR, exist_ok=True)

files = sorted(glob.glob(str(DATA_DIR / "*ocr*.json")))

# Patterns for rule extraction from Chinese legal text
CLAUSE_PAT = re.compile(r'第[一二三四五六七八九十百千\d]+条')
COND_PAT = re.compile(r'(有下列情形之一的[，。；]?)')
SHALL_PAT = re.compile(r'(应当|必须)')
MAY_PAT = re.compile(r'(可以)')
FORBID_PAT = re.compile(r'(不得|禁止)')
CASE_LIST_PAT = re.compile(r'[（(][一二三四五六七八九十\d]+[)）]')

# Collect rule-dense snippets
all_rules = []
stats = {"total_pages": 0, "rule_pages": 0, "extracted_rules": 0}

for fpath in files:
    fname = os.path.basename(fpath)
    with open(fpath, encoding='utf-8') as f:
        data = json.load(f)
    
    file_rules = []
    for page in data['pages']:
        text = page['text']
        stats["total_pages"] += 1
        
        # Score page for rule density
        score = sum([
            bool(CLAUSE_PAT.search(text)),
            bool(SHALL_PAT.search(text)),
            bool(COND_PAT.search(text)),
            bool(FORBID_PAT.search(text)),
        ])
        
        if score >= 2:
            stats["rule_pages"] += 1
            
            # Try to extract individual rules by splitting on clause numbers
            # Look for "第X条" prefixed clauses
            clauses = CLAUSE_PAT.split(text)
            for i, clause in enumerate(clauses):
                clause = clause.strip()
                if len(clause) > 30 and any(p.search(clause) for p in [SHALL_PAT, FORBID_PAT, MAY_PAT]):
                    # Check for condition→conclusion pattern
                    has_cond = COND_PAT.search(clause) or CASE_LIST_PAT.search(clause)
                    conclusion_type = ""
                    if SHALL_PAT.search(clause):
                        conclusion_type = "obligation"
                    elif FORBID_PAT.search(clause):
                        conclusion_type = "prohibition"
                    elif MAY_PAT.search(clause):
                        conclusion_type = "permission"
                    
                    file_rules.append({
                        "source": fname,
                        "page": page["page"],
                        "clause_index": i,
                        "text": clause[:500],
                        "has_condition": bool(has_cond),
                        "conclusion_type": conclusion_type,
                        "length": len(clause),
                    })
                    stats["extracted_rules"] += 1
    
    short_name = fname[:40]
    print(f"{short_name}: {len(file_rules)} rules extracted")
    all_rules.extend(file_rules)

# Save extracted rules
with open(os.path.join(OUT_DIR, "extracted_rules.json"), "w", encoding="utf-8") as f:
    json.dump({"stats": stats, "rules": all_rules[:500]}, f, ensure_ascii=False, indent=2)

print(f"\n=== Summary ===")
print(f"Total pages: {stats['total_pages']}")
print(f"Rule pages: {stats['rule_pages']} ({100*stats['rule_pages']//stats['total_pages']}%)")
print(f"Extracted rules: {stats['extracted_rules']}")
print(f"\n=== Sample Rules ===")
for r in all_rules[:8]:
    print(f"\n[{r['source'][:30]} p{r['page']}] type={r['conclusion_type']} cond={r['has_condition']}")
    print(f"  {r['text'][:200]}")
