# SPEC-100 Tasks

## TASK-100-001: Lock Repository Baselines

Status: COMPLETE
Dependencies: none
Allowed files: specs/100-jc-public-baseline/evidence/baselines.json
Acceptance: AC-100-001 — baselines.json contains exactly 3 entries with valid SHA format

## TASK-100-002: Inventory Formal Repository

Status: COMPLETE
Dependencies: TASK-100-001
Allowed files: specs/100-jc-public-baseline/evidence/formal-inventory.json
Acceptance: AC-100-002 — count matches `git ls-files | wc -l`

## TASK-100-003: Inventory JC Repository

Status: COMPLETE
Dependencies: TASK-100-001
Allowed files: specs/100-jc-public-baseline/evidence/jc-inventory.json
Acceptance: AC-100-003 — count matches `git ls-files | wc -l`

## TASK-100-004: Scan Root License Files

Status: COMPLETE
Dependencies: TASK-100-002, TASK-100-003
Allowed files: specs/100-jc-public-baseline/evidence/license-scan.json
Acceptance: AC-100-004 — every repository has a root license entry or flagged absence

## TASK-100-005: Scan File-Level License Markers

Status: COMPLETE
Dependencies: TASK-100-004
Allowed files: specs/100-jc-public-baseline/evidence/license-markers.json
Acceptance: AC-100-005 — every tracked file has a marker entry or flagged absence

## TASK-100-006: Scan Third-Party References

Status: COMPLETE
Dependencies: TASK-100-002, TASK-100-003
Allowed files: specs/100-jc-public-baseline/evidence/third-party-scan.json
Acceptance: AC-100-006 — every third-party dependency has a license entry or flagged absence

## TASK-100-007: Identify Currently Public Paths

Status: COMPLETE
Dependencies: TASK-100-002, TASK-100-003, TASK-100-005
Allowed files: specs/100-jc-public-baseline/evidence/public-paths.json
Acceptance: AC-100-007 — every public path has evidence of public accessibility

## TASK-100-008: Classify PUBLIC_STANDARD

Status: COMPLETE
Dependencies: TASK-100-007
Allowed files: specs/100-jc-public-baseline/evidence/classifications/public_standard.json
Acceptance: AC-100-008 — each classified path has confidence + reason

## TASK-100-009: Classify PUBLIC_FORMAL

Status: COMPLETE
Dependencies: TASK-100-007
Allowed files: specs/100-jc-public-baseline/evidence/classifications/public_formal.json
Acceptance: AC-100-009 — each classified path has confidence + reason

## TASK-100-010: Classify PUBLIC_CORE

Status: COMPLETE
Dependencies: TASK-100-007
Allowed files: specs/100-jc-public-baseline/evidence/classifications/public_core.json
Acceptance: AC-100-010 — each classified path has confidence + reason

## TASK-100-011: Classify PUBLIC_REFERENCE

Status: COMPLETE
Dependencies: TASK-100-007
Allowed files: specs/100-jc-public-baseline/evidence/classifications/public_reference.json
Acceptance: AC-100-011 — each classified path has confidence + reason

## TASK-100-012: Classify COMMERCIAL_PRIVATE_FUTURE

Status: COMPLETE
Dependencies: TASK-100-007
Allowed files: specs/100-jc-public-baseline/evidence/classifications/commercial_private_future.json
Acceptance: AC-100-012 — each classified path has confidence + reason

## TASK-100-013: Classify PATENT_REVIEW

Status: COMPLETE
Dependencies: TASK-100-007
Allowed files: specs/100-jc-public-baseline/evidence/classifications/patent_review.json
Acceptance: AC-100-013 — each classified path has confidence + reason

## TASK-100-014: Classify THIRD_PARTY_REVIEW

Status: COMPLETE
Dependencies: TASK-100-007
Allowed files: specs/100-jc-public-baseline/evidence/classifications/third_party_review.json
Acceptance: AC-100-014 — each classified path has confidence + reason

## TASK-100-015: Validate Complete Path Coverage

Status: COMPLETE
Dependencies: TASK-100-008 through TASK-100-014
Allowed files: specs/100-jc-public-baseline/evidence/coverage-validation.json
Acceptance: AC-100-015 — unclassified count = 0, duplicate count = 0

## TASK-100-016: Generate PUBLIC_BASELINE_MANIFEST.md

Status: COMPLETE
Dependencies: TASK-100-015
Allowed files: specs/100-jc-public-baseline/evidence/reports/PUBLIC_BASELINE_MANIFEST.md
Acceptance: AC-100-016 — manifest contains all classified paths with category and reason

## TASK-100-017: Generate DISCLOSURE_FREEZE.md

Status: COMPLETE
Dependencies: TASK-100-015
Allowed files: specs/100-jc-public-baseline/evidence/reports/DISCLOSURE_FREEZE.md
Acceptance: AC-100-017 — freeze scope is clearly defined with references to classified paths

## TASK-100-018: Generate ASSET_CLASSIFICATION.json

Status: COMPLETE
Dependencies: TASK-100-015
Allowed files: specs/100-jc-public-baseline/evidence/reports/ASSET_CLASSIFICATION.json
Acceptance: AC-100-018 — JSON valid, all paths present, no duplicates

## TASK-100-019: Generate ASSET_CLASSIFICATION.md

Status: COMPLETE
Dependencies: TASK-100-018
Allowed files: specs/100-jc-public-baseline/evidence/reports/ASSET_CLASSIFICATION.md
Acceptance: AC-100-019 — markdown renders correctly, covers all paths from JSON

## TASK-100-020: Generate LICENSE_STATUS.md

Status: COMPLETE
Dependencies: TASK-100-004, TASK-100-005, TASK-100-006
Allowed files: specs/100-jc-public-baseline/evidence/reports/LICENSE_STATUS.md
Acceptance: AC-100-020 — every tracked file has a license status entry

## TASK-100-021: Generate HUMAN_REVIEW_REQUIRED.md

Status: COMPLETE
Dependencies: TASK-100-015
Allowed files: specs/100-jc-public-baseline/evidence/reports/HUMAN_REVIEW_REQUIRED.md
Acceptance: AC-100-021 — every LOW confidence item from prior tasks appears exactly once

## TASK-100-022: Red-Team Disclosure Language

Status: COMPLETE
Dependencies: TASK-100-016 through TASK-100-021
Acceptance: red_team_verdict = PASS or PASS_WITH_LIMITS

## TASK-100-023: Create Local Review Commit

Status: COMPLETE
Dependencies: TASK-100-022
Acceptance: commit exists locally, all reports in evidence directory
