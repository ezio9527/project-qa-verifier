# 03_TEST_REPORT.md - 校验者交付：测试报告与质量审计

> **关联规范版本**: `<spec-version>` (如 `v1.0.0`) | **迭代轮次**: `Iteration <iteration>`  
> **审计执行者**: `project-qa-verifier` | **最终裁决**: `<PASSED | FAILED>`  
> **更新时间**: `<YYYY-MM-DDTHH:mm:ssZ>`

---

## 1. 测试套件执行全景 (Test Execution Summary)

| 测试类型 | 执行命令 | 总用例数 | 通过 (Pass) | 失败 (Fail) | 跳过 (Skip) | 执行耗时 | 单项判定 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **静态检查 & 类型** | `<lint-check-command>` | - | - | - | - | 1.2s | `PASSED` |
| **单元测试 (Unit)** | `<unit-test-command>` | 24 | 24 | 0 | 0 | 3.4s | `PASSED` |
| **集成测试 (Integration)**| `<integration-test-command>` | 8 | 8 | 0 | 0 | 6.2s | `PASSED` |
| **端到端测试 (E2E)** | `<e2e-test-command>` | 4 | 4 | 0 | 0 | 12.5s | `PASSED` |
| **防回归套件 (Regression)**| `<regression-test-command>`| 80 | 80 | 0 | 0 | 8.1s | `PASSED` |
| **对抗/破坏测试 (Chaos)** | `<chaos-test-command>` | 12 | 12 | 0 | 0 | 4.5s | `PASSED` |

---

## 2. 覆盖率与质量门禁审计 (Quality Gates)

* **行覆盖率 (Line Coverage)**: `<actual>%` (门禁目标: `>= <target>%`) $\rightarrow$ **达标 / 未达标**
* **分支覆盖率 (Branch Coverage)**: `<actual>%` (门禁目标: `>= <target>%`) $\rightarrow$ **达标 / 未达标**
* **函数覆盖率 (Function Coverage)**: `<actual>%` (门禁目标: `>= <target>%`) $\rightarrow$ **达标 / 未达标**
* **性能基准指标对比 (若涉及 Perf)**:
  - 现状基准 (Baseline): `P99 = <baseline-p99>ms`
  - 验收门禁 (Target): `P99 <= <target-p99>ms`
  - 实测表现 (Actual): `P99 = <actual-p99>ms` $\rightarrow$ **达标 / 劣化阻断**

---

## 3. 契约一致性静态核验 (Contract Drift Verification)

* **比对基准**: [.workflow/01_SPEC.md](01_SPEC.md) 与 [docs/API_SPEC.md](../docs/API_SPEC.md)
* **审计结果**:
  - [x] 数据实体字段命名与类型 100% 对齐（无拼写漂移）
  - [x] 可选/必填字段约束一致
  - [x] HTTP 状态码与异常响应结构完全一致

---

## 4. 缺陷、异常与复现清单 (Defects & Regressions)

> [!NOTE]
> 若所有测试均通过且门禁达标，本章节填写“无缺陷发现”。

*(若发现失败，按以下规则分类记录并触发状态分流)*:

### 缺陷详情 (Defect #1)
* **现象描述**: `<缺陷现象与报错简述>`
* **根因归因**: `[纯代码实现缺陷 (Implementation) | 架构/契约设计缺陷 (Architectural/Spec)]`
* **关联文件**: `src/<path-to-file>:<line>`
* **自动化复现用例 (Reproduction Test)**: `tests/<repro-test-file>`
* **执行复现命令**: `<command-to-reproduce-test>`
* **真实错误堆栈**:
  ```text
  <贴入详细错误堆栈>
  ```

---

## 5. 最终结论与状态机打卡 (Final Handoff)

* **验收裁决**: `[PASSED (全绿交付) | FAILED_FOR_CODER (退回编码者) | BLOCKED_FOR_ARCHITECT (阻断提报架构师)]`
* **状态机打卡更新**:
  - 更新 `.workflow/state.json` 为：
    ```json
    {
      "current_phase": "COMPLETED",
      "status": "COMPLETED",
      "last_actor": "project-qa-verifier",
      "next_actor": null,
      "blocked": false,
      "rfc_pending": false
    }
    ```
