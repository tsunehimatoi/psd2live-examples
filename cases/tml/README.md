# tml 自动生成示例

[案例索引](../../README.md) · [下载素材包](https://github.com/tsunehimatoi/psd2live-examples/releases/download/assets-v1/tml-1.0.0.zip) · [文件清单](manifest.json)

原作者说明：由 AI 生成的示例。

本案例的素材、工程及展示输出按 **CC0 1.0 Universal** 发布。作者与来源信息作为资料保留。

## 使用步骤

1. 在示例仓库运行 `python scripts/fetch.py --case tml`，或在主仓库运行 `python tools/examples/fetch.py --case tml`。
2. 在 PSD2Live 中打开 `examples/tml/psd-input/tml.psd`。打开分层 PSD，检查自动生成结果，并导出模型文件族。
3. 从 `.model3.json` 加载已有运行时输出，并保留其引用的纹理、动作和物理文件。CMO3 用于编辑器检查，诊断 JSON 用于分析。

## 版本与结果

素材版本为 `1.0.0`。来源及兼容测试起点记录在清单的 `source` 与 `compatibility` 中。

这是既有素材与结果的迁移，未重新生成。结果可能随算法、设置和程序版本变化；已有输出用于展示，不是固定验收基准。生成新结果请使用独立输出目录。
