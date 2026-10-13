# 绯灯祈 · 无 see-through 拆分与复杂模拟

[案例索引](../../README.md) · [下载素材包](https://github.com/tsunehimatoi/psd2live-examples/releases/download/assets-v2/hiakari-inori-1.0.0.zip) · [文件清单](manifest.json)

![动作与模拟预览](preview.gif)

grok bot + GPT Image（Codex exec 或 Web）的尝试，实践无 see-through 拆分，以及长衣袖、流苏、尾巴、裙子、铃铛等复杂模拟的效果。

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
