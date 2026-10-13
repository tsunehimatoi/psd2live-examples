# star_lan 关节与纹理示例

[案例索引](../../README.md) · [下载素材包](https://github.com/tsunehimatoi/psd2live-examples/releases/download/assets-v1/star_lan-1.0.0.zip) · [文件清单](manifest.json)

原角色说明：GPT-6.1 sol 自述的原创角色，原画由图像模型生成，PSD 在其基础上拆分。

本案例的素材、工程及展示输出按 **CC0 1.0 Universal** 发布。作者与来源信息作为资料保留。

## 使用步骤

1. 在示例仓库运行 `python scripts/fetch.py --case star_lan`，或在主仓库运行 `python tools/examples/fetch.py --case star_lan`。
2. 在 PSD2Live 中打开 `examples/star_lan/psd-input/star_lan.psd`。导入 PSD 或打开配套工程，检查关节变形、多纹理及动画预览。
3. 从 `.model3.json` 加载已有运行时输出，并保留其引用的纹理、动作和物理文件。CMO3 用于编辑器检查，诊断 JSON 用于分析。

## 版本与结果

素材版本为 `1.0.0`。来源及兼容测试起点记录在清单的 `source` 与 `compatibility` 中。

这是既有素材与结果的迁移，未重新生成。结果可能随算法、设置和程序版本变化；已有输出用于展示，不是固定验收基准。生成新结果请使用独立输出目录。

## MCP 体验记录

用图像模型与 MCP 做过纹理高清化和简单拆分。已有记录：衣物等大面积区域效果较好，眼睛等低像素细节保持不足。原始 Prompt、Skill 和完整调用记录尚未整理，因此此记录不作为可重放验收场景。

后续可尝试完整重绘后逐步擦除，并记录模型、客户端、素材版本与操作步骤。
