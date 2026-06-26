# SPEC-000 Design

## Architecture

控制层组件：

```
CLAUDE.md (persistent instructions)
+ .claude/rules/ (6 scoped rules)
+ .claude/skills/ (11 lifecycle skills)
+ .claude/agents/ (7 role-separated agents)
+ .claude/hooks/ (7 enforcement hooks)
+ .claude/settings.json (hook bindings)
+ scripts/ (validation + gate scripts)
+ schemas/ (JSON Schemas for headless output)
+ specs/ (13 spec directories with lifecycle files)
+ .github/workflows/ (5 CI workflows)
```

## Component Design

### CLAUDE.md（根指令，< 200 行）
使命、仓库角色、生命周期状态机、状态权威、硬禁令清单、人工决策门禁、CI 验证原则、sorry 容忍机制、命令清单。

### Rules（6 个）
- `00-spec-driven.md`: 无审批不实现，一次一 Task，不改需求
- `10-state-authority.md`: 磁盘权威，COMPLETE 需 CI + Red Team
- `20-git-safety.md`: 允许 status/diff/log/show/branch/worktree/commit，禁止 force push/rewrite/merge/tag/delete
- `30-formal-proof.md`: 复用密封模块，不弱化定理，blocking path 零 sorry
- `40-runtime-refinement.md`: 证书 checker 独立于 evaluator，ID 不混用
- `50-human-decisions.md`: 8 种人工决策主题，触发后暂停

### Skills（11 个）
覆盖完整生命周期。每个 skill 有 Usage/Actions/Constraints。

### Agents（7 个）
- spec-coordinator (opus): 协调，可调用其他 agent
- requirements-analyst (opus, read-only): 提取需求
- formal-architect (opus, read-only): 设计形式语义
- lean-prover (opus, worktree): 实现 Lean 证明
- runtime-engineer (opus, worktree): 实现 JC 适配
- verifier (opus, read-only): 验证完成
- red-team (opus, read-only): 三层防线审查

### Hooks（7 个）
- PreToolUse×4: 危险命令、文件范围、spec 状态、定理保护
- PostToolUse×1: 证据记录
- SubagentStop×1: 子 agent 输出验证
- Stop×1: 停止验证

### CI Workflows（4 个新增 + 1 个原有）
- ci.yml (原有): pytest
- formal-proof.yml: lake build + sorry gate + axiom audit + hash gate
- runtime-tests.yml: JC 运行时测试
- spec-integrity.yml: spec 完整性 + 依赖 DAG + sorry ledger
- safety-gates.yml: LICENSE 保护 + 定理强度 + sorry gate

### Scripts（7 个新增）
sorry-gate, theorem-hash-gate, theorem-strength-gate, validate-spec-completeness, validate-evidence, check-dependency-dag, validate-sorry-ledger

## Error Semantics

| 触发 | 行为 |
|------|------|
| Hook deny | 返回 permissionDecision="deny"，阻止操作 |
| CI exit 1 | 阻止 PR 合并 |
| Verifier REWORK | 返回实现阶段 |
| Red Team REJECT | 返回实现阶段 |
| HUMAN_DECISION_REQUIRED | 暂停，等人工输入 |

## Migration

- 现有 AGENTS.md 保留不删除
- 现有 ci.yml 保留不修改
- 现有 scripts/ 脚本保留
