# ds 动作与物理示例

[案例索引](../../README.md) · [下载素材包](https://github.com/tsunehimatoi/psd2live-examples/releases/download/assets-v1/ds-1.0.0.zip) · [文件清单](manifest.json)

![导出模型的动作预览](preview.webp)

素材为社区自发创作的 DeepSeek 形象“大肥鱼”，与 DeepSeek 官方没有联系。

素材、工程及导出结果按 **CC0 1.0** 发布。

## 使用步骤

1. 下载上方素材包解压，或运行 `python scripts/fetch.py --case ds`（主仓库为 `python tools/examples/fetch.py --case ds`）。
2. 在 PSD2Live 中打开 `psd-input/ds.psd`。导入 PSD 后生成模型，预览动作和物理，检查导出文件。
3. 查看成品：加载 `.model3.json`，保留其引用的纹理、动作和物理文件；`.cmo3` 用于编辑器检查，诊断 JSON 用于分析。

## 版本与结果

素材版本 `1.0.0`，素材包中的导出由 **PSD2Live 0.1.0** 生成。预览由 Cubism SDK for Native 5-r.5 直接渲染素材包中的 `.model3.json`，依次播放点头、摇头与待机动作，物理开启。

来源与兼容版本见 [清单](manifest.json) 的 `source`、`compatibility`。

导出结果迁移自既有版本，未重新生成，仅供参考，不作为验收基准；结果会随算法、设置和版本变化。生成新结果请使用独立输出目录。
