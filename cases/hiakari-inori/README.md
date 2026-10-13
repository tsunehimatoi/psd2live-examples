# 绯灯祈 · 无 see-through 拆分与复杂模拟

[案例索引](../README.md) · [下载素材包](https://github.com/tsunehimatoi/psd2live-examples/releases/download/assets-v2/hiakari-inori-1.0.0.zip) · [文件清单](manifest.json)

![动作与模拟预览](preview.gif)

grok bot + GPT Image（Codex exec 或 Web）的尝试，实践无 see-through 拆分，以及长衣袖、流苏、尾巴、裙子、铃铛等复杂模拟的效果。

导入后继续采用快速手工工作流，包括模拟调整。最终文件来自原资料根目录的工程与 `hiakari_inori_layers_v3-psd2live` 导出目录；`history/` 保存早期与实验版本。

动作 GIF 由 `ReadmeShowcaseTool.bodyOrbit` 读取最终工程生成，包含已保存的模拟。生成参数见 [preview.json](preview.json)，复现步骤见 [预览生成](workflow/preview.md)。

作者：grok bot。按 CC0 1.0 发布。角色与形象为原创，制作时未参考任何现有作品，如有雷同纯属巧合。

## 使用

```sh
python scripts/fetch.py --case hiakari-inori
```

- 工程：`project/hiakari_inori_layers_v3.psd2live`
- PSD：`psd-input/hiakari_inori_layers_v3.psd`
- 导出：`export/hiakari_inori_layers_v3.model3.json`
- 物理开/关对比：`preview/physics-on.gif`、`preview/physics-off.gif`
- 早期版本：`history/`

制作在 PSD2Live 3.4.2 / Linux 上完成。

## 内容

- [workflow/](workflow/README.md)：制作手册、过程记录与脚本
- [prompts/](prompts/)：出图 Prompt 与任务记录
- 前置尝试：[雾岛澪](../kirishima-mio/README.md)
