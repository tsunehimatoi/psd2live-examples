# PSD2Live Examples

[主项目](https://github.com/tsunehimatoi/psd2live) · [案例索引](cases/README.md) · [下载素材](https://github.com/tsunehimatoi/psd2live-examples/releases) · [案例投稿](https://github.com/tsunehimatoi/psd2live-examples/issues/new/choose) · [投稿指南](CONTRIBUTING.md)

PSD2Live 的示例素材、工程、导出模型，以及制作经验、Prompt 和 Skill。下载即可复现，也欢迎分享你的案例。

## 案例

| 案例 | 内容 | 标签 |
| --- | --- | --- |
| [tml](cases/tml/README.md) | 分层 PSD 导入、自动生成与导出 | 入门、生成、导出 |
| [ds](cases/ds/README.md) | 完整角色，含动作与物理 | 生成、动作、物理 |
| [star_lan](cases/star_lan/README.md) | 关节变形、多纹理与 AI 协作经验 | 骨架、纹理、MCP |
| [绯灯祈](cases/hiakari-inori/README.md) | grok bot + GPT Image，无 see-through 拆分与复杂模拟 | 拆分、模拟、grok |
| [雾岛澪](cases/kirishima-mio/README.md) | 绯灯祈的前置尝试：生成拆层、配准与遮挡补全 | 拆层、配准、grok |

带预览图的完整列表见 [案例索引](cases/README.md)。

## 下载

从 [Releases](https://github.com/tsunehimatoi/psd2live-examples/releases) 下载 zip 解压，或用脚本下载并校验（Python 3.11+，无第三方依赖）：

```sh
python scripts/fetch.py --case tml
```

`--all` 下载全部，文件写入 `examples/<案例 ID>/`。

## 投稿

无需 Git：在 [案例投稿](https://github.com/tsunehimatoi/psd2live-examples/issues/new/choose) 中附上示例（大文件贴网盘链接），写一两句做了什么、效果如何即可，维护者整理后发布。未完成或失败的尝试同样欢迎，不接受广告。

提交 PR 及内容要求见 [投稿指南](CONTRIBUTING.md)。

## 目录

```text
cases/<id>/        每份投稿一个目录
├── README.md
├── manifest.json  素材清单（有素材包时）
├── workflow/      方法、脚本与经验
├── prompts/
├── skills/
└── mcp/
scripts/           下载、校验、打包与 MCP 检查脚本
```

子目录按需创建，详见 [投稿规范](CONTRIBUTING.md#投稿规范)。

## MCP 服务检查

在 PSD2Live 的“工具 → MCP…”中启用服务，将端点和令牌设为环境变量 `PSD2LIVE_MCP_ENDPOINT`、`PSD2LIVE_MCP_TOKEN`，运行：

```sh
python scripts/mcp_discovery.py
```

检查初始化、工具分页发现和 `workspace_list_operations` 调用；不修改工程、不保存令牌，默认只连接本机端点。接口以主项目 [MCP 文档](https://github.com/tsunehimatoi/psd2live/blob/master/docs/zh/agent/MCP_AUTHORING.md) 为准。

## 许可证

除另有标注外，本仓库内容及 Release 素材按 [CC0 1.0](LICENSE) 发布，可自由使用、修改和商用，作者与来源保留在案例中。投稿默认同意此方式，其他许可请在投稿时注明。主项目的软件许可证不受影响。

<details>
<summary>技术说明</summary>

- 仓库只存说明、清单和脚本；PSD、工程、导出包等大文件通过版本化的 Release 附件分发。脚本下载和解压时都会核对清单中的大小与 SHA-256，全部通过才写入目标目录，压缩包缓存在 `build/example-assets/`。
- 主项目有独立的锁文件和同样的入口（`python tools/examples/fetch.py --case tml`），素材更新不会自动改变主项目的验收输入。
- 已有导出仅作展示。生成结果随版本和设置变化，不作为固定的视觉验收基准。
- 案例的能力分类使用清单的 `tags`，不复制素材。
- 产品内部接口、会话、重放和保存恢复的回归测试在主仓库。

</details>
