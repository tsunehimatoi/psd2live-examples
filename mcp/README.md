# MCP 外部验收与使用案例

产品服务及内部回归测试由 [主项目](https://github.com/tsunehimatoi/psd2live) 维护。公开契约以主项目的 [MCP 文档](https://github.com/tsunehimatoi/psd2live/blob/master/docs/zh/agent/MCP_AUTHORING.md) 和服务返回的 schema 为准。

## HTTP 发现检查

启动 PSD2Live，在“工具 → MCP…”启用服务，把端点和令牌设置为本地环境变量 `PSD2LIVE_MCP_ENDPOINT` 和 `PSD2LIVE_MCP_TOKEN`，运行：

```sh
python mcp/acceptance/discovery.py
```

脚本验证初始化、工具分页发现以及 `workspace_list_operations` 调用。不修改工程、不保存令牌；默认仅允许连接本机端点。需要服务正在运行，不随本仓库目录 CI 自动执行。

## 场景分享

固定调用场景放在案例的 `scenarios/`，注明所用素材 ID/版本、psd2live commit、前置状态、调用、断言、保存重开与导出检查。写入场景使用独立工作区和输出目录。

Agent 体验案例放在案例的 `prompts/` 和 `skills/`，记录客户端、模型、输入、效果、失败与修正过程。提交前移除令牌、会话 ID 和私人路径。客户端配置直接从应用 MCP 对话框复制，不在本仓库维护另一套操作定义。
