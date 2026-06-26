# SPEC-010 Requirements

## REQ-010-001
Demo SHALL 包含一个纯函数的最小规格，该函数可在本地测试和 CI 中验证。

## REQ-010-002
Demo SHALL 包含一次故意实现失败，Verifier SHALL 拒绝该失败实现。

## REQ-010-003
Worker SHALL 在新 iteration 中修复失败实现，Verifier SHALL 通过修复版本。

## REQ-010-004
Red Team SHALL 审查最终实现（全自动三层防线）。

## REQ-010-005
Demo SHALL 测试进程中断后从磁盘状态恢复。

## REQ-010-006
Demo SHALL 测试 `HUMAN_DECISION_REQUIRED` 状态的触发和清除。

## REQ-010-007
Demo SHALL 测试 sorry gate（注册一个 sorry，验证 CI 阻止未注册的 sorry）。

## Non-Goals

- 不测试形式化证明链（Lean 4）
- 不测试运行时仓库（juris-calculus）
- 不测试跨仓库操作

## Risks

- Demo 函数过于简单可能无法覆盖控制链的所有边界
- 本地 CI 模拟无法完全替代 GitHub Actions 环境

## Human Decisions

- HREQ-010-01: 无（Demo 不涉及许可证、专利或法律语义决策）
