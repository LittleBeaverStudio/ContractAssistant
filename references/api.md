# 小河狸合同助手本机 Skill API

基础地址由软件运行端口决定，通常是 `http://127.0.0.1:8870/api/skill`，如端口被占用，软件会自动顺延到后续端口。优先使用 `scripts/contract_assistant_client.py` 自动发现。

所有接口返回 `{ "success": true, "data": ... }` 形态；失败返回 `{ "success": false, "error": ... }`。

## GET /api/skill/info

返回软件名称、版本、模块清单（合同台账、履约节点、业务单、自动生成占位合同、节点发票匹配、往来单位库、内置体检）与可导出的端点列表。

## GET /api/skill/companies

返回公司列表、税号、别名。

## GET /api/skill/summary

参数：`company_id`、`start`、`end`。

返回合同台账一页摘要：台账规模、方向（销售/采购）分布、履约节点进度、覆盖统计。口径与 `/api/skill/contracts` 一致——`voided` 剔除、`terminated` 保留已发生部分。

## GET /api/skill/contracts

参数：`company_id`、`start`、`end`、`direction`、`status`、`keyword`、`page`、`page_size`。

返回合同主档，包含公司、合同编号、名称、方向、类型、状态、主体（甲乙方）、金额、签订日期、到期日、备注等字段。合同附件路径不经此端点暴露。

## GET /api/skill/contract-nodes

参数：`company_id`、`start`、`end`、`page`、`page_size`。

返回履约节点（里程碑/收付款节点），含所属合同、计划日期、实际日期、状态、金额。

## GET /api/skill/contract-links

参数：`company_id`、`start`、`end`。

返回合同间关联（主子合同、补充协议等）。

## GET /api/skill/biz-entries

参数：`company_id`、`start`、`end`、`keyword`。

返回与合同关联的业务单/业务分录（如订单、入库、发票钩稽记录）。

## GET /api/skill/projects

参数：`company_id`、`start`、`end`。

返回项目维度聚合（按项目归并的合同与履约进度）。

## GET /api/skill/coverage

参数：`company_id`、`start`、`end`。

返回合同覆盖/健康度统计：`voided` 已剔除、`terminated` 保留已发生部分；给出覆盖缺口与风险点。

## GET /api/skill/expiring

参数：`company_id`、`start`、`end`、`days`（默认 90）。

返回 `days` 天内到期（含已逾期未翻状态）的合同清单，供催收与续约提醒。

## GET /api/skill/parties

参数：`company_id`、`start`、`end`、`keyword`。

返回往来单位（客户/供应商）库，含识别自动、归并手动的规则结果，可模糊搜索。
