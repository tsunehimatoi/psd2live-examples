> 历史资料：保留当时的描述与版本信息，文件列表可能与本次导入不一致。以案例首页及 manifest.json 为准。

# PSD2Live v3.4.2 需求/用法整理(来自 README 与 docs/zh)

资料来源(均在 `/workspace/psd2live-src/`):`README.md`、`docs/zh/spec/PSD_LAYER_SPEC.md`、`docs/zh/guide/USER_GUIDE.md`、`docs/zh/guide/DEVELOPMENT.md`、`docs/zh/agent/MCP_AUTHORING.md`、`docs/zh/spec/EXPORT_TARGETS.md`,以及本机实测(括号内标【实测】)。标【文档未写】的是文档没有明确说明的点。

---
## (a) PSD 图层命名 / 分组规范

### 总原则
- 格式:**RGB、8 位、透明背景的分层 PSD**。文字、矢量、图层样式、调整图层要**先栅格化/合并**进像素层。
- 身体基本正立;头部可轻微倾斜(自动基准估计仍要在预览里核对)。
- **没有硬性"必须有哪些图层"的校验**:文档只说自动生成质量主要取决于分层;**未识别的图层不会丢弃**,会生成网格并用回退归属,可在界面「图层」表格里手动改类型/部件/侧别。命名只是预设入口,"命名成功不代表自动造型已通过验收"。
- 识别按名称(中/英/日/韩别名)匹配;完整别名以源码 `src/main/kotlin/io/github/psd2live/core/LayerClassifier.kt` 为准。

### 部件标签与可识别名称(文档表,节选自 PSD_LAYER_SPEC.md,不含 UNKNOWN)
| Tag | 名称 |
|---|---|
| BACK_HAIR 后发 | `back hair` / 后发 / 后髪 / 后脑勺 / 뒷머리 |
| FRONT_HAIR 前发 | `front hair` / 前发 / 前髪 / 刘海 / 앞머리 |
| HEADWEAR 头饰 | `headwear` / 帽子 / 头饰 / 頭飾 / 모자 |
| FACE 脸 | `face` / 脸 / 臉 / 脸部 / 얼굴 |
| FACE_DETAIL 脸部细节 | `facedetail` / 脸部细节 / 面部细节 / 腮红 / 볼터치 |
| IRIDES 虹膜(瞳孔) | `irides` / 瞳孔 / 虹膜 / 眼珠 / 눈동자 |
| EYEBROW 眉毛 | `eyebrow` / 眉毛 / 眉 / まゆ毛 / 눈썹 |
| EYEWHITE 眼白 | `eyewhite` / 眼白 / 白眼 / 白目 / 흰자 |
| EYELASH 睫毛 | `eyelash` / 睫毛 / まつ毛 / まつげ / 속눈썹 |
| EYE_CLOSE 闭眼 | `eye close` / 闭眼 / 閉眼 / 目閉じ / 감은 눈 |
| EYEWEAR 眼镜 | `eyewear` / 眼镜 / 眼鏡 / めがね / 안경 |
| EARS 耳朵 | `ears` / 耳朵 / 耳 / みみ / 귀 |
| EARWEAR 耳饰 | `earwear` / 耳环 / 耳環 / 耳饰 / 귀걸이 |
| NOSE 鼻子 | `nose` / 鼻子 / 鼻 / はな / 코 |
| MOUTH 嘴 | `mouth` / 口 / 嘴 / 嘴巴 / 입 |
| MOUTH_OPEN 张嘴 | `mouth open` / 张嘴 / 張嘴 / 开口 / 벌린 입 |
| MOUTH_CLOSE 闭嘴 | `mouth close` / 闭嘴 / 閉嘴 / 闭口 / 다문 입 |
| TOOTH_T 上牙 | `tooth-t` / 上牙 / 上歯 / 上齿 / 윗니 |
| TOOTH_B 下牙 | `tooth-b` / 下牙 / 下歯 / 下齿 / 아랫니 |
| TONGUE 舌头 | `tongue` / 舌头 / 舌頭 / 舌 / 혀 |
| NECK 脖子 | `neck` / 脖子 / 颈部 / 頸部 / 목 |
| NECKWEAR 领饰 | `neckwear` / 领饰 / 領飾 / 围巾 / 목도리 |
| TOPWEAR 上衣 | `topwear` / 上衣 / 衣服 / 服装 / 상의 |
| HANDWEAR 手臂/手 | `handwear` / 手臂 / 手 / 腕 / 팔 |
| BOTTOMWEAR 下装 | `bottomwear` / 下装 / 下裝 / 裤子 / 치마 |
| LEGWEAR 腿 | `legwear` / 腿 / 大腿 / 小腿 / 다리 |
| FOOTWEAR 脚/鞋 | `footwear` / 脚 / 腳 / 鞋 / 신발 |
| TAIL 尾巴 | `tail` / 尾巴 / 尾 / しっぽ / 꼬리 |
| WINGS 翅膀 | `wings` / 翅膀 / 翼 / つばさ / 날개 |
| OBJECTS 道具 | `objects` / 道具 / 物件 / 소품 |

### 左右侧(角色自身的左右,**角色左侧通常在画面右边**)
- 可识别的后缀/前缀写法:`eyelash-l`、`eyelash-r`、`eyelash_left`、`左睫毛`、`왼쪽 속눈썹`、`속눈썹_우`;也支持括号形式 `(L)`、`[右]`、`【左】`。韩文单字 `좌`/`우` 必须用分隔符或括号隔开。(源码正则确认:l/r/left/right/左/右/왼쪽/오른쪽/좌/우。)
- **没有侧别的双侧图层(如两只眼睛画在同一层)不会自动拆分**,会当一个部件生成;要左右独立动作,必须在 PSD 里分层,或进编辑器按网格/多边形拆分(「网格拓扑与拆分」)。
- 示例 ds.psd 的命名就是 `ears-l/ears-r`、`eyebrow-l/-r`、`eyewhite-l/-r`、`irides-l/-r`、`eyelash-l/-r`、`handwear-l/-r`(【实测】ds 识别出 26 层,眼睛各层侧别全部正确)。

### 头发
- **前发(front hair)与后发(back hair)必须分开**;被遮挡区域保留足够重叠余量,便于运动。
- 带数字的名称(`front hair 1`)用于区分素材;分类器会清理 Photoshop 副本后缀(copy / のコピー / 的副本 / 副本 / 복사 + 数字)。**数字名本身不会建立表情切换**。
- 文档没有"前/中/后"三层头发的规定:只有 FRONT_HAIR 和 BACK_HAIR 两类【文档未写 "中间发"】;侧发等可用同类名加数字,或交给未知图层手动归类。

### 眼睛
- **眼白、瞳孔(虹膜)、上睫毛分别绘制**;瞳孔保留被眼皮遮住的完整部分。
- 上睫毛预设不适合混入下眼眶线;即使命名器能识别"下睫毛",也应检查或改用独立细节层。
- 闭眼差分可用 EYE_CLOSE 命名(差分机制见下)。眉毛 EYEBROW 左右各一层。

### 嘴
- **提供最大张口素材**:可把口腔画成整体,或另分上牙(TOOTH_T)、下牙(TOOTH_B)、舌头(TONGUE)。闭口原图**无法靠几何变形恢复不存在的口腔**。
- MOUTH / MOUTH_OPEN / MOUTH_CLOSE 为可识别名;ds 示例里的嘴是 `mouth` + 子层 `mouth / 上唇描边`、`mouth / 下唇描边`(导出里自动生成 `ArtMeshMouth_lip_0/1`)。

### 身体部位
- 躯干/四肢/附属:NECK、TOPWEAR、HANDWEAR(左右)、BOTTOMWEAR、LEGWEAR、FOOTWEAR、TAIL、WINGS、NECKWEAR、OBJECTS。自动骨架(可选)按图层标签推断躯干/四肢/尾巴。
- 单层只有"一条领子"之类需要穿过其它部件时,用编辑器「前后分层」功能(见 docs/zh/guide/DEPTH_SPLIT.md)。

### 必需 vs 可选(综合文档与实测,非官方硬性规定)
| 级别 | 内容 |
|---|---|
| 官方明确建议(影响质量) | 眼白/瞳孔/上睫毛分层;张嘴素材(或上牙/下牙/舌头);前发与后发分开;身体基本正立;特效/文字先栅格化 |
| 想要完整头部转动 | 至少 FACE、FRONT_HAIR、BACK_HAIR、左右眼各部件、MOUTH(推断;文档未给最小清单) |
| 可选 | HEADWEAR、FACE_DETAIL、NOSE、EARS/EARWEAR、EYEWEAR、NECKWEAR、TAIL、WINGS、OBJECTS、差分层、EYE_CLOSE、MOUTH_OPEN/CLOSE 等 |
| 缺失时 | 不报错、不阻止导入;对应动作/参数不会生成或需手动修;未知名图层保留 |

### 差分(表情切换)
- 数字/名称不等于表情切换。**开关差分**:指定一个参数控制显示;**切换差分**:多个图层共享同一参数、设置不同"关联 ID"实现多选一;**预设**:走部件算法。可在图层表格的类型列(Preset / 开关 / 切换)和 ID 列设置。

### 图层组/文件夹
- 文档没有明确规定 PSD 图层组的语义【文档未写】。【实测】ds.psd 中图层被平铺识别,带 ` / ` 的名称(如 `mouth / 上唇描边`)表示"父组 / 子层"路径。建议用平铺命名,稳妥。

---
## (b) 推荐 PSD 尺寸 / 画布

- **文档没有给出明确的推荐尺寸/最低分辨率**【文档未写】。能确认的事实:
  - 仓库示例 PSD 尺寸【实测,读 PSD 头】:`ds.psd` 1280×1280;`star_lan.psd` 1280×1280;`tml.psd` 2048×2048;均为 RGB 8 位。
  - 网格间距的单位以"长边缩放到 2048 px 的文档像素"为参照(CLI `--mesh-spacing` 默认 64,GUI 默认 40;`--mesh-pixels` 则按源像素);即**设计基准是长边 ≈2048 px**。
  - 贴图集页面默认 4096(256–16384),页面会自动增长到能容纳最大图层的画布分辨率(下一个 2 的幂,最多 16384)。
  - 单文件图片导入限制:单张 ≤64 MiB 且 ≤16 百万像素;整批 ≤32 百万像素(影响用 MCP 导入图片,不是 PSD 本身)。
  - 星 lan 作者备注:眼睛等低像素细节在 AI 放大后无法保持 → 低分辨率素材细节会受限;可选「纹理高清化」(2×/4×,需本地 nunif Python 环境)。
- 实用建议(基于以上推断,非官方):正方形或接近的画布,长边 1280–2048 px;眼睛/嘴等细节层保证足够像素;角色居中、身体正立、四周留出头发/裙摆运动余量。

---
## (c) 工程 新建 / 导入 / 调整 / 导出 的 UI 流程
1. **导入 PSD**:菜单 **File → Import → 从 PSD 新建工程…**(中文界面)快捷键 `Ctrl+Shift+O`,或把 PSD 拖进窗口。在「开始」界面选**模型预设(最小 / 默认 / 完整)**,并勾选需要"按网格拆分"的图层(如画在同一层的左右腿)。
2. **核对识别结果**:右侧「图层 (Layers)」表格检查每层的部件类型、侧别、差分设置(类型 Preset/开关/切换、Binding、ID/侧别);识别错的直接改。快捷 `Ctrl+R` 重新分析 PSD。
3. **预览与修改**:顶部工作区标签(Edit、Mesh、Rigging、Animation、Preview、Physics、Texture、History,+ 新建);先去「预览」看动作和物理,再按需进入编辑/网格/绑定/动画/物理/纹理工作区。右上「Model presets」里可改 Rigging & Facial / Rig Values / Motions / Physics & Simulation(头发/衣服模拟、骨架)。
4. **保存**:`Ctrl+S` 保存 `.psd2live` 工程(含原始 PSD、素材、设置、编辑与历史分支)。**导出的 `.psd2live.json` 只是诊断报告,不能当工程用**。
5. **导出**:`Ctrl+G` 导出 Cubism 格式(.moc3 文件族 / .cmo3;目标版本 Cubism 3.0–5.3,默认 5.0);其它格式在 **文件 → 导出为**;`Ctrl+Shift+E` 导出分层 PSD。导出成功会弹窗,显示写入位置和警告/损失报告。纹理集设置在导出窗口里。导出 CMO3 时同时写 `.can3`(动作),需与 cmo3 放同目录。
6. 其他:已有 Cubism 模型 → 文件 → 导入 → 用 CMO3 替换当前模型 / 从 CMO3 新建工程;`F1` 打开程序内教程(零基础 18 课 / Cubism 经验者 13 课);「设置 → 提示」可恢复"不再提示"的弹窗;「工具 → 更新生成结果」把编辑合并到新版生成器结果。
- 导出目标(17 个,【实测】`PSD2Live targets`):moc3、cmo3、vtube-studio、psd-pose、spine(实验)、dragonbones(实验)、p2lrt、web、gltf(实验)、png-sequence、sprite-sheet、gif、mp4、webm、mov、apng、webp。视频/动图类需要 ffmpeg(box 已有 `/usr/bin/ffmpeg`)。
- Linux 要求:X11/GLX(XWayland 可用);无 GL 时自动回退软件渲染(【实测】box 上就是此情形)。

---
## (d) MCP 接口
- **启动**:MCP 服务**默认开启**,随 GUI 启动自动监听 `http://127.0.0.1:23871/mcp`(Streamable HTTP + Bearer 令牌;不要用已废弃的 `/sse`)。【实测】GUI 启动日志:`AI endpoint running: http://127.0.0.1:23871/mcp`。**必须先开着桌面 GUI**(CLI 模式不起 MCP)。
- **设置**:菜单 **Tools → MCP…**:开关服务、端口(1024–65535,默认 23871)、访问令牌(32–256 位字母/数字/-/_,可 Regenerate 或自己填)、工具集(Compact 精简 25 工具,默认;Complete 每操作一个工具)。改端口/令牌后点「Apply and restart」,已连接的宿主需更新配置。该对话框也提供 Claude Code 命令 / Codex TOML / JSON / Stdio 配置的复制。
- **令牌**:明文存在本机 Java Preferences;文档/界面默认掩码,需在对话框里「Show/Copy」。(【实测】本机令牌已被我改为 `[REDACTED_MCP_TOKEN]`。)无令牌访问 → HTTP 401。
- **连接示例**:`claude mcp add --transport http psd2live http://127.0.0.1:23871/mcp --header "Authorization: Bearer <TOKEN>"`;仅支持 stdio 的宿主用仓库根目录 `mcp_proxy.py`(环境变量 `PSD2LIVE_MCP_ENDPOINT`、`PSD2LIVE_MCP_TOKEN`)。
- **协议细节**【实测】:`POST /mcp`,头 `Authorization: Bearer …`、`Accept: application/json, text/event-stream`;先 `initialize`(返回 header `mcp-session-id`,后续请求带上)→ `notifications/initialized` → `tools/list` / `tools/call`。最小客户端:`/workspace/notes/mcp_client.py`。
- **精简工具集 25 个工具**(`/workspace/notes/mcp_tools_list.json`):
  - 单项:`workspace_overview`(一次读画布/参数/图层/变形器/物理/动作概况)、`workspace_inspect`(scope=project/settings/preview/objects/layers/parameters/physics/swings/paths/simulations/vertex_groups)、`workspace_list_operations`(分页发现)、`workspace_get_operation`(读单项 schema)、`workspace_apply_edits`(原子批量,1–128 项,全成功才提交一个历史节点)、`workspace_preview_edits`(试运行几何编辑)、`rig_deform`、`keyform_apply`、`workspace_call`(调用未直接发布的操作:`{"operation":"layer_classify","request":{...}}`)。
  - 意图工具:`author_axis`(建参数+关键形)、`author_physics`(物理组+拟合)、`author_compile`(只读,预览意图将编译出的成员)。
  - 族工具(`{"op":"<op>","request":{...},"wait_ms":0-30000}` 执行 `<族>_<op>`):`view`、`parameter`、`motion`、`skeleton`、`path`、`physics`、`simulation`、`swing`、`source_paint`、`snapshot`、`history`、`project`、`job`。
  - 全部公开操作共约 190 项(Compact 直接覆盖 98 项)。
- **用法要点**:
  1. 所有工具参数外层统一 `{"request": {...}}`(族工具是 `{"op":..., "request":{...}}`)。
  2. 先 `workspace_inspect {"request":{"scope":"project"}}` 或 `workspace_overview` 取当前 `state`(不透明令牌)和 `project_id`;写操作必须带 `state`;`request_id`/`project_id` 在 Compact 下可省略;`state` 冲突报 `state_conflict`。
  3. 后台操作返回 job:`wait_ms`(**最大 30000**)内完成则直接给终态,否则用 `job_wait`/`job_get` 继续。
  4. 工程/导出相关(均在 `project` 族):`import_psd`(绝对路径 `path`,可选 `discard_unsaved`)、`create_artwork`(PNG 等按位置建工程)、`import_cmo3`、`open`、`save`、`save_as`(`path`)、`export_model`(`output_directory` 绝对路径,导出 moc3/cmo3 文件族)、`export_target`(`target`+`output_directory`+`settings`)、`export_psd`(`path`)。
  4a. 图层分类:`workspace_call` → `layer_classify`(`layer_id`、`type`、`role`/部件、`side`、`parameter`、`switch_id`)。
  5. 纹理/图集:`layer_get_texture`、`atlas_get`、`atlas_pack`、`layer_set_pixel_density` 等;素材:`asset_*`、`layer_import_images`;动作:`motion_*`;物理:`physics_*`、`simulation_*`、`model_apply_preset`;骨骼:`skeleton_*`;历史:`history_checkpoint/list/checkout`。
  6. MCP 不生成图像,新增素材需宿主自带图像生成能力;"能调用工具 ≠ 复杂建模可靠"(见 docs/zh/STATUS.md,头发拆分与遮挡补全评价为"不可用")。
  7. MCP 与 GUI **共用同一个工作区**:MCP 导入/保存会直接替换 GUI 里当前工程;未保存工程切换默认被拒(`unsaved_changes`),除非 `discard_unsaved:true`。
- 【实测】已通过 MCP 完成:导入 ds.psd → overview → export_model(moc3/cmo3 文件族)→ save_as(.psd2live)→ export_target(png-sequence),全部成功,见 install_log.md §6。

---
## (e) 命令行(CLI)
- 启动器:`/workspace/psd2live/PSD2Live/bin/PSD2Live`(发布包,自带 JRE,免装 Java)。无参数 = 启动桌面 GUI;有参数 = CLI,**必须有 `--input`**(`--help` 除外)。源码版等价写法 `./gradlew run --args="..."`(需 JDK 21)。
- **能无界面从 PSD 直接生成并导出 moc3/cmo3:是**。【实测】不需要 DISPLAY,`ds.psd` 4.9 秒完成:
  `PSD2Live/bin/PSD2Live --input examples/ds/psd-input/ds.psd --output /workspace/notes/cli_out/ds [--lang zh]`
  → 产物 `ds.moc3`、`ds.cmo3`、`ds.can3`、`ds.model3.json`、`ds.cdi3.json`、`ds.physics3.json`、`ds.{idle,blink,nod,shake}.motion3.json`、`ds.4096/texture_00.png`、`ds.psd2live.json`。CLI **不产生可继续编辑的 `.psd2live` 工程**。
- **参数**(帮助 + DEVELOPMENT.md):
  | 参数 | 默认 | 作用 |
  |---|---|---|
  | `--input <path>` | 必填 | 输入分层 PSD |
  | `--output <path>` | PSD 同目录 `psd2live-output` | 导出目录 |
  | `--lang zh\|en\|ja\|ko` | 系统语言 | 日志语言 |
  | `--clear-user-data` | — | 单独使用:删除用户设置/工作区存储/`~/.psd2live` 缓存后退出 |
  | `--atlas <size>` | 4096 | 纹理集尺寸(256–16384) |
  | `--mesh-spacing <px>` | 64 | 网格间距(2048 px 文档基准) |
  | `--mesh-pixels` | 关 | 按源像素算网格间距 |
  | `--mesh-wrap <单位>` | 0 | 包裹拓扑,闭合窄缝 |
  | `--head-strength` / `--body-strength` | 1.0 | 头部转动/身体运动幅度 |
  | `--mesh-only` | 关 | 只出贴图集+网格 |
  | `--no-deformers` / `--no-motions` / `--no-physics` | 关 | 不生成变形器/动作/物理 |
  | `--no-cmo3` / `--no-moc3` / `--no-json` | 关 | 不输出对应文件(至少保留一种) |
  | `--upscale <1\|2\|4>` 及 `--upscale-python/--nunif-dir/--upscale-model/--upscale-tile/--upscale-noise/--no-upscale-neural-alpha` | 1(关) | 可选神经网络纹理高清化,需本地 nunif Python 环境 |
- **子命令**:
  - `PSD2Live targets`:列出 17 个导出目标及各自 `--set` 键。
  - `PSD2Live export <model.psd2live|input.psd> --target <t> [--set k=v ...] [--output dir] [--name base]`:从 .psd2live 工程(当前历史状态)或 PSD(默认设置)导出到任意目标,并写 `<名称>.<目标>.report.json` 损失报告。例:`export model.psd2live --target gif --set clip=Nod --set size=512`;`export model.psd2live --target psd-pose --set pose=ParamAngleX=20`。退出码:0 成功、1 导出失败、2 参数错误。
  - 实验性目标(spine / dragonbones / gltf)只能经 CLI 导出。
- 注意:CLI 的 `--mesh-spacing` 默认 64,GUI 初始为 40(文档说明),同一 PSD 两边生成结果略有不同。
- 【未测】`export` 子命令只看过帮助与文档,没实际跑(本次只跑了主 CLI 和 MCP 导出)。

---
## 其他可用信息
- 示例(`/workspace/psd2live-src/examples/`):`ds`(1280², 26 层)、`tml`(2048²)、`star_lan`(1280², 含 .concept.png 与 .psd2live 工程)。素材权利见各目录 readme,GPL 不自动覆盖素材。
- 许可:应用 GPL-3.0;format-model/format-compile/runtime(p2lrt)MIT。
- 兼容性提示:导出成功≠在所有运行时一致,正式使用前在 Cubism Editor/VTube Studio 里检查。
