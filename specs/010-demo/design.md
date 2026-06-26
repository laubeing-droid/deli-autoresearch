# SPEC-010 Design

## Demo Function

目标函数：`classify_score(score: int) -> str`

语义：
- `score < 0` → raise ValueError
- `0 <= score < 40` → "FAIL"
- `40 <= score < 70` → "PASS"
- `70 <= score <= 100` → "DISTINCTION"
- `score > 100` → raise ValueError

这是一个纯函数，无副作用，边界清晰，适合测试控制链路。

## File Layout

```
demo/
├── classifier.py          ← classify_score 实现
tests/demo/
├── test_classifier.py     ← 测试用例
```

## Test Strategy

| 测试场景 | 输入 | 期望输出 |
|---------|------|---------|
| 下界异常 | -1 | ValueError |
| FAIL 区 | 20 | "FAIL" |
| PASS 区 | 55 | "PASS" |
| DISTINCTION 区 | 85 | "DISTINCTION" |
| 边界 0 | 0 | "FAIL" |
| 边界 40 | 40 | "PASS" |
| 边界 70 | 70 | "DISTINCTION" |
| 边界 100 | 100 | "DISTINCTION" |
| 上界异常 | 101 | ValueError |

## Intentional Failure Strategy

TASK-010-002 实现有意错误：将 PASS 和 DISTINCTION 的边界设为 60（而非 70），导致 `classify_score(65)` 返回 "DISTINCTION" 而非 "PASS"。测试 `test_boundary_70` 会失败。

## Human Decision Test

TASK-010-009 创建一个人工决策场景：将函数分类为 PATENT_REVIEW，触发 HUMAN_DECISION_REQUIRED。人工确认后清除。
