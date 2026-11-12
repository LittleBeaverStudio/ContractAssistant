---
name: littlebeaver-contract-assistant
displayName: 小河狸合同助手
display_name: 小河狸合同助手
display_name_en: LittleBeaver Contract Assistant
description: 读取并分析本机小河狸合同助手中的数据。当用户要求连接小河狸合同助手、查询合同台账或履约节点、统计合同覆盖与即将到期、分析往来单位或项目、汇总合同金额时使用。通过应用的 localhost Skill API 在本机处理数据。
description_zh: 读取并分析本机小河狸合同助手中的数据：合同台账与履约节点、即将到期提醒、合同覆盖统计、往来单位与项目汇总。仅通过 localhost 接口在本机处理数据，不上传合同数据。
description_en: Read and analyze local LittleBeaver Contract Assistant data. Query contract ledger, performance nodes, expiring alerts, coverage, parties and projects. Local localhost API only.
version: 1.0.1
author: 小河狸工作室
license: 小河狸非转售许可 1.0（企业内部使用免费，转售收费需授权）
slug: littlebeaver-contract-assistant
summary: 读取并分析本机小河狸合同助手中的数据：合同台账、履约节点、即将到期提醒、合同覆盖统计、往来单位与项目汇总。仅通过 localhost 接口在本机处理数据。
tags: [小河狸, 合同管理, localhost, 只读]
metadata:
  author: 小河狸工作室
  version: 1.0.0
examples_zh:
  - 连接小河狸合同助手，汇总我当前公司的合同台账
  - 列出 90 天内即将到期的合同
  - 按往来单位统计合同金额与覆盖情况
examples_en:
  - Connect LittleBeaver Contract Assistant and summarize my contract ledger
  - List contracts expiring within 90 days
  - Aggregate contract amounts and coverage by counterparty
---

# 小河狸合同助手 Skill

许可证：小河狸非转售许可 1.0（完整条款见 `LICENSE.md`）。

通过用户本机运行的「小河狸合同助手」桌面应用读取合同数据。确保应用与智能体运行在同一台电脑上。仅调用本机 API，不通过本 Skill 上传合同数据。

默认使用简体中文回答。金额默认按人民币格式显示并保留两位小数；使用「销售合同」「采购合同」「履约节点」「到期」「覆盖」「往来单位」等合同管理常用术语。除非用户明确要求，否则不要把台账计算结果表述为法务或审计结论。

## 连接应用

1. 优先使用 `scripts/contract_assistant_client.py`。
2. 用户提供地址时，传入 `--base-url http://127.0.0.1:<port>`。
3. 用户未提供地址时，扫描 `http://127.0.0.1:8870` 附近端口，并自动发现应用（优先用 `/api/metadata` 的 `app` 字段，缺失时退回 `/api/skill/info` 确认 `app_name=小河狸合同助手`，以区分同系列其他助手）。
4. **检测不到本机应用时**，客户端会自动回退到清晰标注的**示例数据**（演示/离线模式），保证命令始终返回结构完整的 JSON，不会崩溃；此时 stderr 会提示「未检测到本机小河狸合同助手，以下为示例数据」，请用户打开软件后重试以获取真实数据。
5. 也可显式传入 `--demo` 强制使用示例数据，或传入 `--strict` 在检测失败时直接报错（用于自动化环境）。

可选环境变量：

- `CONTRACT_ASSISTANT_BASE_URL`：指定应用地址，例如 `http://127.0.0.1:8870`。
- `CONTRACT_ASSISTANT_PORTS`：指定逗号分隔的端口或端口范围，例如 `8870-8890,9000`。

## 常用查询

在 Skill 目录中运行：

```bash
python scripts/contract_assistant_client.py info
python scripts/contract_assistant_client.py companies
python scripts/contract_assistant_client.py summary --company-id 1
python scripts/contract_assistant_client.py contracts --company-id 1 --direction 销售 --page-size 100
python scripts/contract_assistant_client.py expiring --company-id 1 --days 90
python scripts/contract_assistant_client.py parties --company-id 1 --keyword 口腔
python scripts/contract_assistant_client.py coverage --company-id 1
python scripts/contract_assistant_client.py contract-nodes --company-id 1
python scripts/contract_assistant_client.py projects --company-id 1
python scripts/contract_assistant_client.py biz-entries --company-id 1
python scripts/contract_assistant_client.py contract-links --company-id 1
```

处理自然语言分析请求时，先获取满足问题所需的最小数据集：

- 选择公司：运行 `companies`。
- 一页摘要（台账规模、方向、节点、覆盖）：运行 `summary`。
- 核查具体合同：运行 `contracts`，按需设置 `company_id`、`direction`（销售/采购）、`status`、`keyword`、`page`、`page_size`。
- 即将到期提醒（催收/续约）：运行 `expiring`，设置 `days`（默认 90）。
- 往来单位（客户/供应商）分析：运行 `parties`。
- 合同覆盖/健康度：运行 `coverage`。
- 履约节点进度：运行 `contract-nodes`。
- 项目与业务单：运行 `projects` / `biz-entries`。
- 合同间关联（主子、补充协议）：运行 `contract-links`。

## API 规则

使用以下本机 Skill API：

- `/api/skill/health`
- `/api/skill/info`
- `/api/skill/companies`
- `/api/skill/summary`
- `/api/skill/contracts`
- `/api/skill/contract-nodes`
- `/api/skill/contract-links`
- `/api/skill/biz-entries`
- `/api/skill/projects`
- `/api/skill/coverage`
- `/api/skill/expiring`
- `/api/skill/parties`

各接口支持的筛选参数：

- `company_id`：可重复传入。
- `start` 和 `end`：使用 `yyyy-mm-dd` 格式。
- `direction`：使用 `销售` 或 `采购`。
- `status`：合同状态（如 `active`、`terminated`、`voided` 等，以应用实际枚举为准）。
- `keyword`：对合同与往来单位执行模糊搜索。
- `days`：`expiring` 接口控制到期窗口天数。
- `page` 和 `page_size`：控制列表分页。

`coverage` 接口已剔除 `voided`（作废）合同；`terminated`（终止）保留已发生部分。合同附件路径不经 skill 端点暴露（仅本机一键打开），本 Skill 不读取本机绝对路径。

需要完整字段说明时，读取 `references/api.md`。

## 分析要求

回答合同问题时，明确说明所选公司、日期范围以及是否排除作废合同。

分析「哪些合同即将到期」「某往来单位合同覆盖是否充分」等问题时，先读取 `summary` 或 `coverage`；需要逐条核对时，再读取 `contracts` / `expiring` 并按状态、方向或往来单位聚合。
