# SPEC-100 Risks

## RISK-100-001: License Ambiguity
Files without clear license markers may require human review, delaying completion.
Mitigation: Flag all ambiguous items for human review rather than making assumptions.

## RISK-100-002: Overclaiming Secrecy
Red team must verify no report declares currently-public content as trade secret.
Mitigation: REQ-100-006 + TASK-100-022 red-team check.

## RISK-100-003: Underclaiming Sensitivity
Patent-sensitive content may be missed in classification.
Mitigation: PATENT_REVIEW items trigger HUMAN_DECISION_REQUIRED automatically.

## RISK-100-004: Inventory Drift
Repository state may change between baseline lock and classification.
Mitigation: TASK-100-001 locks HEAD SHA; all work references that exact commit.
