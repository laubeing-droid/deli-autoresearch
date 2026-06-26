# SPEC-100 Acceptance Criteria

## AC-100-001
baselines.json contains exactly 3 entries (deli-autoresearch, legal-math-modeling, juris-calculus) with valid 40-character hex SHA format.

## AC-100-002
formal-inventory.json file count matches `git ls-files | wc -l` in legal-math-modeling.

## AC-100-003
jc-inventory.json file count matches `git ls-files | wc -l` in juris-calculus.

## AC-100-004
Every repository has a root license entry or flagged absence in license-scan.json.

## AC-100-005
Every tracked file has a marker entry or flagged absence in license-markers.json.

## AC-100-006
Every third-party dependency has a license entry or flagged absence in third-party-scan.json.

## AC-100-007
Every public path has evidence of public accessibility in public-paths.json.

## AC-100-008 through AC-100-014
Each classified path in the respective classification file has confidence (HIGH/MEDIUM/LOW) + reason. LOW confidence items entered in HUMAN_REVIEW_REQUIRED.md.

## AC-100-015
coverage-validation.json shows unclassified count = 0 and duplicate count = 0.

## AC-100-016
PUBLIC_BASELINE_MANIFEST.md contains all classified paths with category and reason.

## AC-100-017
DISCLOSURE_FREEZE.md freeze scope is clearly defined with references to classified paths.

## AC-100-018
ASSET_CLASSIFICATION.json is valid JSON, all paths present, no duplicates.

## AC-100-019
ASSET_CLASSIFICATION.md renders correctly, covers all paths from JSON.

## AC-100-020
LICENSE_STATUS.md has every tracked file with a license status entry.

## AC-100-021
HUMAN_REVIEW_REQUIRED.md contains every LOW confidence item exactly once.

## AC-100-022
Red team verdict = PASS or PASS_WITH_LIMITS.

## AC-100-023
Local commit exists with all reports in evidence directory.
