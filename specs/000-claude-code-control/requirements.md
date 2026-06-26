# SPEC-000 Requirements

## REQ-000-001
仓库 SHALL 定义项目级 `CLAUDE.md`，包含使命、仓库角色、生命周期、状态权威、硬禁令、人工决策门禁、CI 验证、sorry 容忍机制和命令清单。

## REQ-000-002
仓库 SHALL 定义完整 Spec 生命周期 Skills：init, status, requirements, design, tasks, execute, verify, red-team, resume, decide, report。

## REQ-000-003
仓库 SHALL 分离 implementation、verification、red-team Agents，各自职责明确，互不越界。

## REQ-000-004
仓库 SHALL 使用 Hooks 强制执行：危险命令拦截、文件范围限制、spec 状态限制、定理保护、证据记录、子 agent 输出验证、停止验证。

## REQ-000-005
所有写入 Task SHALL 在 worktree 中执行，确保隔离。

## REQ-000-006
所有 headless 执行 SHALL 产生 JSON Schema 约束输出。

## REQ-000-007
磁盘状态 SHALL 是跨会话唯一权威（specs/*/status.json, state/decisions/）。

## REQ-000-008
控制层 SHALL NOT 实现独立通用模型循环。小型脚本可验证 JSON、检查依赖、记录证据，但不得直接调用模型 API 或实现第二套 agent framework。

## REQ-000-009
形式化验证 SHALL 由 GitHub Actions CI 执行（lake build, sorry gate, axiom audit, theorem hash gate）。

## REQ-000-010
Red Team SHALL 全自动执行（三层防线），不依赖人工数学审查。

## REQ-000-011
CI SHALL 包含 sorry gate，blocking path 不允许 sorry。

## Non-Goals

- 不实现完整的 agent orchestration framework（使用 Claude Code 内置机制）
- 不实现自定义模型 API 调用
- 不在 SPEC-000 阶段验证形式化证明链（SPEC-2xx 范围）

## Risks

- Claude Code hooks API 可能变更，需要跟踪官方文档
- GitHub Actions runner 对 Lean 4 build 的内存限制
- worktree 管理需要清理策略避免磁盘积累

## Human Decisions

- HREQ-000-01: 无
