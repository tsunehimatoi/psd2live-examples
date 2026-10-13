# PSD2Live Examples

[主项目](https://github.com/tsunehimatoi/psd2live) · [素材下载](https://github.com/tsunehimatoi/psd2live-examples/releases) · [投稿指南](CONTRIBUTING.md)

这里收集 PSD2Live 示例素材、工程、制作经验、Prompt、Skill 与公开 MCP 接口验收案例。Git 保存说明、清单和脚本；PSD、工程、导出包等大文件通过版本化 Release 附件分发。

| 案例 | 用途 | 标签 |
| --- | --- | --- |
| [tml](cases/tml/README.md) | 分层 PSD 导入、自动生成与导出 | 入门、生成、导出 |
| [ds](cases/ds/README.md) | 完整生成与动作示例 | 生成、动作、物理 |
| [star_lan](cases/star_lan/README.md) | 关节变形、多纹理、工程与人机协作经验 | 骨架、纹理、MCP |

## 下载

Python 3.11 或更新版本，不需要安装第三方库。在本仓库根目录运行：

```sh
python scripts/fetch.py --case tml
python scripts/fetch.py --all
```

文件写入 `examples/<案例 ID>/`，压缩包缓存到 `build/example-assets/`。下载及解压均核对清单中的大小与 SHA-256；只有所有文件验证通过后才写入目标目录。也可以直接下载 Release 附件并解压。

主项目有独立锁文件和同样的下载入口：`python tools/examples/fetch.py --case tml`。素材更新不会自动改变主项目的验收输入。

## 分类与贡献

每个案例以 `cases/<id>/` 为单位，包含 `README.md` 和 `manifest.json`；相关 Prompt、Skill、固定 MCP 场景放在同一案例下。跨案例的内容分别放在 `prompts/`、`skills/`、`mcp/`。能力分类使用清单的 `tags`，不复制素材。

熟悉 Git 的用户通过 PR 提交案例说明与清单；其他用户可以通过 [案例投稿](https://github.com/tsunehimatoi/psd2live-examples/issues/new/choose) 分享素材链接、步骤与结果。维护者整理后发布素材包。

完整工程与导出文件族应一起打包，保留 `.model3.json` 引用的纹理、动作和物理文件。现有导出仅用于展示，生成版本和设置变化会影响结果，不作为固定视觉验收基准。

## MCP 验收

[MCP 目录](mcp/README.md) 提供外部 HTTP 发现检查与场景投稿约定。确定性调用与 Agent 自由执行的体验评测分别记录。产品的内部接口、会话、历史重放和保存恢复回归测试保留在主仓库。

## 许可证

除文件或案例明确另有标注外，本仓库内容及配套 Release 素材均按 **CC0 1.0 Universal** 发布，包括示例、工程、案例说明、Prompt、Skill 和脚本。现有三个案例均已在清单中明确标注 `CC0-1.0`。作者与来源作为资料保留。

投稿即表示同意上述默认发布方式；有单独许可的内容请在投稿及清单中明确说明。主项目的软件许可证由主项目维护，不受这里的素材许可改变。

见 [LICENSE](LICENSE) 与 [CC0 官方说明](https://creativecommons.org/publicdomain/zero/1.0/)。
