"""Analyze SPC adjudication rules data for Horn rule extraction."""

from __future__ import annotations

import glob
import json
import os
import re
from pathlib import Path


def _spc_ocr_dir() -> Path:
    value = os.environ.get("SPC_OCR_JSON_DIR", "").strip()
    if not value:
        raise SystemExit("SPC_OCR_JSON_DIR must point to the SPC OCR JSON directory.")
    return Path(value).expanduser().resolve()


DATA_DIR = _spc_ocr_dir()
files = sorted(glob.glob(str(DATA_DIR / "*ocr*.json")))
print(f"Found {len(files)} JSON files")

rule_patterns = [
    (r"第[一二三四五六七八九十百千\d]+条", "法条引用"),
    (r"应当|必须", "义务性规范"),
    (r"不得|禁止", "禁止性规范"),
    (r"可以", "授权性规范"),
    (r"有下列情形之一的", "情形列举"),
    (r"要件|构成要件", "构成要件"),
    (r"审查要点", "审查要点"),
    (r"裁判规则", "裁判规则"),
]

total_pages = 0
rule_pages_total = 0
for fpath in files:
    with open(fpath, encoding="utf-8") as f:
        data = json.load(f)
    pages = data["total_pages"]
    total_pages += pages
    rule_pages = 0
    for page in data["pages"]:
        matches = [tag for pat, tag in rule_patterns if re.search(pat, page["text"])]
        if len(matches) >= 2:
            rule_pages += 1
    rule_pages_total += rule_pages
    short = os.path.basename(fpath)[:30]
    print(f"  {short}: {pages}p, rule pages={rule_pages} ({100 * rule_pages // pages if pages else 0}%)")

print(
    f"\nTotal: {total_pages} pages, {rule_pages_total} with rule patterns "
    f"({100 * rule_pages_total // total_pages if total_pages else 0}%)"
)
