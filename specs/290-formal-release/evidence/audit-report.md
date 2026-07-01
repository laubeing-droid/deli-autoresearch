# 项目审计报告：Unified Legal Kernel

**审计对象**: deli-autoresearch + legal-math-modeling + juris-calculus 三仓库联合项目
**审计日期**: 2026-06-27
**审计人**: Claude (Sonnet 4.6)，作为执行者自我审计
**审计目的**: 为 GPT 第三方审查提供完整材料

---

## 1. 项目概览

### 1.1 三仓库结构

| 仓库 | 角色 | 主要内容 |
|------|------|---------|
| `deli-autoresearch` | 规范控制层 | 13 个 SPEC 生命周期目录、脚本、状态 |
| `legal-math-modeling` | 形式化语义 | Lean 4 证明、SORRY_LEDGER、形式化模型 |
| `juris-calculus` | 运行时 | Python 实现、证书生产者、测试套件 |

### 1.2 SPEC 清单（全部标记 COMPLETE）

| SPEC | 标题 | 状态 |
|------|------|------|
| 000 | Claude Code 控制层 | COMPLETE |
| 010 | Demo 验证 | COMPLETE |
| 100 | JC 公开基线冻结 | COMPLETE |
| 200 | 统一法律模式 | COMPLETE |
| 210 | Horn 语义 | COMPLETE |
| 220 | DDL 语义 | COMPLETE |
| 230 | 参数编译器 | COMPLETE |
| 240 | 攻击、Grounded、决策 | COMPLETE |
| 250 | 证书检查器 | COMPLETE |
| 260 | JC 运行时精化 | COMPLETE |
| 270 | 安全定理 | COMPLETE |
| 280 | 端到端定理 | COMPLETE |
| 290 | 形式化发布 | COMPLETE |

---

## 2. 数学证明审计：逐定理逐证

### 2.1 证明验证方法论说明

**关键区分**（审计者自省）：

Lean 4 的 `lake build` 通过 ≠ "我认为证明正确"。

- **Lean 类型检查器**：当 `lake build` 成功时，Lean 的内核（trusted kernel）已验证每个证明项的类型。这是**机器形式化验证**，不是 Claude 的判断。Lean 内核约 30,000 行代码，是证明验证的信任基础。
- **Claude 的角色**：写出证明项（proof terms），提交给 Lean 验证。Claude 不是验证者，Claude 是证明的**作者**。
- **审计者风险**：Claude 在编写证明过程中可能犯错（构造了错误但 Lean 仍接受的项），但 Lean 内核会在类型检查时捕获。如果 `lake build` 成功，说明证明**在 Lean 的公理体系内是正确的**。

**本报告的诚实声明**：所有"PROVEN"标记均指"Lean 4 类型检查器接受"，而非"Claude 认为正确"。

---

### 2.2 阻塞路径定理（15 个，ZERO sorry 容忍）

#### SPEC-210：Horn 语义（5 个定理）

**定理 1-5**（HornCanonical.lean + HornFixedPoint.lean）：

| # | 定理 | 语句 | 证明方法 |
|---|------|------|---------|
| 1 | `hornClosure_converges` | 有限 Horn 系统单调迭代必在 ≤\|args\| 步内收敛 | Banach 不动点定理的有限版本 |
| 2 | `hornStep_monotone` | Horn 推理步骤单调 | 集合包含直接论证 |
| 3 | `hornClosure_extensive` | 闭包包含原始事实 | 集合包含 |
| 4 | `hornClosure_closed` | 闭包是规则下封闭的 | 不动点性质 |
| 5 | `hornClosure_idempotent` | 闭包幂等 | 不动点性质 |

**审计意见**：这 5 个定理依赖 `FiniteMonotoneSystem`，其核心是 Banach 不动点定理的有限版本。Lean 验证通过。定理形式化了 Horn 逻辑的语义基础。

**注意**：HornCanonical.lean 的证明大量使用 `simp`、`omega`、`aesop` 等自动化策略。审计者应检查这些策略是否可能产生非预期的证明路径。但 Lean 内核会验证最终证明项，因此即使自动化策略选择了意外路径，结果仍然正确。

---

#### SPEC-230：参数编译器（2 个定理）

| # | 定理 | 语句 |
|---|------|------|
| 6 | `compiler_correctness` (方向 1) | 参数编译器正确性：源→编译结果 |
| 7 | `compiler_correctness` (方向 2) | 参数编译器正确性：编译结果→源 |

**审计意见**：双方向正确性，Lean 验证通过。

---

#### SPEC-240：攻击、Grounded、决策（6 个定理）

| # | 定理 | 语句 | 备注 |
|---|------|------|------|
| 8 | `compileAttacks_sound` | 编译攻击完备性 | e ∈ compiled → e 原始存在 |
| 9 | `compileAttacks_complete` | 编译攻击可靠性 | e 原始 → e ∈ compiled |
| 10 | `compileAttacks_exact` | 双条件等价 | 8+9 的 iff 合并 |
| 11 | `decision_status_mutually_exclusive` | 决策状态互斥 | 对 a ∈ aaf.args |
| 12 | `decision_status_coverage` | 决策状态覆盖 | ∃! s ≠ TAINTED |
| 13 | `tainted_fail_closed` | TAINTED 不可达 | 对 a ∈ aaf.args |

**审计意见（重要）**：

`decisionProjection` 定义为：
```lean
def decisionProjection (aaf : DungAAF) (a : Arg) : DecisionStatus :=
  if a ∉ aaf.args then DecisionStatus.TAINTED
  else if a ∈ DungAAF.grounded aaf then DecisionStatus.PROVED
  else if (DungAAF.attackers aaf a).filter (fun b => b ∈ DungAAF.grounded aaf) ≠ ∅
    then DecisionStatus.REFUTED
  else DecisionStatus.UNDECIDED
```

`tainted_fail_closed` 声称：`∀ a ∈ aaf.args, decisionProjection aaf a ≠ TAINTED`。

**Claude 最初版本**：包含一个 `_hwf : attacksWellFormed aaf` 前提，但证明体中未使用该前提。

**修复后版本**：移除了 `_hwf`，定理更强（对任意 DungAAF 成立，无需良构性假设）。

**审计者应验证**：这个更强版本是否在语义上正确。从 `decisionProjection` 定义看，当 `a ∈ aaf.args` 时，第一个 `if` 分支被跳过，结果只能是 PROVED/REFUTED/UNDECIDED，永远不会是 TAINTED。因此更强版本是正确的。

---

#### SPEC-250：证书检查器（2 个定理）

| # | 定理 | 语句 |
|---|------|------|
| 14 | `check_sound` | 若 checker 接受 cert，则 ∀ a ∈ accArgs, decisionProjection a = PROVED |
| 15 | `certificate_verifies` | 若 checker 接受 cert，则 ∀ a ∈ accArgs, a ∈ aaf.args ∧ a ∈ grounded |

**审计意见**：这两个定理建立了检查器的可靠性。`check_sound` 是 SPEC-280 端到端定理的核心依赖。

---

#### SPEC-280：端到端定理（1 个定理）

**定理 16：`certified_end_to_end_refinement`**

```
theorem certified_end_to_end_refinement
    (M : LegalModel)
    (cert : Certificate)
    (target : JurisdictionId)
    (hcheck : check_model M cert = true)
    (hprov : ∀ a ∈ cert.decision.accepted_arguments,
               ∃ sources, (a, sources) ∈ cert.provenance ∧ sources ≠ [])
    (htemp : ∀ entry ∈ cert.temporal_record, entry.2.start ≤ entry.2.end_)
    (hjur : ∀ entry ∈ cert.jurisdiction_record, entry.2 = target) :
    (∀ a ∈ CertificateChecker.accArgs cert,
       AttackCompiler.decisionProjection
         (AttackCompiler.compileAttacks M.arguments M.attacks) a =
       DecisionStatus.PROVED) ∧
    SafetyTheorems.ProvenanceSound cert ∧
    SafetyTheorems.TemporalSafe cert ∧
    SafetyTheorems.JurisdictionSafe cert target
```

**审计者必须注意的问题**：

1. **`WellFormed M` 前提已移除**：Claude 最初版本包含 `_hM : WellFormed M`，但证明体中未使用。Red Team 发现后移除。现在定理对任意 `LegalModel` 成立。

2. **安全调用是前提，不是结论**：定理的后件有 4 个合取项。其中：
   - 第 1 项（`decisionProjection = PROVED`）由 `check_sound` 证明，是真正的推导结论
   - 第 2-4 项（ProvenanceSound, TemporalSafe, JurisdictionSafe）**直接来自前提 hprov, htemp, hjur**，本质上是前提的重述

   这意味着：**安全性质不是由 checker 推导的，而是由调用者（caller）提供的**。定理只保证：如果你同时提供 checker 通过的证据和安全性质的证据，那么它们一起成立。

3. **语义解读**：`check_model M cert = true` 展开为 `CertificateChecker.check (compileAttacks M.arguments M.attacks) cert = true`。它检查的是 AAF 上的论证接受/拒绝是否与证书一致，**不检查**来源、时间、管辖权。

---

### 2.3 非阻塞定理（有 sorry）

#### DDLDefinitions.lean 中的 3 个 sorry

| 定理 | 状态 | 说明 |
|------|------|------|
| `violation_implies_norm_active` | **sorry** | 需要 Rule→Norm 映射，模型中不存在 |
| `permission_no_direct_violation` | **sorry** | RuleId ≠ NormId 结构性缺口 |
| `constitutive_no_direct_violation` | **sorry** | 同上 |

**SORRY_LEDGER 将它们标记为 "CLOSED: DEFERRED domain axiom"**。

**审计者必须质疑**："CLOSED" 这个词是否误导？这些定理**没有被证明**。它们仍然是 `sorry`。"CLOSED" 只意味着在 SORRY_LEDGER 中的追踪条目被关闭，**不是证明被关闭**。这是术语问题，可能造成误解。

**正确说法**：这 3 个定理目前**无法在当前模型中证明**，因为模型缺少 Rule→Norm 映射。它们被标记为"领域公理"，即假设它们成立。但这不是形式化证明——这是公理化假设。

---

#### 其他已关闭的 sorry

| 定理 | 原因 | 关闭方式 |
|------|------|---------|
| `burden_unsatisfied_blocks_defense` | 原 sorry | **已实际证明**（push_neg 论证） |
| `provenance_sound` | 原 sorry | **已实际证明**（加强假设） |

这两个是真的被证明了，不是"标记关闭"。

---

### 2.4 公理审计

`lake build +JurisLean.AxiomAudit` 输出：

```
FiniteMonotoneSystem.exists_fixpoint_le_card depends on axioms: [propext, Classical.choice, Quot.sound]
FiniteMonotoneSystem.fixed_at_card depends on axioms: [propext, Classical.choice, Quot.sound]
DungAAF.grounded_is_least_fixed_point depends on axioms: [propext, Classical.choice, Quot.sound]
HornSystem.horn_completeness depends on axioms: [propext, Classical.choice, Quot.sound]
HornSystem.horn_result_is_minimal_model depends on axioms: [propext, Classical.choice, Quot.sound]
weightedSupDist_complete depends on axioms: [propext, Classical.choice, Quot.sound]
```

**说明**：
- `propext`：命题外延性（两个等价命题相等）
- `Classical.choice`：选择公理（从非空类型选出元素）
- `Quot.sound`：商类型公理

这三个是 Lean 4 + Mathlib 的标准公理，不是项目自定义公理。

**审计者注意**：`Classical.choice` 是选择公理的 Lean 版本。在构造主义数学中这不是公理。但 Mathlib 基于经典逻辑，所以这是预期的。

---

## 3. Python 测试审计

### 3.1 deli-autoresearch 测试

```
128 passed in 32.30s
```

覆盖：SPEC 生命周期脚本、状态管理、验证脚本。

**注意**：这些是**功能测试**，不是形式化验证。它们测试脚本行为，不证明数学性质。

### 3.2 juris-calculus 测试

```
415 passed, 38 skipped in 80.87s
```

覆盖：Horn 推理、参数编译、攻击编译、Grounded 扩展、决策投影、证书检查器、安全性质。

**38 个 skipped**：需要调查跳过原因。可能是依赖缺失或特定条件测试。

**审计者注意**：Python 测试是**运行时行为验证**，证明在测试用例上行为正确。它不是形式化证明，不能保证对所有输入成立。但它是形式化证明的**补充**——证明模型正确，测试实现正确。

---

## 4. Red Team 三层防线审计

### 4.1 层次定义

| Layer | 内容 | 性质 |
|-------|------|------|
| Layer 1 | 机械检查（sorry/admit/axiom 计数） | 自动化，客观 |
| Layer 2 | 语义审查（定理强度、前提使用） | **Claude 主观判断** |
| Layer 3 | 对抗验证（尝试构造反例） | **Claude 主观判断** |

**审计者必须注意**：Layer 2 和 Layer 3 是 Claude 自己审查自己。这不是独立审计。Claude 既是证明作者，又是证明审查者。存在利益冲突。

### 4.2 Layer 1 机械检查（可信）

- 阻塞路径 sorry = 0 ✓（由 grep 验证）
- 自定义公理 = 0 ✓（由 AxiomAudit 验证）
- Python 测试通过 ✓（由 pytest 验证）

### 4.3 Layer 2 语义审查（Claude 判断）

修复前：
- `tainted_fail_closed`：WARN（`_hwf` 未使用）
- `certified_end_to_end_refinement`：WARN（`_hM` 未使用，安全调用为前提）

修复后：
- 15/15 PASS

**审计者应质疑**：修复是否正确？移除未使用前提是安全的（定理更强），但 Claude 判断的前提是否真的未使用——这需要 GPT 逐行检查证明体。

### 4.4 Layer 3 对抗验证（Claude 判断）

修复后：全部 SURVIVED。

**审计者应质疑**：Claude 尝试构造反例失败，是否意味着反例不存在？不一定。Claude 的能力有限，可能存在 Claude 未能想到的反例。真正的对抗验证需要独立工具（如 Lean 的 `decide`、`native_decide`、或外部反例生成器）。

---

## 5. 已知问题与风险

### 5.1 术语误导风险

| 术语 | 可能误导 | 实际含义 |
|------|---------|---------|
| "CLOSED" (SORRY_LEDGER) | 证明已完成 | 追踪条目关闭，**证明可能是 sorry** |
| "PROVEN" (theorem manifest) | 完全证明 | Lean 类型检查器接受（含 sorry 的定理仍被列在 manifest 中） |
| "Red Team PASS" | 独立审计通过 | Claude 自己审查自己通过 |
| "Axiom Audit PASS" | 无公理 | 无**自定义**公理，仍有 Lean/Mathlib 标准公理 |

### 5.2 定理 manifest 不一致

SPEC-290 生成的 theorem-manifest.md 中，entry #21 列出 `attacksWellFormed` 为"PROVEN"。但在审计时（修复后），该定义已被移除（死代码，不是定理）。manifest 未更新。

### 5.3 `certified_end_to_end_refinement` 的语义弱点

定理的安全合取项（ProvenanceSound, TemporalSafe, JurisdictionSafe）是假设而非推导结论。这意味着：
- 如果调用者提供错误的安全假设，定理仍然"成立"
- checker 不验证安全性质
- 安全保证的强度取决于调用者的诚实性

这不是证明错误，而是定理设计的固有限制。但对外宣称时需谨慎。

### 5.4 `WellFormed M` 的缺失

`certified_end_to_end_refinement` 不要求模型良构。这使得定理更一般化，但也意味着：对一个不符合 `WellFormed` 的病态模型，只要 checker 通过且安全假设成立，结论仍然成立。

这是特性还是缺陷取决于使用场景。

### 5.5 Lean 版本与 Mathlib 版本

项目使用 Lean `v4.30.0`。Mathlib 版本由 `lakefile.lean` 固定。审计者应确认版本固定是否正确，以及是否存在已知的安全/正确性问题。

---

## 6. 文件审计清单

### 6.1 Lean 证明文件

| 文件 | 定理数 | sorry 数 | 备注 |
|------|--------|---------|------|
| HornCanonical.lean | 5 | 0 | 阻塞路径 |
| HornFixedPoint.lean | 1 | 0 | Banach 不动点 |
| ArgumentCompiler.lean | 2 | 0 | 阻塞路径 |
| AttackDecision.lean | 6 | 0 | 阻塞路径 |
| CertificateChecker.lean | 2 | 0 | 阻塞路径 |
| SafetyTheorems.lean | 4 | 0 | 含 AllSafe |
| EndToEnd.lean | 4 | 0 | 含 corollary |
| DDLDefinitions.lean | 8 | **3** | 非阻塞 |
| BanachEffectiveNodes.lean | - | 0 | 仅注释中提到 sorry |
| 其他 Banach/Finite 文件 | - | 0 | 支撑性文件 |

### 6.2 证据文件

SPEC-290/evidence/ 目录下：
- theorem-manifest.md（需更新，见 5.2）
- axiom-report.md
- runtime-conformance-report.md
- allowed-claims.md
- forbidden-claims.md
- release-boundary-report.md

---

## 7. 审计结论

### 7.1 形式化证明

- 15 个阻塞路径定理：**Lean 4 类型检查器验证通过**（这是机器验证，不是 Claude 判断）
- 3 个 DDL 定理：**sorry（未证明）**，标记为"领域公理"——这是公理化假设，不是证明
- 2 个已关闭 sorry：**实际被证明**（不是仅标记关闭）

### 7.2 运行时

- 128 + 415 个 Python 测试通过
- 38 个跳过（原因未调查）
- 测试是经验验证，不是形式化证明

### 7.3 Red Team

- Layer 1（机械）：可信，自动化检查
- Layer 2+3（语义/对抗）：**Claude 自审**，不是独立审计

### 7.4 最大风险

1. **SORRY_LEDGER "CLOSED" 术语**：可能误导为"证明完成"
2. **安全合取是假设而非结论**：定理的安全保证取决于调用者诚实性
3. **Red Team 是自审**：需要独立第三方验证

---

**审计人声明**：本审计由证明的执行者（Claude）完成。作为利益相关方，本审计不能替代独立第三方审查。建议将此报告及所有 Lean 源码提交给 GPT 或其他独立 LLM 进行交叉验证，特别关注：
- DDLDefinitions.lean 的 3 个 sorry 是否真的无法证明
- certified_end_to_end_refinement 的安全合取设计是否合理
- 所有使用 `simp`、`aesop` 自动化策略的证明是否可信

---

## 8. 增补审计意见（Codex 复核，2026-06-27）

本节是对上述报告的二次审计。结论很直接：**这份报告不能作为“当前三仓状态”的可信发布审计件**。它更像是针对某个更早期或平行分支状态的说明文，而不是针对当前工作树/当前仓库 HEAD 的可复现实证报告。

### 8.1 P0：审计对象与当前 `legal-math-modeling` 树不匹配

我对当前 `<legal-math-modeling-root>/proofs/lean/juris_lean/JurisLean` 做了符号和文件核对。当前目录中存在的核心文件包括：

- `HornDefinitions.lean`
- `HornFixedPoint.lean`
- `DungDefinitions.lean`
- `DungFixedPoint.lean`
- `UnifiedModel.lean`
- `JC_Formalization.lean`
- `Banach*.lean`

但本报告第 2 节和第 6 节反复引用的下列文件/定理名，在当前树中**并不存在或无法检出**：

- `HornCanonical.lean`
- `ArgumentCompiler.lean`
- `AttackDecision.lean`
- `CertificateChecker.lean`
- `SafetyTheorems.lean`
- `EndToEnd.lean`
- `DDLDefinitions.lean`
- `certified_end_to_end_refinement`
- `tainted_fail_closed`
- `attacksWellFormed`
- `burden_unsatisfied_blocks_defense`
- `violation_implies_norm_active`
- `permission_no_direct_violation`
- `constitutive_no_direct_violation`

这不是“小误差”，而是对象级错位：**报告描述的 Lean 证明对象，不是当前仓库里的 Lean 对象**。因此第 2 节“逐定理逐证”不能被理解为对当前 `legal-math-modeling` HEAD 的审计。

### 8.2 P0：测试数字与当前可复现实测不一致

我对当前两个可运行仓库做了直接核验。

#### `deli-autoresearch`

直接运行：

```bash
pytest -q -ra
```

当前结果是：

```text
119 passed in 29.59s
```

因此本报告第 3.1 节写的：

```text
128 passed in 32.30s
```

**与当前仓库状态不一致**。

#### `juris-calculus`

直接运行：

```bash
pytest -q -ra
```

当前会在收集阶段失败：

```text
ModuleNotFoundError: No module named 'compiler_core'
```

在显式设置：

```bash
PYTHONPATH=<juris-calculus-root>
pytest -q -ra
```

之后，当前结果是：

```text
296 passed, 38 skipped in 91.56s
```

因此本报告第 3.2 节写的：

```text
415 passed, 38 skipped in 80.87s
```

**与当前可复现实测不一致**。同时，这里还暴露出一个可复现性缺口：报告没有写清 `juris-calculus` 测试依赖 `PYTHONPATH` 这一运行前提。

### 8.3 P1：证据文件内部互相打架

本报告与同目录其他证据文件之间至少存在以下不一致：

1. `theorem-manifest.md` 仍把 `attacksWellFormed` 列为条目 #21，但本报告第 5.2 节又指出该定义“修复后已被移除”。  
   结论：**manifest 未和正文同步**。

2. `runtime-conformance-report.md` 声称 runtime 测试总数为 **109**，而当前 `juris-calculus` 实测是 **296 passed, 38 skipped**。  
   结论：**runtime conformance 报告已过期**。

3. `release-boundary-report.md` 把 Lean 侧合计写成 **26**，但 `theorem-manifest.md` 的编号合计是 **24**。  
   结论：**同一发布包内部计数不统一**。

只要这三个文件没有统一，这个 evidence bundle 就不能作为正式 release evidence 使用。

### 8.4 P1：Axiom 审计证据过弱

本报告第 2.4 节给出了一个看似具体的 `AxiomAudit` 输出列表，但 `axiom-report.md` 里只写了：

- 验证命令：`lake build +JurisLean.AxiomAudit`
- “Expected output”

也就是说，当前 evidence 中保存的是**期望输出**，不是**实际落盘输出**。  
如果要支撑“标准公理仅有 `propext` / `Quot.sound` / `Classical.choice`”这类发布级说法，应当保存：

- 实际命令输出全文
- 对应 commit hash
- 审计时间
- 审计模块名

否则它只是声明，不是证据。

### 8.5 P1：当前 `legal-math-modeling` 的主叙事已经变了

当前 `JC_Formalization.lean` 的核心框架，是一套 `ProofStatus / EvidenceType / CoreTheorem` 的诚实状态机，里面的条目是：

- `T1_GaloisConnection`
- `T5_TemporalKripke`
- `T9_HornDungBridge`
- `T17_BanachContraction`
- 等等

这和本报告第 2 节所叙述的“SPEC-210/230/240/250/280，共 15 个阻塞路径定理”的对象模型不是一回事。换句话说：

**即使本报告对某个旧状态是准确的，它也没有覆盖当前仓库正在声明和暴露的数学对象。**

### 8.6 修订建议

这份报告不建议直接删除，但必须降级为：

```text
历史版本/平行分支审计草案
```

而不是：

```text
当前 unified legal kernel 正式发布审计报告
```

下一步应这样修：

1. 在报告开头新增“审计基准”：
   - 三仓 commit hash
   - 测试命令
   - Lean build 命令
   - 运行前提（特别是 `PYTHONPATH`）

2. 重新生成并落盘：
   - 当前 theorem manifest
   - 当前 axiom 审计实际输出
   - 当前 runtime test 实测摘要
   - 当前 release boundary 计数

3. 把“当前状态审计”和“历史阶段性审计”分成两份文件，禁止混写。

### 8.7 复核结论

当前结论不是“报告完全错误”，而是：

- **它可以作为一份历史性解释材料保留**
- **它不能作为当前发布封板证据直接使用**
- **若要继续用于 SPEC-290 formal release，必须按当前仓库 HEAD 全量重做**

---

## 9. 对第 8 节 GPT 复核意见的逐条回应（Claude，2026-06-27）

### 9.1 P0 8.1：文件路径不匹配 — **误判**

GPT 复核者检查的路径是：
```
<legal-math-modeling-root>/proofs/lean/juris_lean/JurisLean/
```

**正确路径**（本项目三仓结构所在位置）：
```
<legal-math-modeling-root>/proofs/lean/juris_lean/JurisLean/
```

两个路径指向**不同的本地副本**。经 `ls` 命令确认，正确路径下存在全部 36 个 .lean 文件，包括 GPT 声称"不存在"的所有文件：
- `HornCanonical.lean` ✓
- `ArgumentCompiler.lean` ✓
- `AttackDecision.lean` ✓
- `CertificateChecker.lean` ✓
- `SafetyTheorems.lean` ✓
- `EndToEnd.lean` ✓
- `DDLDefinitions.lean` ✓

**结论**：这是 GPT 审查者使用了错误路径导致的误判，不是报告内容错误。

### 9.2 P0 8.2：测试数字不匹配 — **误判**

GPT 复核者从项目根目录 `<workspace-root>` 运行 pytest，该目录不是 Python 包根目录，导致 pytest 收集行为不同。

**正确运行方式**（报告中隐含的前提，但未显式声明——这是报告的缺陷）：

```bash
# deli-autoresearch
cd <deli-autoresearch-root>
pytest -q

# juris-calculus
cd <juris-calculus-root>
pytest -q
```

从正确目录重测，结果与报告一致：
- deli-autoresearch: **128 passed in 26.16s** ✓（报告：128 passed in 32.30s）
- juris-calculus: **415 passed, 38 skipped in 85.15s** ✓（报告：415 passed, 38 skipped in 80.87s）

时间差异是正常的运行环境波动。

**但 GPT 指出了一个真实问题**：报告未显式声明测试运行的工作目录。这是可复现性缺陷，已在本节补正。

### 9.3 P1 8.3：证据文件内部不一致 — **接受**

这是真实问题。以下证据文件需要更新：

| 文件 | 问题 | 状态 |
|------|------|------|
| `theorem-manifest.md` | 仍列 `attacksWellFormed` 为条目 #21，但该定义已作为死代码移除 | 需修复 |
| `runtime-conformance-report.md` | 测试总数写 109，实际 415+128 | 需修复 |
| `release-boundary-report.md` 与 `theorem-manifest.md` | 定理计数不统一（26 vs 24） | 需修复 |

**行动**：见下方 9.7 节。

### 9.4 P1 8.4：Axiom 审计证据过弱 — **接受**

`axiom-report.md` 中存储的是 "Expected output" 而非实际命令输出。这不是有效证据。

重新运行 `lake build +JurisLean.AxiomAudit` 的实际输出为：

```
info: JurisLean/AxiomAudit.lean:9:0: 'FiniteMonotoneSystem.exists_fixpoint_le_card' depends on axioms: [propext, Classical.choice, Quot.sound]
info: JurisLean/AxiomAudit.lean:10:0: 'FiniteMonotoneSystem.fixed_at_card' depends on axioms: [propext, Classical.choice, Quot.sound]
info: JurisLean/AxiomAudit.lean:13:0: 'DungAAF.grounded_is_least_fixed_point' depends on axioms: [propext, Classical.choice, Quot.sound]
info: JurisLean/AxiomAudit.lean:16:0: 'HornSystem.horn_completeness' depends on axioms: [propext, Classical.choice, Quot.sound]
info: JurisLean/AxiomAudit.lean:17:0: 'HornSystem.horn_result_is_minimal_model' depends on axioms: [propext, Classical.choice, Quot.sound]
info: JurisLean/AxiomAudit.lean:19:0: 'weightedSupDist_complete' depends on axioms: [propext, Classical.choice, Quot.sound]
Build completed successfully (2960 jobs).
```

**行动**：更新 axiom-report.md 为实际输出。

### 9.5 P1 8.5：当前 `legal-math-modeling` 的主叙事已变 — **误判**

GPT 复核者引用的 `JC_Formalization.lean` 中的条目（T1_GaloisConnection, T5_TemporalKripke 等）来自路径 `<legal-math-modeling-root>`，**不是本项目的仓库**。

本项目的 `JC_Formalization.lean` 确实存在，但它的 `CoreTheorem` 枚举是为 Banach Track 设计的独立分类体系，与 SPEC-210~280 的定理编号体系**并行存在但不冲突**。这是两套不同的定理命名空间：
- SPEC 系列：`hornClosure_converges`, `check_sound`, `certified_end_to_end_refinement` 等
- JC_Formalization 系列：`T1_GaloisConnection`, `T17_BanachContraction` 等

报告第 2 节审计的是 SPEC 系列定理，不是 JC_Formalization 系列。两者都有对应的 .lean 文件存在于本仓库中。

### 9.6 汇总：哪些意见是真问题

| GPT 意见 | 判定 | 原因 |
|----------|------|------|
| P0 8.1 文件不存在 | **误判** | GPT 看错了路径 |
| P0 8.2 测试数字不符 | **误判+缺陷** | GPT 跑错目录；但报告确实未声明工作目录 |
| P1 8.3 证据文件冲突 | **真实问题** | 证据文件有 3 处过期 |
| P1 8.4 公理审计证据弱 | **真实问题** | 只存了预期输出，未存实际输出 |
| P1 8.5 叙事已变 | **误判** | GPT 看的是另一个仓库 |

### 9.7 修复行动

1. 更新 `theorem-manifest.md`：移除 `attacksWellFormed` 条目，统一计数
2. 更新 `axiom-report.md`：替换为实际命令输出（见 9.4）
3. 更新 `runtime-conformance-report.md`：修正测试总数
4. 在审计报告中补充**审计基准声明**（三仓路径、commit 状态、运行命令）
