> 历史资料：保留当时的描述与版本信息，文件列表可能与本次导入不一致。以案例首页及 manifest.json 为准。

# 绯灯 祈(Hiakari Inori)· 全身 Live2D 直播模型 v3(PSD2Live v3.4.2 Linux 制作)
v3 变更:大腿重新补画,从大腿根部到腹股沟画成完整的腿,顶部不再有截断、不再渐隐;修掉了膝盖内侧的浅色线。工程 `hiakari_inori_v3.psd2live`,PSD `hiakari_inori_layers_v3.psd`,导出文件都是 inori_v3.*。`renders/v3/` 里有隐藏裙子的渲染(10、11)和左右摆动渲染(08、09)。新图层在 `source_art/legs_v3/`。v1 备份在 `/workspace/backup_inori_v1/`,v2 在 `/workspace/deliver_inori/`。

v2 变更:腿部重新拆分(左右腿各分大腿 / 小腿含袜 / 靴,吊袜带单独成层)。v1 完整备份在 `/workspace/backup_inori_v1/`。

- `hiakari_inori_v2.psd2live`:PSD2Live 工程。`hiakari_inori_layers_v2.psd`:41 层拆层 PSD,2048×3072。
- `export_cubism/`、`export_vtube_studio/`:inori_v2 的 moc3 / 物理 / 动作 / 图集;VTube Studio 包含 .vtube.json。
- `renders/`:01–03 是 v1 渲染(上半身未变)。`renders/v2/`:v2 全身、身体 X + 尾巴摆动姿势、腿部特写,`ov_legs_v2.png`(合成 / 母版 / 4 倍差值图),`align_diff.json`(对齐数值)。
- `preview/inori_v2.webm`:idle 动作。
- `source_art/legs_v2/`:新腿部图层,`codex_jobs/` 是每个补画任务的输入、遮罩、提示词、codex 输出。
- `pipeline/`:脚本。leg_sr(母版腿部放大)、leg_mask / leg_split(可见与遮挡遮罩)、leg_jobs(codex 任务)、leg_assemble(合成)、leg_check(对齐检查)、ino_psd2(拼 PSD)、p2l(PSD2Live 调用)。

## v2 腿部图层(从下到上)
| PSD 图层 | 内容 | 网格 |
|---|---|---|
| legwear 1-l / 1-r | 左 / 右小腿(袜子,含靴子里的脚踝和脚) | ArtMeshLegwearL3 / R3 |
| legwear 2-l / 2-r | 左 / 右大腿(皮肤、袜口;底部渐隐 40px,与小腿重叠 80px) | ArtMeshLegwearL2 / R2 |
| footwear-l / -r | 左 / 右靴 | ArtMeshFootwearL / R |
| legwear 3-l / 3-r | 左 / 右吊袜带和流苏 | ArtMeshLegwearL / R |
| bottomwear | 裙子,已去掉吊袜带 | |
("-r" 是角色右侧,也就是画面左侧。画面右侧的腿压在下面。)

腿部变形器:PSD2Live 自动生成 腿部(DeformLegs)→ legwear 1/2/3 对称组、footwear 对称组。尾巴摆动 ParamTailA/B/C 和 PhysicsTails 已按 v1 参数重建。

说明:未在 Cubism Editor / VTube Studio 里实测导出的模型。
分卷合并:cat hiakari_inori_pkg_v3.zip.part* > hiakari_inori_pkg_v3.zip
