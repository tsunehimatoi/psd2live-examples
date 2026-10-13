# 雾岛澪 · 前置尝试

[案例索引](../README.md) · [下载素材包](https://github.com/tsunehimatoi/psd2live-examples/releases/download/assets-v2/kirishima-mio-1.0.0.zip) · [文件清单](manifest.json)

![全身预览](preview.png)

grok bot + GPT Image 的前置尝试，包括生成拆层、配准、正脸重做与遮挡补全。后续的完整实践见 [绯灯祈](../hiakari-inori/README.md)。

作者：grok bot。按 CC0 1.0 发布。角色与形象为原创，制作时未参考任何现有作品，如有雷同纯属巧合。

## 使用

```sh
python scripts/fetch.py --case kirishima-mio
```

- 工程：`kirishima_mio_fullbody.psd2live`
- PSD：`kirishima_mio_fullbody_layers.psd`
- 导出：`export_cubism/`、`export_vtube_studio/`

制作在 PSD2Live 3.4.2 / Linux 上完成，未在 Cubism Editor 与 VTube Studio 中实测。

## 内容

- [workflow/](workflow/experience.md)：制作笔记与原交付说明
- 脚本与制作手册与绯灯祈共用：[workflow](../hiakari-inori/workflow/README.md)
