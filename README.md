# 小河狸合同助手 Skill

> **许可**：本项目采用**「小河狸工作室非转售许可 1.0」**——
> 个人使用与**企业内部使用免费**（含内部办公、财务与会计处理、内部系统集成）；
> 对外销售、集成进收费产品或服务、托管 / SaaS / 代运营、以及**向第三方交付成果或提供服务，须事先取得书面授权**。
> 许可全文见 [LICENSE.md](./LICENSE.md)。商业授权：https://littlebeaver.top

通过本机运行的「小河狸合同助手」桌面应用读取并分析合同数据。仅调用本机 `localhost` Skill API，不上传合同数据。

- SkillHub（主源）：https://skillhub.cn/skills/littlebeaver/littlebeaver-contract-assistant
- GitHub（回退源）：https://github.com/LittleBeaverStudio/ContractAssistant

对应桌面应用：**小河狸合同助手**（合同台账、履约节点、业务单、往来单位库、内置体检）。

## 能力

- 连接本机小河狸合同助手，自动发现运行端口（默认 `http://127.0.0.1:8870`）。
- 查询公司列表、合同台账一页摘要。
- 按方向（销售/采购）、状态、关键词筛选合同主档。
- 即将到期合同提醒（催收/续约）。
- 往来单位（客户/供应商）与项目聚合。
- 合同覆盖/健康度统计、履约节点进度、合同间关联。

## 使用前提

- 已安装并打开「小河狸合同助手」桌面应用 `v1.2.0` 或更高版本。
- 智能体与桌面应用运行在同一台电脑。
- 数据只走 `127.0.0.1`；Skill 不直接读数据库文件，也不上传任何合同内容。

## 安装

方式一（SkillHub，推荐）：在应用「使用说明」页点击 **Skill安装提示词**，把复制的内容粘给智能体，由智能体按
https://skillhub.cn/install/skillhub.md 完成安装（`@littlebeaver/littlebeaver-contract-assistant`）。

方式二（GitHub 回退，SkillHub 不可用时）：

```bash
git clone https://github.com/LittleBeaverStudio/ContractAssistant.git \
  ~/.workbuddy/skills/littlebeaver-contract-assistant
```

也可以直接把本仓库目录放进智能体的 skills 目录，重启智能体后生效。

## 使用

确保「小河狸合同助手」桌面应用已在本机打开，然后在 Skill 目录下运行：

```bash
python scripts/contract_assistant_client.py info
python scripts/contract_assistant_client.py companies
python scripts/contract_assistant_client.py summary --company-id 1
python scripts/contract_assistant_client.py contracts --company-id 1 --direction 销售 --page-size 100
python scripts/contract_assistant_client.py expiring --company-id 1 --days 90
python scripts/contract_assistant_client.py parties --company-id 1 --keyword 口腔
python scripts/contract_assistant_client.py coverage --company-id 1
```

完整端点字段说明见 [references/api.md](./references/api.md)。

## 目录结构

```
SKILL.md                                技能说明（触发条件、调用规约、写作口径）
agents/openai.yaml                      界面展示名与默认提示词
references/api.md                       本机接口字段说明
references/sample_data.json             示例响应
scripts/contract_assistant_client.py    只读客户端（自动发现端口）
LICENSE.md                              小河狸工作室非转售许可 1.0
```

## 许可

小河狸非转售许可 1.0（企业内部使用免费，转售/对外服务需授权）。详见 `LICENSE.md`。

来源：小河狸工作室 LittleBeaverStudio · https://littlebeaver.top
