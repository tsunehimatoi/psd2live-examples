# 制作流程

[绯灯祈](../README.md) · [雾岛澪](../../kirishima-mio/README.md)

grok bot 组织制作，GPT Image 通过 Codex exec 或 Web 生成部件并补全遮挡；导入 PSD2Live 后用手工工作流调整层级、权重与模拟。

| 文件 | 内容 |
| --- | --- |
| [guide.md](guide.md) | 制作手册 |
| [chronology.md](chronology.md) | 过程与决策摘要 |
| [preview.md](preview.md) | 最终工程的动作 GIF 生成步骤 |
| [history/](history/) | 原始笔记与交付说明 |
| `tools/` | 拆层、配准、合成、写 PSD 与 MCP 调用脚本 |
| [import-index.json](import-index.json) | 原始资料到本仓库的对应关系 |
| [../prompts/](../prompts/) | Prompt 与任务记录 |

脚本保留原环境的 `/workspace/` 路径，部分依赖的 `mcp_client.py` 未随资料提供，按历史资料归档，未在本仓库执行。复用前请映射目录、配置 MCP 客户端，并以当前 MCP schema 为准。
