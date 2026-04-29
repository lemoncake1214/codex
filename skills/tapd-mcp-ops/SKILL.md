---
name: tapd-mcp-ops
description: 使用 TAPD MCP 或 TAPD Open API 进行需求文档管理、研发任务下发、以及按条件批量下载需求文档到项目目录。用户提到 TAPD、需求池、任务拆解、批量导出/下载需求文档、历史需求回溯、按版本区间筛选时触发。
---

# TAPD MCP Ops

## 快速执行流程
1. 确认凭据：优先 `TAPD_ACCESS_TOKEN`。
2. 优先调用 MCP Server；若 MCP 不可用，则退回 `scripts/tapd_bulk_download.py` 直连 Open API。
3. 对“管理需求文档”先拉取需求列表，再按状态/负责人/迭代/版本过滤。
4. 对“下发研发任务”按单需求创建任务并回填关联关系。
5. 对“批量下载需求文档”将结果导出为 `markdown/json` 到项目目录。

## 常用操作模板

### 1) 管理需求文档
- 输入：workspace_id、过滤条件（状态、迭代、负责人、更新时间区间、版本区间）。
- 输出：
  - `docs/tapd/requirements/index.md`
  - `docs/tapd/requirements/<story_id>.md`

### 2) 下发研发任务
- 读取需求详情（标题、描述、验收标准）。
- 拆分任务（开发/联调/测试/发布）。
- 设置负责人、日期、优先级、迭代并回写关联。

### 3) 批量下载特定条件需求文档
```bash
python skills/tapd-mcp-ops/scripts/tapd_bulk_download.py \
  --workspace-id <WALKUP_WORKSPACE_ID> \
  --version-ranges "v1.0-v1.4,v1.8-v2.5" \
  --out-dir ./docs/tapd/walkup-requirements \
  --format markdown
```

> 若 TAPD 项目中的版本字段不是 `version`，用 `--version-fields` 指定候选字段，例如：
> `--version-fields "release,iteration,version"`

## 参考资料
- API 速查：`references/tapd-api-quickref.md`
- 官方开放平台：`https://open.tapd.cn/document/api-doc/API文档/api_reference/`
