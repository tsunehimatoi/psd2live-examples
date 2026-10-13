# star_lan 关节与纹理示例

[案例索引](../../README.md) · [下载素材包](https://github.com/tsunehimatoi/psd2live-examples/releases/download/assets-v1/star_lan-1.0.0.zip) · [文件清单](manifest.json)

![导出模型的动作预览](preview.webp)

原角色说明：GPT-6.1 sol 自述的原创角色，原画由图像模型生成，PSD 在其基础上拆分。

素材、工程及导出结果按 **CC0 1.0** 发布。

## 使用步骤

1. 下载上方素材包解压，或运行 `python scripts/fetch.py --case star_lan`（主仓库为 `python tools/examples/fetch.py --case star_lan`）。
2. 在 PSD2Live 中打开 `psd-input/star_lan.psd`。导入 PSD 或打开配套工程，检查关节变形、多纹理及动画预览。
3. 查看成品：加载 `.model3.json`，保留其引用的纹理、动作和物理文件；`.cmo3` 用于编辑器检查，诊断 JSON 用于分析。

## 版本与结果

素材版本 `1.0.0`，素材包中的导出由 **PSD2Live 3.2.0** 生成。预览由 Cubism SDK for Native 5-r.5 直接渲染素材包中的 `.model3.json`，依次播放点头、摇头与待机动作，物理开启。

来源与兼容版本见 [清单](manifest.json) 的 `source`、`compatibility`。

导出结果迁移自既有版本，未重新生成，仅供参考，不作为验收基准；结果会随算法、设置和版本变化。生成新结果请使用独立输出目录。

## MCP 体验记录

用图像模型与 MCP 做过纹理高清化和简单拆分。已有记录：衣物等大面积区域效果较好，眼睛等低像素细节保持不足。原始 Prompt、Skill 和完整调用记录尚未整理，因此此记录不作为可重放验收场景。

后续可尝试完整重绘后逐步擦除，并记录模型、客户端、素材版本与操作步骤。
