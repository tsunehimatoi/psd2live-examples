# 动作预览生成

[案例](../README.md) · [生成记录](../preview.json)

使用主项目 `ReadmeShowcaseTool.kt` 的 `bodyOrbit` 方法读取最终工程。动作仅加入内存副本，源工程保持原字节。

## 步骤

在主项目根目录执行，工程路径替换为已下载文件的绝对路径：

```powershell
$env:PSD2LIVE_TOOLS = '1'
$env:PSD2LIVE_ORBIT_PROJECTS = 'D:\examples\hiakari-inori\project\hiakari_inori_layers_v3.psd2live'
$env:PSD2LIVE_ORBIT_SIZE = '600'
.\gradlew.bat :test --tests 'io.github.psd2live.tools.ReadmeShowcaseTool.bodyOrbit' '-Ppsd2live.testHeap=6g' --no-daemon --rerun
```

身体依次上下、左右与椭圆摆动，再回到中立位置；X/Y 振幅为 8/10，周期 1.2 秒。工具输出开启/关闭物理两组 PNG 和模拟权重图，位于 `build/tools/readme-orbit/hiakari_inori_layers_v3-{on,off,pins}/`。

每组 172 帧、30 fps、600 px 长边。通过 FFmpeg 编成白底循环 GIF；首页版 320×480、15 fps、约 5.74 秒，素材包内另有 400×600 的开/关对比。

## 结果

本次成功读取七组模拟配置，涉及裙子、袖子后片、颈饰前/后片、耳朵、前发与尾巴。开/关物理的采样帧存在实际像素差异，源工程哈希与工具 commit 记录在 `preview.json`。

预览展示实际渲染效果，不作为固定像素验收基准。
