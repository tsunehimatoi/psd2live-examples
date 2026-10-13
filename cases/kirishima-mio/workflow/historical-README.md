> 历史资料：保留当时的描述与版本信息，文件列表可能与本次导入不一致。以案例首页及 manifest.json 为准。

# 雾岛 澪 · 全身 Live2D 直播模型(PSD2Live v3.4.2 Linux 制作)

- `kirishima_mio_fullbody.psd2live`:PSD2Live 工程文件(用 PSD2Live 打开即可继续编辑)。
- `kirishima_mio_fullbody_layers.psd`:27 层拆层 PSD(第五版:脖子已补画到脸后面,脸放大 16%),2048×3072,已按 PSD2Live 命名规范命名。
- `export_cubism/`:moc3 / cmo3 / can3 / physics3 / cdi3 / 4 个动作(idle、blink、nod、shake) / 4096 图集。
- `export_vtube_studio/`:VTube Studio 可直接加载的包(含 .vtube.json)。
- `renders/`:`01_fullbody_*`(3072 px 全身)、`02_head_*`(头部特写)、`03_expression_sheet.png`(8 个姿势/表情)、`05_body_pose_check.png`(身体摆动检查)。
- `preview/`:idle 动作的 webm(2.4 MB)与 gif(42 MB,较大)。
- `PSD2Live_体验笔记.md`:体验笔记(现象、bug、体验不佳的地方)。
- `source_art/`:ChatGPT 生成的母版与每个部件的拆层原图(绿底)。`pipeline/`:抠图、配准、合成、写 PSD 的脚本和参数。

说明:唯一没有用图像生成补全的是腿部皮肤层(ChatGPT 内容过滤拒绝),取自母版并只对被裙子/袜子遮住的少量区域向外延伸,详见体验笔记第 5 节。未在 Cubism Editor 和 VTube Studio 里实测。
