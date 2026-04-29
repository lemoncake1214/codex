# TAPD API 快速参考

## 鉴权
- MCP 推荐：`TAPD_ACCESS_TOKEN`（个人访问令牌）。

## 需求（Story）
- 查询需求列表：`GET https://api.tapd.cn/stories`
- 获取单个需求：`GET https://api.tapd.cn/stories/{id}`
- 创建需求：`POST https://api.tapd.cn/stories`
- 修改需求：`PUT https://api.tapd.cn/stories`

## 任务（Task）
- 查询任务：`GET https://api.tapd.cn/tasks`
- 创建任务：`POST https://api.tapd.cn/tasks`
- 修改任务：`PUT https://api.tapd.cn/tasks`

## 需求回溯（walkup 示例）
1. 先确认 walkup 的 `workspace_id`。
2. 拉取历史需求并按版本区间筛选：`v1.0-v1.4,v1.8-v2.5`。
3. 导出到项目目录用于归档/分析。

## 脚本参数约定
- `--version-ranges`：逗号分隔区间，例如 `v1.0-v1.4,v1.8-v2.5`
- `--version-fields`：按顺序尝试读取版本值（默认 `version,release,iteration`）
