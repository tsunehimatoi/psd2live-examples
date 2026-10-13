# Live2D 直播模型完整流程手册(PSD2Live v3.4.2 Linux 版)

> 读者:和我用同一台 box 的下一个 AI agent(有 Shell、`codex` CLI、`grok` CLI、PSD2Live MCP,客户端是 `/workspace/tools/m.py`)。
> 目标:从零做出一个**高质量、全身、可直播**的 Live2D 模型,中途不走弯路。
> 依据:本手册只写 box 上实际跑过、留有记录的内容,每条结论后面都标了出处路径。两个已交付角色:
> - **雾岛 澪**(Kirishima Mio,第一个角色,做到 v5):`/workspace/deliver_full3/`
> - **绯灯 祈**(Hiakari Inori,第二个角色,做到 v3):`/workspace/deliver_inori/`(另有一份较早的 v3 草稿在 `/workspace/deliver_inori_v3/`)
>
> 主要来源:`/workspace/deliver_full3/PSD2Live_体验笔记.md`、`/workspace/deliver_inori/体验与建模笔记.md`、`/workspace/deliver_inori_v3/体验与建模笔记.md`、两个交付目录的 `README.md`、`/workspace/art/inori/char.md`、`/workspace/notes/install_log.md`、`/workspace/art/edit_try/NOTES.md`、`/workspace/tools/*.py|sh`、`/workspace/art/inori/**/prompt.txt` 和 `*.log`。

---

## 目录
0. 一页速查(TL;DR)
1. 总体策略(5 条铁律)
2. 环境与工具清单(脚本逐个说明)
3. 分步流程(带命令)
   - 3.1 角色设定
   - 3.2 全身母版
   - 3.3 头部特写(歪头检查)
   - 3.4 图层清单与命名
   - 3.5 并行生成分层
   - 3.6 色键抠图 + 去绿边
   - 3.7 对齐(最耗时)
   - 3.8 叠图 / 差值检查
   - 3.9 2x 放大与合成
   - 3.10 遮挡补画(裁切 + 洋红遮罩)
   - 3.11 腿和大腿专项
4. 写 PSD 与 PSD2Live MCP 操作
5. 渲染检查(rv.sh / view)
6. 实际用过的提示词(原文)和结果
7. 出图工具对比(codex / grok / GenerateImage / ChatGPT 网页 / HF Space)
8. 交付:打包、分卷、上传
9. 用户的期望与工作方式
10. 坑点清单
11. 交付前 QA 清单
12. 两个角色的已知问题

---

## 0. 一页速查(TL;DR)

1. **母版质量就是上限。** 先用 codex 生成全身母版(2:3,严格正面、对称站姿、纯白底),再生成一张**严格正面、眼线水平**的头部特写。拆层前**先量眼线角度**(澪第一版头部特写本身歪 1.7°,放回全身后变成 -4.7°,用户一眼就看出“脸歪了”)。
2. 按 **PSD2Live 能识别的命名**设计约 40 层(祈 v3 是 41 层,全部识别,没有 Unknown)。
3. 用 `codex exec` **8 路并行**按部件出“只保留该部件 + 补全被挡部分 + 纯 #00FF00 绿底”的图。
4. `key.py` 抠绿 + 去绿边 → 对齐(codex 每张都按自己的尺度重绘:偏移 10~90 px,缩放 0.6~1.4 倍):有纹理的层用 SIFT + `estimateAffinePartial2D`,眼睛用带缩放搜索的 ECC,脸底层用手工地标,姿势不对的手臂直接镜像另一侧。
5. **最好的做法(祈 v2/v3 定型)**:**看得见的像素直接取自母版**(母版对应区域 Real-ESRGAN 放大 2 倍对齐画布),**只有被遮挡的部分**用“精确裁切 + 洋红遮罩”交给图像生成补画,贴回时只取遮罩内的像素。不要用代码硬切或模糊填充冒充补画。
6. 大腿要从**裙下的大腿根**开始画,不能截断、不能渐隐;**每个裁切只放一条腿**(另一条腿填成纯绿背景)。检查时要看**隐藏裙子**和**左右摆动**的渲染。
7. `mkpsd.write()` 写 2048×3072 的 PSD → MCP `project import_psd`(**每次都新建工程,手动加的尾巴 swing 和物理会丢**)→ 重建尾巴 swing(目标写不带 `mesh:` 前缀的网格名)和 PhysicsTails → `export_target` 导出 moc3 / vtube-studio / webm。
8. **每次返工前先备份**(参考 `/workspace/backup_inori_v1/`、`/workspace/backup_v4/`)。
9. 交付包超过 100 MB 时用 7z 分卷(`.7z.001` 这种命名),上传 Google Drive;用户电脑离线时 CopyFromBox 会失败。
10. 只汇报用户**能直接看到**的结果;用户会放大看细节(袜子错位、截断),交付前自己先查这些。

---

## 1. 总体策略(5 条铁律)

### 1.1 母版质量决定上限
- 所有图层最终都要和母版对齐;母版上的细节(发丝、衣纹、五官)就是成品的上限。头部要另外生成**高精度特写**,因为全身母版里的脸太小(祈的全身母版 `master_1.png` 是 1024×1536,头部特写 `head_1.png` 是 1086×1448;头部层最后按 `Mhead2body.npy` 里约 0.2745 倍的相似变换缩回全身画布,再乘 2 放到 2048×3072)。
- 来源:`/workspace/deliver_full3/PSD2Live_体验笔记.md` 第 5 节;`/workspace/tools/ino_build.py`;`/workspace/art/inori/Mhead2body.npy`。
- 已知的代价:辫子、双尾、尾巴这些只在 1024 宽的全身母版上出现的部件,放大 2 倍后细节比头部差(祈的已知问题)。**下次做:全身母版尽量要大图,或者给长发和尾巴也单独出特写。**

### 1.2 头部特写必须严格正面、左右对称
- 澪的教训(`deliver_full3/PSD2Live_体验笔记.md`“第三轮”):ChatGPT 出的头部特写本身两眼连线倾斜约 1.7°,耳朵一高一低;再按 SIFT 求出的相似变换(含约 3° 旋转)放回全身,结果眼线变成约 **-4.7°**,眼睛还偏离脸的中线约 12 px,用户反馈“脸歪了”。先用 `symmetrize.py` 镜像补救,最后(第四版)还是**重新生成严格正面的特写,重做全部头部层**才解决。
- 祈从一开始就在提示词里写了 “STRICTLY front-facing, camera exactly level, head perfectly upright (eye line exactly horizontal) … symmetrical about the vertical centerline”,第一次就出了正脸(`deliver_inori/体验与建模笔记.md` 流程第 1 条)。
- **拆层前必须做的检查**:量两只虹膜中心连线的角度、两只耳朵的高度差;超过约 1° 就重新生成,不要靠后期旋转补救。

### 1.3 图层清单要先设计好,命名直接用 PSD2Live 能识别的
- 澪 27 层、祈 41 层,都是导入后一次全部识别,左右侧也判对了。命名规则见 3.4。

### 1.4 被遮挡的部分用图像生成补,不要用代码硬切
- 用户的原则是“所有被遮挡部分都由图像生成补全”。澪唯一的例外是腿部皮肤层(ChatGPT 拒绝生成,改为取母版像素并向外延伸约 35 px 和 10 px),在 README 里专门写了说明(`deliver_full3/README.md` 最后一段)。
- grok 有时会**自己写代码做泊松融合、模糊或取色填充**来冒充补画(证据:grok 在 `/tmp/inpaint_thigh.py`、`/tmp/compose_thigh.py` 里自己写的脚本;`knee_g1` 的成品就是这种,已作废,见 `deliver_inori_v3/体验与建模笔记.md`)。提示词里必须写上 “The magenta pixels must come from your image generation output (resize to canvas, copy only magenta-position pixels)”。

### 1.5 最终定型的做法:可见像素取自母版,只有被遮挡的区域按遮罩补画
- 祈 v2 定型(`deliver_inori/体验与建模笔记.md`“v2:腿再分一次”):
  1. 母版腿部区域用 Real-ESRGAN 放大 2 倍,对齐到 2048×3072 画布(`leg_sr.py`)。
  2. 用裙子、腰封、袖子图层的 alpha,加上背景色和吊袜带颜色,算出每条腿、每只靴的**可见遮罩**(`leg_mask.py`、`leg_split.py`)。
  3. 遮挡区域按“精确裁切 + 洋红色 #FF00FF 遮罩”交给 codex/grok 补画,**贴回时只取遮罩内的像素**(`leg_jobs.py`、`leg_assemble*.py`)。
  4. 结果:可见区域与母版逐像素一致,内部 p99 差值为 0;完全一致的像素比例:袜腿 99.4%、靴 99.3%、吊袜带 99.8%(`deliver_inori/renders/v2/align_diff.json`)。
- 好处:没有对齐误差,没有风格漂移;只有被遮住的地方是新画的。
- 代价:母版上画好的阴影(裙摆在大腿上的投影、吊袜带勒痕)会留在腿上,动起来时阴影跟着腿走。**下次可以把这些阴影区域也放进遮罩重画**(祈 v3 已经这样处理了吊袜带和裙摆投影)。

### 1.6 每次返工前先备份
- 澪做到一半工作区被重置过一次,丢了一批文件(`deliver_full3/PSD2Live_体验笔记.md` 第 5 节第 6 条)。PSD2Live 崩溃后的恢复对话框还卡死过,只能清掉 `~/.psd2live/agent-workspaces`(先备份到 `/workspace/art/recovery_bak`)。
- 习惯:每做一版就 `cp -a deliver_xxx backup_xxx_vN`;新版本的文件用新文件名(`inori_v3.*`),旧版本留在原位(`deliver_inori/` 里 v2 和 v3 同时保留)。

---

## 2. 环境与工具清单

### 2.1 PSD2Live 本体
- 启动器:`/workspace/psd2live/PSD2Live/bin/PSD2Live`(注意不是 `/workspace/psd2live/bin/...`)。源码和文档:`/workspace/psd2live-src`(release 包里不带 docs 和示例 PSD)。
- 启动 GUI(会同时启动 MCP):
  ```bash
  cd /workspace/psd2live && DISPLAY=:10 nohup PSD2Live/bin/PSD2Live > /workspace/notes/psd2live_gui.log 2>&1 &
  ```
  日志里出现 `AI endpoint running: http://127.0.0.1:23871/mcp` 就表示 MCP 起来了。没有 GL 时会回退到软件渲染(`Cannot create Linux GL context`),不影响使用。
- MCP 令牌:已经在 GUI 的 Tools → MCP… 对话框里设成固定值,写在 `/workspace/notes/mcp_client.py` 里(只监听 127.0.0.1)。重启后令牌仍然有效。
- 如果 `m.py` 连接被拒(祈 v3 做到一半时 GUI 进程消失过):用上面的命令重新启动。普通 `kill` 杀不干净,再启动会提示“PSD2Live 已在运行”,要用 `kill -9`。如果卡在“恢复未保存的编辑”对话框:先备份再清掉 `~/.psd2live/agent-workspaces`。
- CLI 不需要 DISPLAY:`PSD2Live/bin/PSD2Live --lang zh --input x.psd --output out/x` 大约 5 秒出 moc3/cmo3,但**不会生成可继续编辑的 .psd2live 工程**(`/workspace/notes/install_log.md` 第 5 节)。

### 2.2 `/workspace/tools/` 脚本说明

> 祈的脚本都写死了 `os.chdir('/workspace/art/inori')`。给新角色用时,复制一份再改 `D=` 和路径。用到 `sr.py` 的脚本要用 `/workspace/tools/venv-sr/bin/python` 运行(里面有 torch-cpu、spandrel)。

| 脚本 | 作用 | 关键参数 / 用法 |
|---|---|---|
| `m.py` | MCP 通用调用器。初始化会话,然后调用一个工具并打印 JSON | `python3 /workspace/tools/m.py <tool> '<json args>' [最多输出字符数]`,例如 `python3 /workspace/tools/m.py workspace_inspect '{"request":{"scope":"project"}}' 2000`。底层是 `/workspace/notes/mcp_client.py`(`rpc()`、`call()`) |
| `mview.py` | 和 m.py 一样,但会把返回的图片保存成 `<out>_<k>.png` | `python3 mview.py view '<args>' /tmp/out` |
| `rv.sh` | 渲染当前工程的快捷方式(`view` / `render_model`,透明背景,canvas_rect 视口) | `bash rv.sh <输出前缀> '<参数JSON>' [left top w h] [长边]`。默认全画布 0 0 2048 3072,长边 1600。例如 `bash /workspace/tools/rv.sh /tmp/legs '{"ParamBodyAngleX":10,"ParamLegSway":1}' 600 1300 900 1772 1200` |
| `key.py` | 绿幕抠图 + 去绿边 + 去噪点 | `python3 key.py in.png out.png`。`key(inp,out,lo=0.17,hi=0.96)`:用四角 8×8 像素估计背景色(接近纯绿时按 #00FF00 处理);alpha = 1 − (g−max(r,b))/背景绿度,再按 lo/hi 拉伸;前景色反推去掉背景;半透明处把 G 限制在 max(R,B)+6 以内去绿边;面积小于 40 px 的连通块删掉(防止 PSD2Live 把低透明度噪点的整个包围盒当成网格) |
| `ino_gen.py` | 用 codex 并行生成分层。`TPL` 是统一的提示词模板,`P` 是 {层名:(参考图, 部件描述)} | `python3 ino_gen.py <并发数> [层名...]`,例如 `python3 /workspace/tools/ino_gen.py 8`。输出到 `gen/<name>.png`,日志在 `gen/<name>.log`;已存在的跳过;每层最多试 2 次,单次超时 900 s。命令形式:`codex exec --skip-git-repo-check -s workspace-write -C <dir> "<prompt>"`,stdin 用 DEVNULL |
| `ino_sift.py` | SIFT 特征匹配 + `cv2.estimateAffinePartial2D`(RANSAC,阈值 4 px),求“抠好的层 → 参考图”的相似变换,打印内点数、缩放、旋转、平移 | `python3 ino_sift.py [层名...]`。`SIFT_create(nfeatures=6000, contrastThreshold=0.01)`,ratio test 0.8;成对的层(`PAIRS`:eye_white iris eyelash eyebrow legwear boots)先按中间 30%~70% 范围内 alpha 列和最小处切成左右两半再分别求变换;`fit()` 被 ino_build 调用 |
| `ino_align3.py` | ECC 配准:先做平移网格多起点搜索(小部件 ±30 px,大部件 ±90 px),再试一次仿射,只有缩放在 0.94~1.06 之间、剪切小于 0.05 时才采用 | `python3 ino_align3.py [层名...]` → `aligned3/`。小部件 blur 1.4,大部件 blur 2.5;用预乘 alpha 的 Lanczos 变换(`warp()`) |
| `ino_align5.py` | 带缩放搜索的 ECC(用于眼睛):缩放从 0.7 到 1.3、步长 0.04,每个缩放都跑一遍 ino_align3.fit,取 cc 最高的 | `python3 ino_align5.py eyelash iris eye_white eyebrow nose` → `aligned5/`。实测(`art/inori/align5.log`):睫毛 cc 0.92/0.84、s≈0.8;虹膜 cc 0.985/0.955、s=0.7;眼白 cc 0.68/0.58(不可靠);眉毛和鼻子 cc=-1(失败)→ 眼白和眉毛借用同侧睫毛的变换 |
| `ino_build.py` | 身体层:按变换(SIFT / 单位阵 / 手给矩阵)对齐,先用 Real-ESRGAN 放大 2 倍(`sr.process`,缓存在 `hr/`),再 `warp2(sc2(M))` 放到 2048×3072;头部层:读 `headfinal/*.png`,按 `Mhead2body.npy`×2 放回 → `final/` | `venv-sr/bin/python ino_build.py`。右臂 `armR = arm_L[:, ::-1]`(镜像),`tail_C` 用手写矩阵(缩放 0.6),`sleeve_R/braid/twintail` 用单位阵 |
| `ino_comp.py` | 按 `ORDER` 从下到上合成 `final/` 里的层,输出 `comp_full.png`、缩略图 `comp_full_s.png` 和头部放大图 `comp_head_zoom.png`,用来和母版对比 | `python3 ino_comp.py` |
| `ino_psd.py / ino_psd2.py / ino_psd3.py` | 拼 PSD(分别对应 v1/v2/v3)。按名字和顺序组层,成对的层用 `split()` 拆成 -r/-l,然后调用 `mkpsd.write` | `python3 ino_psd3.py /workspace/art/inori/inori_v3.psd` |
| `mkpsd.py` | `write(layers, (2048,3072), path)`:layers 是从下到上的 `[(名字, RGBA ndarray)]` 列表;每层按 alpha>0 的包围盒裁切,用 `psd_tools` 的 `PixelLayer.frompil` 写入并带上 top/left 偏移。`split_pair()` 按连通块把一层拆成左右两层 | 在其他脚本里 `from mkpsd import write` |
| `sr.py` | Real-ESRGAN(`weights/RealESRGAN_x4plus_anime_6B.pth`,用 spandrel 加载,CPU 8 线程)。`sr4()` 分块做 4 倍放大(tile 128,pad 12);`process(path)` 按包围盒裁切 → 用边缘颜色外扩 → 4 倍 → Lanczos 缩到 2 倍 → 低频颜色校正 → 防振铃夹紧 → alpha 也走 SR(或用 bic 模式);输出**原尺寸 2 倍**的 RGBA | `import sr as SR; o = SR.process('in.png')`(返回 ndarray)。眉毛、嘴、鼻子用 `alpha_mode='bic'` |
| `upscale.py / up_all.py` | 命令行 4 倍放大(会自动切换到 venv-sr);up_all 先按包围盒裁切再放大,存 `up4/meta.json` 记录偏移 | `python3 upscale.py in.png out.png --scale 4` |
| `symmetrize.py` | 澪第三轮的补救方案:以视觉右侧的眼白、睫毛、眉毛为准镜像出左侧;左侧虹膜保留原图,只移到对称位置;脸底层把右半边镜像到左半边 | `python3 symmetrize.py in.npz out.npz [轴x=1026.5]`。这只是补救,最终还是重新生成了正面特写 |
| `leg_sr.py` | 母版腿部区域 (340,660)-(700,1536) 做 4 倍再缩到 2 倍,贴进白底 2048×3072 画布,得到 `legs/master_hr.png` | 在 `/workspace/art/inori` 下运行 `venv-sr/bin/python /workspace/tools/leg_sr.py` |
| `leg_mask.py` | 遮挡 occ = 裙子(alpha>8)∪腰封∪两只袖子(alpha>40);用 master_hr 的白色连通区域判出背景;可见腿 = 候选区 ∩ 非背景 ∩ 非遮挡;再分出靴子 | 输出 `legs/occ.npy`、`vis_leg.npy`、`vis_boot.npy` |
| `leg_split.py` | 按颜色分出吊袜带(红/金);去掉白纱;逐行找两腿之间的背景缝,作为左右腿分割线 `cut_leg`(膝盖贴在一起的那段用插值并平滑);每条腿的轮廓 = 旧 legwear 层的轮廓 ∪ 可见区域,闭运算后逐行填满;hid = 轮廓 − 可见;下层腿多带 16 px 的内侧条带 | 输出 `vis_/hid_{leg,boot}_{R,L}.npy`、`gar_R/L.npy` |
| `leg_jobs.py` | v2 的 6 个补画任务(thigh_R/L、knee_L、foot_R/L、boot_L):每个任务一个框,`input.png` = 绿底 + 母版可见像素 + 洋红遮挡区;`mask.png`;`prompt.txt` | 输出 `legs/jobs/<job>/`,运行方式见 3.10 |
| `leg_thigh3.py` | v3 的大腿任务:遮罩从 y=1250 的大腿根开始(远在裙子和腰封下面),外侧沿可见轮廓线性外推再放宽 25 px,内侧沿分割线一直到两腿中间;闭运算 5 次;y≥1960 以下不算 | 输出 `legs/jobs3/thigh_{R,L}/`、`hid3_thigh_*.npy` |
| `leg_knee3.py` | 找出分割线 ±6 px 内比周围亮 8 以上的浅色像素(膝盖浅色线),和下层腿的遮挡区一起放进遮罩 | 输出 `legs/jobs3/knee/` |
| `leg_assemble.py / leg_assemble3.py` | 合成腿部层:可见区域取 master_hr,遮挡区域取各任务 `output.png` 遮罩内的像素(排除绿色和洋红);alpha 做 0.6 的高斯羽化;v3 中大腿(thigh)在 y=2060 以上 40 px 内渐隐,小腿(shin)从 y=1980 开始 | `python3 leg_assemble3.py '{"thigh_R":"thigh6_R_mirror","thigh_L":"thigh4_L_g3","knee":"knee4_g2"}'`(参数是选用的任务目录名;这里写的是 `deliver_inori/source_art/legs_v3/jobs/` 里的组合,示意用) |
| `leg_check.py / leg_check3.py` | 对齐指标:把腿部层合成后和 master_hr 比较,算 2 px 腐蚀后内部的 mean/p99/max/完全一致比例、边缘 2 px 平均差,以及漏到母版背景上的像素数;输出 `ov_legs_v*.png`(合成 / 加裙子 / 母版 / 4 倍差值) | `python3 leg_check3.py` → `legs/align_diff_v3.json` |
| `p2l.py / p2l_w.py` | MCP 帮助函数:`st()` 返回 (project_id, state),`job()`/`W()` 轮询后台任务直到结束(`job op=wait`,`timeout_ms` 30000),`R()` 生成 request_id | 被 p2l_v3 等脚本引用 |
| `p2l_v3.py` | 导入 PSD → 重建三条尾巴的 swing → PhysicsTails → 腿部 ParamLegSway | `python3 p2l_v3.py`(先改里面的 PSD 路径) |
| `p2l_v3exp.py` | `save_as` 保存工程,然后 `export_target` 导出 moc3 / vtube-studio / webm | `python3 p2l_v3exp.py` |
| 其他 | `build_psd_full.py`、`assemble3.py`、`headbuild3.py`(+`headparams3.json`)是澪的 PSD 和头部合成脚本(副本在 `deliver_full3/pipeline/`);`hf_edit.py`、`try_edit.py`、`/workspace/art/run_edits.sh`、`retry_missing.sh`、`ql.py` 是 HF Space 的尝试(都失败了,见第 7 节) | |

---

## 3. 分步流程(带命令)

工作目录约定(按祈的布局):`/workspace/art/<角色>/`,下面有 `gen/`(原始生成图)、`keyed/`(抠好的图)、`aligned*/`(对齐结果)、`headfinal/`(定稿头部层,头部特写坐标)、`hr/`(2 倍放大缓存)、`final/`(画布坐标的定稿层)、`legs/`(腿部专项)。

### 3.1 角色设定(`char.md`)
- 先写一份设定文档,后面所有提示词都从这里取词。祈的设定 `/workspace/art/inori/char.md`:约 18 岁,狐耳巫女 × 近未来机能风;发型左右不对称(画面左编发、画面右低双尾);异色瞳(画面左金色、画面右绯红);狐狸半面具;分离式宽袖;腰封配铃铛;纱裙;过膝袜 + 吊袜带;厚底短靴;颈带;三条狐尾。配色白、绯红、金,加少量黑。
- 写法要点:**所有左右都用 “viewer's left/right”(画面左/右)**,PSD 命名时再换成角色的左右(`-r` 是角色右侧,也就是画面左侧)。
- 设计上的教训:不对称元素越多,后面越难做镜像补救;三条尾巴、编发这类部件会额外多出层和物理工作。过膝袜、吊袜带、超短裙会让大腿补画频繁触发内容审核(见 3.11)。**如果目标是少走弯路,下装可以选不露大腿的款式**(比如长袜接短裤或长一些的裙子)。

### 3.2 全身母版
- 用 codex 生成(提示词原文见 6.1)。命令形式:
  ```bash
  cd /workspace/art/<角色>
  codex exec --skip-git-repo-check -s workspace-write -C /workspace/art/<角色> "<提示词>" < /dev/null > codex_master1.log 2>&1
  ```
- **一定要加 `< /dev/null`**,否则 codex 会显示 “Reading additional input from stdin...” 然后一直等。
- 要求:2:3 竖图,尽量大;严格正面,站直;手臂略微离开身体、手掌张开;双脚并拢,姿势对称;头到鞋全部入画;纯白底,地面无阴影,无文字;多尾巴要分开摆,每条都能看到。
- 祈的结果:`/workspace/art/inori/master_1.png`(1024×1536),一次成功。

### 3.3 头部特写(严格正面 + 歪头检查)
- 提示词见 6.2。输出 `head_1.png`(祈是 1086×1448)。
- **必须检查**:
  ```python
  # 量眼线角度:在 head_1.png 上标出两只虹膜中心(可以先粗略生成 iris 层再算 alpha 质心)
  import numpy as np; (x1,y1),(x2,y2)=(...),(...)
  print(np.degrees(np.arctan2(y2-y1, x2-x1)))   # |角度| > ~1° 就重新生成
  ```
  还要看:两只耳朵的高度、下巴尖是否在两眼中点的正下方。
- 头部特写 → 全身的变换只用**相似变换**,而且**旋转要接近 0**(祈的 `Mhead2body.npy` = [[0.2745, -0.0015, 360.6],[0.0015, 0.2745, 7.1]],旋转约 0.3°)。澪就是被 SIFT 求出的约 3° 旋转把脸带歪了。
- 特写和全身母版的发型会有细微差别(澪的笔记第 5 节第 5 条),最终用特写的脸 + 全身的身体,成品里看不出来。

### 3.4 图层清单与 PSD2Live 命名
PSD2Live 按名字识别 role 和左右(`-l`/`-r` 后缀,指**角色自己**的左右),同一 role 的多层用数字区分(`handwear 1`、`tail 3`)。MCP `project` 的 role 枚举:`back_hair, front_hair, headwear, face, face_detail, irides, eyebrow, eyewhite, eyelash, eye_close, eyewear, ears, earwear, nose, mouth, mouth_open, mouth_close, tooth_t, tooth_b, tongue, neck, neckwear, topwear, handwear, bottomwear, legwear, footwear, tail, wings, objects`(来自 `/workspace/notes/mcp_tools_list.json`)。

**祈 v3 的 41 层(从下到上,`/workspace/tools/ino_psd3.py`)**:
```
tail 3, tail 1, tail 2, back hair, ears-r, ears-l,
legwear 1-l, legwear 2-l, legwear 1-r, legwear 2-r,      # 小腿(袜+靴里的脚) / 大腿
footwear-l, footwear-r, legwear 3-l, legwear 3-r,        # 靴 / 吊袜带
bottomwear, neck, handwear 1-r, handwear 1-l, topwear, bottomwear 2,   # 裙 / 脖子 / 手臂 / 上衣 / 腰封
handwear 2-r, handwear 2-l, neckwear, face, nose,        # 袖子 / 颈带 / 脸底层 / 鼻
eyebrow-r, eyebrow-l, mouth close, mouth open, front hair,
eyewhite-r, eyewhite-l, irides-r, irides-l, eyelash-r, eyelash-l,      # 眼睛放在前发之上(透过刘海)
front hair 2, headwear 2, headwear 1, back hair 2, back hair 3         # 呆毛 / 发饰 / 面具 / 编发 / 双尾
```
**澪 v5 的 27 层**(`/workspace/tools/build_psd_full.py`):`back hair, legwear 1-l/-r(腿皮肤), legwear 2-l/-r(袜子), footwear-l/-r, bottomwear, topwear, handwear-r/-l, neck, neckwear 1(领子), neckwear 2(蝴蝶结), face, nose, eyebrow-r/-l, mouth close, mouth open, front hair, eyewhite/irides/eyelash ×左右`。

命名要点:
- **一定要同时给 `mouth close` 和 `mouth open`**:有张嘴图时,张嘴参数能真正露出口腔、牙齿和舌头;只有一张闭嘴图时,张嘴只是把线条拉开。另外建议关掉 `mouthOutlineEnabled`,否则闭嘴时会出现双线(澪笔记第 2 节第 12 条)。
- 同一 role 的多层,网格编号顺序**和 PSD 顺序不一致**:`tail 1` 对应 `ArtMeshTail2`;`legwear 3` 对应 `ArtMeshLegwearL/R`,`legwear 1` 反而对应 `L3/R3`。**导入后要用 `workspace_inspect` 查出真实的网格名,再写 swing 目标**。
- 祈的腿部层(v2 起):`legwear 1-*` 小腿(袜子,包括靴子里的脚踝和脚)→ `ArtMeshLegwearL3/R3`;`legwear 2-*` 大腿 → `L2/R2`;`footwear-*` → `ArtMeshFootwearL/R`;`legwear 3-*` 吊袜带 → `ArtMeshLegwearL/R`。画面右侧的腿压在下面。
- 刘海比母版更遮眼时,把眼白、虹膜、睫毛放在前发**之上**,PSD2Live 导入后没问题(澪第四版)。
- 同名图层会弹警告,但实际靠稳定 ID 区分,不影响结果。
- 祈没放进去的:腮红层(绿底抠图会把腮红抠坏,澪也舍弃了;如果要做,应该让模型在白底上出图,再用“正片叠底”);`eye_close` 层(眨眼用睫毛形变,效果正常);领子背面、裙子内衬。

### 3.5 并行生成分层(codex,8 路)
```bash
cd /workspace/art/<角色> && mkdir -p gen
python3 /workspace/tools/ino_gen.py 8 > gen_run.log 2>&1 &     # 全部层
python3 /workspace/tools/ino_gen.py 4 front_hair mask          # 只重跑某几层
```
- 头部层用 `head_1.png` 作参考,身体层用 `master_1.png`。提示词模板和每层描述原文见 6.3。
- 实际数据(`art/inori/gen_run*.log` 和 `gen/*.png` 的修改时间):31 层,11:25 开始,12:26 全部完成;头部 12 层大约 4.5 分钟出完,每张约 1–3 分钟;`front_hair` 第一次超过 900 s 超时,导致 ThreadPool 抛异常、整轮中断(`gen_run.log`),之后重跑成功。**建议在 run() 里捕获 TimeoutExpired,不要让一层超时拖垮整轮**。
- 并发再高会出现 “model is at capacity”(笔记里的 codex 列)。
- 生成后要逐张查看(拼成一张总览图,比如 `keyed_sheet.png`),常见问题:
  - 姿势不同:祈的右臂画成了另一个姿势 → 改用左臂镜像。澪的左右臂比例不一致,不能直接镜像复用,要分别配准。
  - 部件缺失或多余:澪的上衣没有袖子也没有领子(正好方便拆层);澪的脖子层被补成很宽的肩膀,要用梯形遮罩限制在领口以内。
  - 尺度漂移:见 3.7。
  - 看不到的部件(祈的第三条尾巴 `tail_C`)只能完全靠生成;它的尺寸不准,用手写矩阵(缩放 0.6)放到另外两条尾巴之间。

### 3.6 色键抠图 + 去绿边
```bash
mkdir -p keyed && for f in gen/*.png; do python3 /workspace/tools/key.py "$f" keyed/$(basename "$f"); done
```
- 必须去绿边(`key.py` 里的 despill 那一步),否则嘴唇和发丝边缘会带绿色或彩色的边(澪笔记第四版第 2 条)。
- 必须去小噪点:背景里残留 3%~10% alpha 的噪点时,PSD2Live 不会报错,而是把噪点所在的整个包围盒当成网格,渲染出一整块洋红或黑色方块(澪笔记第 2 节第 2 条)。抠图后检查每层的 alpha 包围盒是否远大于有效内容。
- 细发丝和半透明阴影(比如腮红)会被抠坏 → 不要单独出腮红层。

### 3.7 对齐(整个流程最耗时的一步)
codex 画每个部件时都会按自己的尺度重绘:**偏移 10~90 px、缩放 0.6~1.4 倍**都出现过(祈);ChatGPT 生成的澪身体层缩放在 0.35~0.88 之间。必须逐层配准:

| 部件类型 | 方法 | 工具 | 实测 |
|---|---|---|---|
| 有纹理的大部件(靴、袜、裙、腰封、上衣、袖、尾巴、颈带、前发) | SIFT + `estimateAffinePartial2D`(相似变换,RANSAC 4 px) | `ino_sift.py`,在 `ino_build.py` 里调用 | 内点数:裙 84,袖 55,腰封 41,袜 38/15,上衣 36,靴 31/29,尾巴 31/12(`art/inori/build.log`)。可靠 |
| 眼睛部件 | 缩放搜索 0.7~1.3 + 平移网格的 ECC | `ino_align5.py` | 睫毛约 0.8 倍,虹膜 0.7 倍(cc 0.98) |
| 低纹理部件(眼白、眉毛、鼻子) | 自己对不准 → **借用同侧睫毛的变换**;嘴和鼻子按中线居中 | 手工 | ECC cc=-1 或 0.6 左右,不能信 |
| 脸底层 | **手工地标**:按下巴、脸颊(或耳宽)位置做**横纵不同比例**的缩放 | 手工 | codex 和 ChatGPT 都会把脸画长 |
| 大面积同色层(澪的袖子、上衣) | ECC 不稳 → 手工量地标 + 半透明叠加原图对准 | 手工 | |
| 姿势不对的层 | 用另一侧**水平镜像** | `arm[:, ::-1]` | 祈的右臂 |
| 生成图本来就和输入对齐(grok 补画、codex 自己贴回) | 不用对齐 | | grok 缩放后可见区域平均误差 3.7~8/255;codex 自己贴回的误差为 0 |

- **数字指标不可全信**:对齐的误差和置信度多次给出互相矛盾的结果,最后都要**叠图肉眼复核**(祈笔记流程第 3 条)。
- 头部层在头部特写坐标里对齐(参考图是 `head_1.png`),定稿后放进 `headfinal/`;身体层在全身母版坐标里对齐。最后由 `ino_build.py` 统一放到 2048×3072 画布。
- 对齐后旋转要接近 0;眼睛、睫毛、眉毛要以**脸的中线**为轴左右对称摆放(澪第三轮发现眼睛整体比中线偏左 12 px)。

### 3.8 叠图 / 差值检查
- 每层对齐后:把该层以 50% 不透明度叠在母版上,或画出层的轮廓线,导出放大图逐个看。祈留下的检查图:`art/inori/ovB.png`、`ovArm.png`、`ovH_cmp.png`、`eyes_aligned5.png`、`chk_ear_L.png`、`neck_view.png` 等。
- 腿部(可见像素取自母版的方案)用 `leg_check3.py` 计算指标,合格标准参考祈 v3(`deliver_inori/renders/v3/align_diff_v3.json`):
  - 袜腿:内部 mean 0.18,p99 2,完全一致 98.4%(v2 是 99.4%;v3 有意把膝盖浅色线放进遮罩重画,所以降低)
  - 靴:mean 0.13,p99 0,完全一致 99.3%
  - 吊袜带:p99 0,完全一致 99.8%
  - 边缘 2 px 平均差 5~12/255(羽化造成,正常)
  - `ov_legs_v3.png` 四联图(合成 / 加裙子 / 母版 / 4 倍差值),差值图在可见区域应该接近全黑。
- **用户会自己放大看袜子和靴子是否错位**。这个检查是用户发现问题后才加上的,以后一开始就要做。

### 3.9 2 倍放大与合成
- 身体层:先在原分辨率上按包围盒裁切,用 Real-ESRGAN 做 4 倍放大再缩到 2 倍(`sr.process`),然后按对齐变换**一次性**放到 2048×3072(`ino_build.warp2(sc2(M))`)。这样能保留线条质量(澪笔记第 4 节)。
- 头部层:特写分辨率更高,直接缩小(约 0.549 倍 = 0.2745×2)。
- 合成预览:`python3 /workspace/tools/ino_comp.py` → `comp_full.png`。
- 预览小坑:Read 图片会按路径缓存,同一个文件名多次预览会看到旧图 → **每次预览换一个文件名**。

### 3.10 遮挡补画(裁切 + 洋红遮罩)——定型做法
1. 定出可见遮罩 `vis` 和遮挡遮罩 `hid`(参考 `leg_mask.py`、`leg_split.py`)。
2. 给每个任务定一个框 (x0,y0,x1,y1),生成:
   - `input.png`:框内填纯绿 (0,255,0);`vis` 的位置放母版像素;`hid` 的位置填洋红 (255,0,255)
   - `mask.png`:hid 的位置为白色
   - `prompt.txt`:提示词原文见 6.4
3. 并行跑(codex 和 grok 可以对同一个任务各跑一份,目录名加 `_cN` / `_gN` 后缀区分,祈 v3 就是这样做的):
   ```bash
   # codex(1~3 分钟)
   cd legs/jobs3/thigh_L_c1 && codex exec --skip-git-repo-check -s workspace-write -C "$PWD" "$(cat prompt.txt)" < /dev/null > codex.log 2>&1 &
   # grok(5~25 分钟)
   cd legs/jobs3/thigh_L_g1 && grok -p "$(cat prompt.txt)" < /dev/null > grok.log 2>&1 &
   ```
   (上面是按 `codex.log` / `grok.log` 的文件布局还原的命令写法;grok 用的是 `-p/--single` 单轮模式,自动执行工具的权限按当前 grok 配置,需要时加 `--always-approve`。)
4. 回贴:输出缩放到框的尺寸,**只取 `hid` 内、且不是绿色也不是洋红的像素**(`leg_assemble3.isgreen/isMag`);可见区域永远用母版像素。
5. grok 会多轮自我修正,有时最后交出的是**它自己用代码平滑过的结果**。可以直接从 `~/.grok/sessions/<URL 编码的 cwd>/<session-id>/images/` 里拿它每一轮的原始生成图,挑最好的一张(祈 v3:`deliver_inori_v3/体验与建模笔记.md`)。
6. 挑选结果时,做一张多候选并排的对比图,按“轮廓自然、无竖棱、无截断、无碎片、袜口连续”的标准选。选中的放进 `legs/jobs3/picked/`,交付时把选中任务的 input/mask/prompt/output 复制到 `source_art/legs_v3/jobs/`。

### 3.11 腿与大腿专项(最容易被用户挑出问题的地方)
- **每个裁切只放一条腿**:另一条腿整个填成纯绿背景(用户的要求;两条腿同时出现时,模型会把两条腿画到一起,或者在中间画出竖棱)。
- **大腿必须从裙下的大腿根开始完整画出来**:遮罩从约 y=1250 开始(远在裙子和腰封的下面),外侧沿可见轮廓往上外推,内侧一直画到两腿中间。生成图里腿外的绿色部分抠成透明,这样顶部是自然的胯部弧线,不是一条水平线。**不能截断、不能硬边、不能渐隐**:用户检查过隐藏裙子后的效果;v2 的大腿“底部渐隐 40px”,v3 的大腿顶部都不能有渐隐。
- 吊袜带、裙摆投影、零碎的可见色块也一并放进遮罩重画,避免出现斑块和截断(祈 v3 第 1 条)。
- 膝盖浅色线:遮罩向外扩 3 px,把浅色像素包进去,只重画下层腿的内侧轮廓(`leg_knee3.py`,`knee4` 任务)。
- 一侧怎么都补不好时:用画好的那一侧**水平镜像**,用可见像素和镜像结果的差值做平滑颜色校正,只填遮罩内的像素(祈右大腿 `thigh6_R_mirror`;两侧裁切框正好以 x=1020 对称)。袜口挂饰等不对称的地方要按最佳偏移单独对齐后再贴入。
- **检查清单**:隐藏裙子的全身图和腿部图、隐藏裙子 + 身体左右摆动 + 腿部摆动、只显示腿和靴(去掉裙子和吊袜带)、膝盖特写。祈 v3 的这些渲染在 `deliver_inori/renders/v3/04~09_*`(每张都有透明底和白底两版)。隐藏裙子的检查可以在 numpy 里把各层(不含裙子)合成后看(`leg_check3.py` 里的 `c` 和 `c2`),也可以另写一份不带裙子的 PSD 导入后渲染。
- 腿部摆动参数:PSD2Live 自动生成的腿部对称组 `DeformPair_*` **没有任何参数轴**。祈 v3 用 swing 给 `DeformLegs` 加了 `ParamLegSway`(lateral,magnitude 0.04,softness 0.8,parallel 0.3,不带物理),只是整体小幅左右摆动。

---

## 4. 写 PSD 与 PSD2Live MCP 操作

### 4.1 写 PSD
```python
import sys; sys.path.insert(0,'/workspace/tools')
from mkpsd import write
layers = [('tail 3', arr_tailC), ('tail 1', arr_tailL), ...]   # 从下到上,RGBA uint8,2048x3072 画布坐标
write(layers, (2048, 3072), '/workspace/art/<角色>/<角色>_v1.psd')
```
- 成对的层用 `split()`(按 alpha 列和最小处切开)或 `mkpsd.split_pair()`(按连通块)拆开;返回顺序是 [画面左(角色右,`-r`), 画面右(角色左,`-l`)]。
- 2048×3072、27~41 层的 PSD,MCP 导入约 2 秒,导出 moc3+cmo3 约 2 秒。纹理会打包成一张 4096 图集(约 4.3 MB)。

### 4.2 MCP 调用约定(经验)
- 所有写操作都要带 `state`(从 `workspace_inspect scope=project` 或上一次结果里拿),很多操作还要带 `project_id`、`request_id`(UUID)。每做完一步都重新 `st()` 拿新的 state(`p2l_v3.py` 的写法)。
- 长任务返回 `terminal:false` 时,用 `job` 的 `op=wait`(`timeout_ms` ≤30000)轮询;`workspace_call` 的 `wait_ms` 也不能超过 30000。
- 参数名不统一:`workspace_get_operation` 用 `id`,`workspace_call` 用 `operation`。
- `workspace_inspect` 分页**没有 `cursor` 字段**,要用 `offset` 或 `query` 翻页/过滤,例如:
  ```bash
  python3 /workspace/tools/m.py workspace_inspect '{"request":{"scope":"objects","query":"Tail"}}' 4000
  ```
- MCP 和 GUI 共用同一个工作区:`import_psd(discard_unsaved=true)` 会直接替换 GUI 里正在编辑的工程。**要先 save_as 保存好上一版**。

### 4.3 导入 PSD(每次都会新建工程!)
```python
c.call('project',{'op':'import_psd','request':{'path':PSD,'discard_unsaved':True,'request_id':R(),'project_id':pid,'state':s}})
```
- **没有“替换图层、保留绑定”的重新导入**:import_psd 每次都新建工程,之前手动加的 swing、自定义物理、腿部参数**全部丢失**,必须重建(下面的 4.4 要每次都跑)。
- 导入后查看识别结果:`workspace_overview`,或者 `workspace_inspect`(Binding 列才是真正的识别结果;GUI 里 Type 列全是 "Preset")。确认没有 Unknown,左右正确。

### 4.4 重建尾巴 swing + PhysicsTails + 腿部摆动(`/workspace/tools/p2l_v3.py` 原样)
```python
for T,P in [('ArtMeshTail','ParamTailA'),('ArtMeshTail2','ParamTailB'),('ArtMeshTail3','ParamTailC')]:
    c.call('swing',{'op':'put','request':{'id':'swing_'+P,'name':'swing '+P,'state':s,'targets':[T],
      'motions':[{'kind':'lateral','parameters':[P],'magnitude':0.25,'lift':0.04,'softness':0.6,'zoom':0.0,'parallel':0.7,
                  'physics':{'length':16.0,'mobility':0.92,'delay':0.9,'acceleration':1.3,'output_scale':1.6}}]}})
    pid,s=st()
c.call('physics',{'op':'put','request':{'id':'PhysicsTails','name':'尾巴摆动','state':s,'enabled':True,
  'inputs':[{'parameter':'ParamAngleX','weight':40,'type':'x'},{'parameter':'ParamBodyAngleX','weight':60,'type':'x'},{'parameter':'ParamBodyAngleZ','weight':50,'type':'angle'}],
  'outputs':[{'parameter':'ParamTailA','vertex':1,'scale':1.0},{'parameter':'ParamTailB','vertex':1,'scale':1.0,'reflect':True},{'parameter':'ParamTailC','vertex':1,'scale':0.7}],
  'segments':[{'length':18.0,'mobility':0.85,'delay':0.9,'acceleration':1.2}]}})
c.call('swing',{'op':'put','request':{'id':'swing_ParamLegSway','name':'腿部摆动 ParamLegSway','state':s,'targets':['DeformLegs'],
  'kind':'lateral','parameters':['ParamLegSway'],'magnitude':0.04,'softness':0.8,'parallel':0.3,'physics_enabled':False}})
```
- **swing 的 targets 要写不带前缀的网格名**(`ArtMeshTail`)。写成 `mesh:ArtMeshTail` 会报“目标不存在”,虽然 `workspace_inspect` 返回的就是带前缀的写法。
- PSD2Live 的自动物理只包括前发、后发和果冻眼;尾巴、狐耳、面具流苏都要自己加。
- `tail 1` 对应 `ArtMeshTail2`,导入后先查清楚对应关系再写。

### 4.5 保存与导出(`/workspace/tools/p2l_v3exp.py`)
```python
c.call('project',{'op':'save_as','request':{'path':D+'/<名字>_v3.psd2live','request_id':R(),'project_id':pid,'state':s}})
for tgt,out in [('moc3','export_cubism'),('vtube-studio','export_vtube_studio'),('webm','preview')]:
    c.call('workspace_call',{'operation':'project_export_target','request':{'request_id':R(),'state':s,'target':tgt,'output_directory':D+'/'+out+'_v3tmp'},'wait_ms':30000})
```
- 导出目标:`moc3, cmo3, vtube-studio, psd-pose, p2lrt, web, png-sequence, sprite-sheet, gif, mp4, webm, mov, apng, webp`。moc3 会同时输出 physics3、cdi3、4 个动作(idle/blink/nod/shake)和 4096 图集。
- webm 导出约 1 分钟(其他目标约 1 秒),用 job wait 等它。GIF 很大(澪 idle 12 秒、1024 px 就有 40 MB 以上),**交付用 webm,不要用 GIF**。
- 先导出到 `*_v3tmp` 临时目录,确认没问题后再把 `<名字>_v3.*` 移进正式目录,不要覆盖 v2 的文件。
- VTube Studio 报告会提示“面部追踪只驱动标准参数:20 个里的 15 个”,属于正常现象。
- `.psd2live` 工程文件的权限是 0600,打包前用 `chmod 644` 改一下。

---

## 5. 渲染检查

```bash
# 全身,默认参数
bash /workspace/tools/rv.sh /tmp/v3_full_a '{}'
# 身体 X + 尾巴摆动
bash /workspace/tools/rv.sh /tmp/v3_pose_a '{"ParamBodyAngleX":10,"ParamTailA":1,"ParamTailB":-1,"ParamTailC":0.6}'
# 腿部特写(canvas_rect 视口 left top w h + 长边)
bash /workspace/tools/rv.sh /tmp/v3_legs_a '{"ParamLegSway":1}' 600 1300 900 1772 1400
# 头部特写
bash /workspace/tools/rv.sh /tmp/v3_head_a '{"ParamAngleX":30}' 600 0 850 1000 1200
```
- 输出 `<前缀>_0.png`。**每次换一个前缀**(Read 会缓存同一路径的旧图)。
- `render_model` 的 `viewport` 必须显式给出 `{mode:"canvas_rect",...}`;没给的参数按默认值渲染,不是按当前滑条位置。
- `view op=render_poses` 一次能渲 9 个姿势做对比,不会动用户当前的滑条。
- 全身 3072 px 渲染不到 1 秒,可以反复看细节。
- 必看的姿势:默认;AngleX/Y/Z ±30;BodyAngleX ±10;张嘴(MouthOpenY=1);闭眼;尾巴摆动;腿部摆动;隐藏裙子。要看接缝(领子/脖子/上衣、袖口/手、袜口/腿、裙摆/腿)有没有露底。
- 交付渲染要同时出透明底和白底两版。

---

## 6. 实际用过的提示词(原文)和结果

### 6.1 全身母版(codex,✅ 一次成功)— `/workspace/art/inori/codex_master1.log`
```
Generate ONE full-body anime character illustration with your image generation tool, and save it as /workspace/art/inori/master_1.png (2:3 portrait, as large as possible). Character: a ~18yo fox-ear shrine maiden with near-future techwear accents, strictly FRONT-FACING, standing straight, arms slightly away from the body with palms open, feet together, symmetrical pose, full body head to shoes fully visible, plain pure white background, no shadows on the ground, no text. Design: waist-length white hair with red gradient tips, asymmetric: on the viewer's left a braid hanging over the chest, on the viewer's right a low twin-tail down to the waist; diagonal-parted straight bangs and one small ahoge; white fox ears with pink inner ear (small gold earring on the viewer's right ear); heterochromia: viewer's-left eye gold, viewer's-right eye crimson, long lashes, gentle slightly sly smile; a white-and-red fox half-mask worn on the viewer's right side of the head; red ribbon hairband with a small gold bell on the viewer's left; white modified miko top with red collar and cuffs, thin gold line patterns, red chest cord with a metal ring; two large detached wide white sleeves with red lining; wide red obi sash with a big bow, gold bell and tassel hanging at the side; red-to-white gradient micro pleated skirt with a translucent white tulle overskirt; black over-the-knee socks with red garter straps; white-soled red-strapped platform short boots; black choker with a tiny bell; three fluffy white fox tails with red tips behind her, spread out so each is visible. High-detail cel-shaded Japanese anime style. When done, print the saved path.
```
结果 1024×1536。缺点:分辨率偏低,导致长发和尾巴细节不足;第三条尾巴几乎被挡住。

### 6.2 头部特写(codex,✅ 一次就是正脸)— `/workspace/art/inori/codex_head1.log`
```
Look at the reference image /workspace/art/inori/master_1.png (full-body anime character). Using your image generation/editing tool, create a high-resolution HEAD close-up of the SAME character (head, ears, hair, neck and upper shoulders only, down to the collarbone), and save it as /workspace/art/inori/head_1.png (portrait 3:4, as large as possible). Requirements: STRICTLY front-facing, camera exactly level, head perfectly upright (eye line exactly horizontal), face shape and both fox ears symmetrical about the vertical centerline; keep every design detail identical to the reference: asymmetric hair (viewer's-left braid over the chest, viewer's-right low twin-tail), diagonal-parted bangs, ahoge, heterochromia (viewer's-left eye gold, viewer's-right eye crimson), white fox half-mask on the viewer's right of the head, red ribbon with gold bell on the viewer's left, black choker with tiny bell, gold earring on the viewer's-right ear. More refined facial detail than the reference (eyes with highlights, lashes, eyebrows, nose, small gentle smile). Plain pure white background. Print the saved path when done.
```
对照:澪的特写是在 ChatGPT 网页里做的,没有要求“eye line exactly horizontal”,结果歪了 1.7°(见 1.2);第四版重新生成严格正面的特写时,ChatGPT 生成了两次才得到可用的。**ChatGPT 网页上用的提示词没有保存在 box 上**。

### 6.3 分层通用模板 + 各层描述(codex,`/workspace/tools/ino_gen.py`)
模板(✅ 31 层里 30 层一次成功,`front_hair` 超时后重试成功):
```
Use your image generation/editing tool with the reference image {ref} (open and look at it). Produce ONE image containing ONLY: {part}. Rules: the output canvas has the same aspect ratio and the SAME framing as the reference, and the element must sit at exactly the same position, same size and same scale as in the reference (pixel-aligned, as if everything else were deleted from the same picture). This is a Live2D layer: paint in naturally any part of the element that is hidden behind other things in the reference, so the element is complete. Pure flat chroma-green background #00FF00 everywhere else; no shadows, no gradient, no text, no other characters or objects, do not recolor, keep the exact same art style, colors and details. Save it as {out} (PNG) and print the path.
```
注意:虽然模板里写了 “exactly the same position, same size”,codex **还是会按自己的尺度重绘**(偏移最多约 90 px,缩放 0.6~1.4 倍),所以 3.7 的对齐步骤省不掉。

各类层的 `{part}` 原文(按类型挑代表,完整列表见脚本):
- **后发** `back_hair`:`the hair mass BEHIND the head and shoulders (the long white hair with red gradient tips that lies behind the head, neck and shoulders), no face, no skin, no ears, no bangs, no front locks, no braid, no twin-tail, no mask, no ornaments; fill the area hidden behind the head and neck with continuous hair`
- **脸底层** `face_base`:`the bald face skin only: forehead, temples, cheeks (keep the blush), chin; complete full face oval with the parts hidden by hair filled in; no eyes, no eyebrows, no nose, no mouth, no hair, no ears, no neck, no clothing`(✅ 但被画得过长 → 手工地标做横纵不同比例的缩放)
- **脖子** `neck`:`the neck, collarbone and upper chest skin only, with the neck extended upward as a complete column behind the jaw (flat horizontal top edge hidden behind the chin, soft chin shadow); no face, no hair, no choker, no clothing`(这是吸取澪第五版教训后写的:脖子上缘如果是被下巴切出的 V 形缺口,低头时会露底)
- **眼白** `eye_white`:`only the two eye whites (sclera shapes with their soft shading) of both eyes, no iris, no lashes, no brows`
- **虹膜** `iris`:`only the two irises as COMPLETE circles including the part hidden under the eyelids (viewer's-left gold, viewer's-right crimson), with highlights and pupils, no eye white, no lashes`(✅ 缩放约 0.7,用 ino_align5 找回)
- **睫毛** `eyelash`:`only the upper eyelashes and eyeliner of both eyes (dark), no iris, no eye white, no brows`
- **眉毛** `eyebrow`:`only the two eyebrows, fully visible (including the part covered by bangs), nothing else`
- **嘴** `mouth` / `mouth_open`:`only the closed gentle-smile mouth/lips at the same place, nothing else` / `only an open smiling mouth (teeth and tongue visible), same position, size and style as the closed smile mouth in the reference, nothing else`
- **前发** `front_hair`:`only the front hair: the diagonal-parted bangs and the side locks hanging in front of the face and shoulders, and the hair parting on top; no ahoge, no braid, no twin-tail, no ears, no mask, no ornaments, no face skin; complete strands (parts hidden behind the face are not needed)`(⚠️ 第一次超过 900 s 超时)
- **耳朵** `ear_R`:`the fox ear on the viewer's RIGHT of the head (white fur, red tip, pink inside) including its gold bell earring, complete including the root hidden under hair and mask, nothing else`
- **饰品** `mask`:`only the white-and-red fox half-mask on the viewer's right side of the head with its red tassels and cord, complete including parts hidden by hair`
- **看不见的部件** `tail_C`:`only the third (middle/back) fluffy white fox tail with red tip that is behind the body between the two big tails (mostly hidden in the reference); paint it complete as a full tail in the same style, hanging down, same scale as the other tails, no body`(✅ 能出图,但尺度不对 → 手写矩阵)
- **袖子** `sleeve_L`:`only the large detached wide white sleeve with red lining, gold patterns, red tassels and the cord on the viewer's LEFT arm, complete including the inside hidden by the arm; no arm skin, no hand`
- **手臂** `arm_R`:`only the bare arm (shoulder, upper arm, forearm, open hand) of the viewer's RIGHT arm as skin, complete including the part hidden inside the sleeve and under the strap; no sleeve, no clothing`(❌ 姿势和母版不同 → 改用 arm_L 镜像)
- **上衣** `top`:`only the white modified miko top (bodice) with its red trim, gold patterns, chest cord with ring, black buckled shoulder straps and the bare chest skin inside the neckline, complete; no head, no neck choker, no arms, no sleeves, no skirt, no obi`
- **裙子** `skirt`:`only the red-to-white gradient pleated micro skirt together with its translucent white tulle overskirt (render the tulle as it looks over white), and the red/black garter belts attached to it, complete including the part hidden behind the obi; no legs`
- **袜腿** `legwear`:`only the pair of black over-the-knee stockings with red garter straps and their thigh skin gap (zettai ryouiki skin band at the top), complete full legs including the parts hidden under the skirt and inside the boots; no skirt, no boots`(✅ v1 能出图;v2 起改成“可见像素取自母版 + 遮罩补画”,这张只用来提供轮廓)
- **靴** `boots`:`only the pair of white-soled red-strapped platform short boots with gold tassels, complete including the parts hidden under the stockings; nothing else`

澪(ChatGPT 网页)那一轮,“单独输出腿部皮肤”这一层被拒绝两次,理由分别是“欺诈”和“裸露/性内容”。没有改写提示词绕过,改为从母版取像素(`deliver_full3/PSD2Live_体验笔记.md` 第 5 节)。

### 6.4 遮挡补画(裁切 + 洋红遮罩)v2 通用版 — `/workspace/tools/leg_jobs.py`(✅ 脚、靴、膝盖下层条带都采用了 codex v2 的结果)
```
In this directory there is input.png ({W}x{H} px) and mask.png (white = region to fill). input.png shows {desc}. Visible original artwork pixels are kept; the MAGENTA (#FF00FF) region is the hidden area that must be painted in (occlusion completion / inpainting). The bright green (#00FF00) is flat chroma background and must stay pure #00FF00.
Use your built-in image generation/editing tool to edit input.png: inpaint ONLY the magenta region so it seamlessly continues the existing anime cel-shaded artwork (same colors, shading, line style, lighting), matching the leg/boot anatomy. Do not change any non-magenta pixel, do not move, crop, rescale or reframe; keep exactly the same canvas size {W}x{H} and position. No magenta may remain. No text.
Save the result as output.png in this directory (resize back to exactly {W}x{H} if the generator returns another size). Then stop.
```
`{desc}` 示例:
- foot:`the lower shin, ankle and foot of a leg in a black semi-sheer stocking, as it would look inside a boot (no boot, just stocking-covered leg and foot)`
- boot:`the inner side of a white platform boot with red straps and red/black sole; continue the boot where it was hidden behind the other boot`
- thigh(v2):`the upper thigh of the character's left leg (right side of image): pale anime skin above a black semi-sheer thigh-high stocking with a plain black top band; the area was hidden under a skirt and garter strap`
  → v2 的大腿遮罩只盖到裙下一小段,codex 那张(thigh_R_c1)**顶部是一条直线截断**,v2 交付时大腿还做了底部 40 px 渐隐。用户指出“截断”后才有了 v3。grok 那几张脚被画平,靴子细节变少,没有采用。

### 6.5 大腿 v3(从大腿根开始,单腿)— `leg_thigh3.py` 生成,`legs/jobs3/thigh4_L/prompt.txt`(✅ 最终左大腿用的是 grok 结果 `thigh4_L_g3`)
```
Files here: input.png (360x740) and mask.png (white = area to paint). input.png is a crop of an anime character illustration: the character's left leg (right side of image), front view, in a black semi-sheer thigh-high stocking with pale skin above it; the skirt, garters and the other leg were removed (only this one leg is present). The MAGENTA area is where the upper thigh was hidden. Using your built-in image generation/editing, paint a complete, natural upper thigh inside the magenta area: smooth skin continuing all the way up to the thigh root / hip crease at the top of the magenta region, rounded natural contour, same cel-shaded anime style, lighting and skin tone as the visible skin, continuing the black stocking top band where it was covered. No clothing, no straps, no cut edges, no hard horizontal lines, no fading. Wherever the magenta extends beyond the natural leg silhouette (outside the leg), fill with flat pure #00FF00 green. Do not change non-magenta pixels; same canvas size and framing. Save as output.png in this directory (resize to exactly 360x740). The result must be clean, smooth continuous skin: no dark fragments, straps, patches, cracks or vertical strips, clean inner edge. Then stop.
```
- 前一版 `thigh_L/prompt.txt` 的区别:没有 “the other leg were removed (only this one leg is present)” 和最后一句 “clean, smooth continuous skin…”。那一轮两条腿都在裁切里,codex 的 `thigh_L_c1~c4` **4 次全部被拒(sexual)**;grok 的 `thigh_L_g5/g6/g9` 出了图,`thigh_L_g2` 被内容审核拦下。
- 右大腿:`thigh4_R_g1/g3/g4` 和 `thigh5_R_g1/g2` 出了图,但都有外形凹凸、中间竖棱、残留吊袜带碎片、袜口缺口这些问题 → 没有采用。

### 6.6 吊袜带挂饰处局部修补 — `legs/jobs3/thigh5_L/prompt.txt`(✅ 采用 grok `thigh5_L_g3`)
```
Files here: input.png (360x740) and mask.png (white = area to paint). input.png is a crop of an anime illustration of ONE leg in a black semi-sheer thigh-high stocking with a lace/elastic top band, front view, on flat green. The MAGENTA rectangle covers part of the skin just above the stocking, the stocking top band, and the stocking below it. Using your built-in image generation/editing, inpaint ONLY the magenta pixels so the skin, the stocking top band and the stocking below continue seamlessly from both sides: no charm, no strap, no grey ghost, no fragments, no blur. Do not change non-magenta pixels; same canvas size and framing. The magenta pixels must come from your image generation output (resize to canvas, copy only magenta-position pixels). Save as output.png here (exactly 360x740). Then stop.
```
`thigh5_L_g2` 和 `thigh5_R_g3` 因为 grok 返回 HTTP 402(额度用完)失败。

### 6.7 右大腿带参考图版 — `legs/jobs3/thigh6_R/prompt.txt`(❌ 都没采用,最后改用镜像 `thigh6_R_mirror`)
```
Files here: input.png (360x740), mask.png (white = area to paint) and reference.png. input.png is a crop of an anime illustration of ONE leg (front view) in a black semi-sheer thigh-high stocking with pale skin above, on flat green; skirt, garters and the other leg removed. The MAGENTA area is the hidden upper thigh plus a patch over the stocking top band. reference.png is the finished, approved opposite thigh of the same character, mirrored: match its smooth, rounded, natural thigh outline, soft shading, skin tone and clean continuous stocking top band. Using your built-in image generation/editing, paint a complete natural upper thigh inside the magenta area, running all the way to the top of the magenta region (thigh root): smooth convex outline with no lumps, no vertical ridge, no notches, no cut edges, no fragments; the stocking top band continuous across the patch. Wherever magenta lies outside the natural leg silhouette, fill with flat #00FF00. Do not change non-magenta pixels; same canvas size and framing. The magenta pixels must come from your image generation output (resize to canvas, copy only magenta-position pixels). Save as output.png here (exactly 360x740). Then stop.
```
结果:codex `c1` 被拒(sexual),`c3/c4` 返回 model at capacity,`c2/c5/c6` 出了图但质量不行;grok `g1~g4` **全部 HTTP 402**(“Grok Build usage balance exhausted”,`thigh6_R_g1/grok.log`)。

### 6.8 膝盖接缝 — `legs/jobs3/knee4/prompt.txt`(✅ 采用 grok `knee4_g2`)
```
Files here: input.png (140x590) and mask.png (white = area to paint). input.png is a crop of an anime illustration showing ONE leg (the leg on the right side) in a black semi-sheer stocking, knee and shin, front view, on a flat green background. The MAGENTA pixels are along its inner (left) edge. Using your built-in image generation/editing, inpaint ONLY the magenta pixels as the continuation of this leg's dark black-stocking shading with a clean dark contour edge; no light line, no white specks. Where magenta lies outside the leg silhouette, fill with flat #00FF00. Do not change non-magenta pixels; keep the exact canvas size and framing. Save as output.png here (resize to exactly 140x590). The magenta pixels must come from your image generation/editing tool output (resize to the canvas, then copy only magenta-position pixels). Then stop.
```
早期的 `knee/prompt.txt`(两条腿都在裁切里):codex `knee_c1/c2` 被拒(sexual);grok `knee_g1` 的成品是用代码平滑出来的,作废。

### 6.9 HF Space 编辑(澪那一轮,❌ 不可用)— `/workspace/art/run_edits.sh`
```
bangs|remove the bangs/front hair and side locks, complete the forehead and face behind them, keep everything else identical
noeyes|remove the eyes, leaving blank smooth skin where the eyes were, keep everything else identical
bald|remove all hair, bald head with ears, keep everything else identical
green|change background to flat green #00FF00, keep everything else identical
```
结果(`/workspace/art/edit_try/NOTES.md`):FLUX.1-Kontext-Dev 能匿名使用(30–50 s 一次),但输出固定为 1360×768,而且每个提示词的缩放和平移都不一样,“去刘海”基本没效果;Qwen-Image-Edit-2511-Lightning 会裁中心约 74.5% 再放大;其他 space 报错,或者需要的 GPU 时长超过匿名配额。分层 space(`see-through`、`Qwen-Image-Layered`)几乎每次都提示 “exceeded your ZeroGPU runs limit”(`/workspace/art/queue_log.txt`)。

### 6.10 提示词写法总结
- 一律用 “viewer's left/right” 指方向;用 “ONLY: … no X, no Y” 把不要的部件逐个排除。
- 写清楚画布:“same canvas size and framing / resize to exactly WxH”。
- 补画:洋红 = 要画的地方,绿 = 背景,并写上 “Do not change non-magenta pixels”。
- 防作弊:写上 “The magenta pixels must come from your image generation output (resize to canvas, copy only magenta-position pixels)”。
- 防截断:写上 “all the way up to the thigh root … No cut edges, no hard horizontal lines, no fading”,以及 “Wherever the magenta extends beyond the natural leg silhouette, fill with flat #00FF00”(这样遮罩可以放心画大一些)。
- 补画结果有具体缺陷时,把缺陷写进否定词:“no lumps, no vertical ridge, no notches, no fragments, no grey ghost”。
- 有一侧已经画好时,提供 `reference.png`(镜像后的另一侧)。
- 被内容审核拒绝时**不要改写提示词去绕过**(两个角色都遵守了这一点):换工具(grok),或者改变方案(镜像、取母版像素),然后在交付说明里写清楚。

---

## 7. 出图工具对比(实测)

| | codex exec(内置 image_gen) | grok CLI(`grok -p`) | 内置 GenerateImage | ChatGPT 网页(gpt-image) | HF ZeroGPU Space |
|---|---|---|---|---|---|
| 速度 | 1–3 分钟一张(补画约 1.5 分钟);31 层 8 路并行约 1 小时 | 一个任务 5–25 分钟,会自己反复多轮生成和修正 | 快 | 40–120 秒一张 | 30–50 s(Kontext),5–13 s(Lightning) |
| 构图 / 对齐 | 分层时按自己的尺度重绘(偏移 10–90 px,缩放 0.6–1.4);补画时由它自己贴回原图,误差为 0 | 生成图和输入的宽高比相同,缩放后可见区域平均误差 3.7–8/255,不用再对齐 | **宽高比参数无效**,参考图只起风格提示作用,做不到位置不变的局部编辑,分辨率低,姿势会漂 → **不适合拆层** | 每张的缩放和位置都会漂,同一对话里也会改画布比例,必须自己做地标对齐 | 固定输出尺寸,而且会裁切或缩放 |
| 内容审核 | **严格**:大腿/膝盖相关任务 9 个目录被拒(sexual);只有右大腿出过 2–3 张 | 较宽松:被拦 3 次(thigh_L_g2、thigh_R_g1、thigh4_L_g4) | — | 澪的“腿部皮肤”层被拒两次(欺诈 / 裸露) | — |
| 遵守“只用生成像素” | 基本遵守 | **有时自己写代码补色或模糊**(knee_g1),需要在提示词里明确禁止,并从 `~/.grok/sessions/.../images/` 取原始生成图 | — | — | — |
| 质量 | 分层质量好;补画大腿时外形尚可,但贴回的色块边界明显,还有顶部直线截断 | 左大腿干净、外形自然;右大腿常见外形凹凸、竖棱、残留吊袜带碎片 | — | 编辑效果最好 | 去刘海等操作效果差 |
| 故障 | 高并发时出现 “model is at capacity”;单次超过 900 s 超时 | 额度用完时返回 **HTTP 402**(“Grok Build usage balance exhausted”),之后所有任务都失败 | — | 需要浏览器登录 | “exceeded your ZeroGPU runs limit” |
| 推荐用途 | **母版、头部特写、全部分层、非敏感部位的补画**(默认工具) | codex 被拒的补画(大腿、膝盖);用量要省着点 | 不用 | codex 不可用时的备选 | 不用 |

数据来源:`deliver_inori/体验与建模笔记.md` 的对比表;`deliver_inori_v3/体验与建模笔记.md`;`art/inori/legs/jobs3/*/codex.log|grok.log`(用 grep 统计 sexual/policy/402/capacity);`deliver_full3/PSD2Live_体验笔记.md` 第 4、5 节;`art/edit_try/NOTES.md`。

统计各任务结果的命令:
```bash
cd /workspace/art/<角色>/legs/jobs3; for d in */; do d=${d%/}; o=$([ -f $d/output.png ] && echo OUT || echo --); r=$(cat $d/*.log 2>/dev/null | grep -ioE "sexual|policy|content moderation|402|capacity" | sort | uniq -c | tr '\n' ' '); echo "$d $o $r"; done
```

---

## 8. 交付

### 8.1 交付目录内容(以 `deliver_inori/` 为模板)
```
README.md                      # 版本变更、文件说明、图层表、已知问题、分卷合并方法
体验与建模笔记.md              # 流程、工具对比、PSD2Live 体验问题、已知不足
<名字>_v3.psd2live             # 工程(chmod 644)
<名字>_layers_v3.psd           # 2048x3072 拆层 PSD
export_cubism/<id>_v3.*        # moc3 / model3 / physics3 / cdi3 / 4 个 motion3 / .4096 图集 / report
export_vtube_studio/<id>_v3.*  # 同上 + .vtube.json
preview/<id>_v3.webm           # idle 动作(不要放 GIF)
renders/v3/                    # 01 全身 / 02 姿势 / 03 腿部特写 / 04-08 隐藏裙子等检查图 / 09 膝盖特写,透明底和白底各一份,外加 align_diff_v3.json
source_art/                    # char.md、master_1.png、head_1.png、gen_layers/、legs_v3/(图层 + jobs/ 里选用任务的 input/mask/prompt/output)
pipeline/                      # 本次用到的所有脚本
```
- 旧版本的文件留在原位(v2 和 v3 并存),README 里写清楚每个版本改了什么。

### 8.2 超过 100 MB 时 → 7z 分卷
祈 v3 的包约 296 MB,分成 4 卷:`/workspace/v3_7z/hiakari_inori_v3.7z.001~.004`,每卷 94,371,840 字节(90 MiB)。py7zr 和 multivolumefile 装在 `/tmp/pk` 这个 venv 里(`/tmp` 可能被清掉,没有就重新装):
```bash
python3 -m venv /tmp/pk && /tmp/pk/bin/pip install py7zr multivolumefile
/tmp/pk/bin/python - <<'PY'
import py7zr, multivolumefile
# multivolumefile.open() 默认后缀是 4 位(.0001);要得到 .7z.001 必须直接用 MultiVolume(ext_digits=3)
with multivolumefile.MultiVolume('/workspace/v3_7z/hiakari_inori_v3.7z', mode='wb',
                                 volume=90*1024*1024, ext_digits=3) as vol:
    with py7zr.SevenZipFile(vol, 'w') as z:
        z.writeall('/workspace/deliver_inori', 'hiakari_inori_v3')
PY
ls -l /workspace/v3_7z
```
(`ext_digits` 参数是在 `/tmp/pk/lib/python3.13/site-packages/multivolumefile/__init__.py` 里确认的。)
- 用户那边用 7-Zip 打开 `.7z.001` 就能自动合并解压。
- 更早的版本用的是 zip + `split` 分卷(`hiakari_inori_pkg_v3.zip.part00~03`,合并方法写在 README 末尾:`cat hiakari_inori_pkg_v3.zip.part* > hiakari_inori_pkg_v3.zip`)。Windows 用户用 7z 分卷更方便。

### 8.3 上传与传输
- 上传到 Google Drive:用 `UploadFile`(connection `google-drive`),一卷一卷地传,然后把链接或文件夹发给用户。传之前可以先在 Drive 里建一个版本文件夹。
- 用 `CopyFromBox` 推到用户电脑:**用户电脑离线时会失败**。失败了就改走 Drive,不要反复重试,也不要说成“已经传好了”。
- 最后汇报时给出:每个文件的大小和数量、怎么解压、主要修改点、哪几张渲染图最值得看。

---

## 9. 用户的期望与工作方式

1. **长任务要自己做到底**:用户要的是成品模型,测试 PSD2Live 是次要的。不要做到一半停下来问“要不要继续”,能自己判断的就自己判断,一直做到交付。
2. **没开始的事不要说“已开始”**:只汇报已经实际启动、并且能验证的工作(进程在跑、文件已生成)。后台任务启动后要确认真的跑起来了。
3. **高并行**:生成和补画任务按 8 路左右并行;codex 和 grok 可以同时对同一个任务各出几张,然后挑最好的。
4. **只汇报能看到的结果**:附上渲染图或对比图的路径,让用户能直接打开看;不要只报数字。
5. **用户会放大看细节**:被他指出过的问题有——第一版有接缝、五官细节不够、不是全身;脸歪了;袜子和靴子对不齐;大腿截断/渐隐;膝盖有浅色线。交付前要**自己先按第 11 节查一遍**。
6. 用户的原则:被遮挡部分要由图像生成补全,不要用代码硬切;每条腿单独生成;大腿要从根部画起。实在做不到的地方(比如被内容审核拒绝),要在 README 里**主动说明是怎么处理的**。
7. 要诚实写出已知问题(两个 README 和笔记里都有“已知不足”一节)。
8. 回复用中文,简洁,不堆术语;时间用 Asia/Shanghai 时区。

---

## 10. 坑点清单(按踩到的先后顺序)

| # | 坑 | 正确做法 |
|---|---|---|
| 1 | codex 不加 `< /dev/null` 会一直等 stdin | 命令末尾加 `< /dev/null`;Python 里用 `stdin=subprocess.DEVNULL` |
| 2 | 头部特写本身歪头,放回时又带入 SIFT 求出的旋转 | 提示词里写“eye line exactly horizontal”;拆层前量角度;放回时旋转约等于 0 |
| 3 | 生成的层尺度和位置都会漂 | 逐层配准(3.7),叠图复核,不要只信数字指标 |
| 4 | 低透明度噪点被 PSD2Live 当成整块网格 | `key.py` 去小连通块;检查 alpha 包围盒 |
| 5 | 绿边 | 去绿边;嘴唇和发丝重点看 |
| 6 | 腮红被抠坏 | 不做腮红层,或者白底出图再用正片叠底 |
| 7 | 生成的手臂姿势不对 | 镜像另一侧;澪那种左右比例不一致的情况则分别配准 |
| 8 | 脖子上缘是 V 形缺口,或者脖子补成宽肩 | 提示词要求“延伸到下巴后面的完整圆柱”;用梯形遮罩限制在领口以内 |
| 9 | 大腿截断、渐隐、两条腿画在一起 | 遮罩从大腿根开始;每次只放一条腿;不渐隐;看隐藏裙子的渲染 |
| 10 | 补画工具用代码模糊冒充补画 | 提示词里禁止;从 grok 的 session images 取原始生成图;逐张查看 |
| 11 | codex 拒绝补画大腿 | 换 grok;不要改写提示词绕过;实在不行用镜像或母版像素,并在文档里说明 |
| 12 | grok 额度用完(402) | 大腿这类关键任务优先给 grok,而且尽早做;非敏感任务用 codex |
| 13 | ino_gen 的 ThreadPool 一层超时就整轮中断 | 捕获异常;已存在的文件会跳过,直接重跑即可 |
| 14 | import_psd 后 swing 和物理全没了 | 每次导入后都跑 `p2l_v3.py` 那一段重建 |
| 15 | swing 目标写了 `mesh:` 前缀 | 写纯网格名 `ArtMeshTail` |
| 16 | tail/legwear 的编号和网格名对不上 | 用 `workspace_inspect`(加 query)查出真实网格名 |
| 17 | `workspace_inspect` 用 cursor 翻页 | 用 `offset`/`query` |
| 18 | `wait_ms` 或 `timeout_ms` 超过 30000 报错 | ≤30000,循环等待 |
| 19 | MCP 导入会覆盖 GUI 当前的工程 | 先 save_as;新版本用新文件名 |
| 20 | GUI 进程消失,或卡在恢复对话框 | 按 2.1 的命令重启;`kill -9`;先备份再清 `~/.psd2live/agent-workspaces` |
| 21 | Read 预览看到的是旧图 | 每次换文件名 |
| 22 | GIF 体积巨大 | 交付用 webm |
| 23 | .psd2live 文件权限是 0600 | 打包前 chmod 644 |
| 24 | 工作区被重置,丢了文件 | 每版都备份;重要的中间文件(gen/ keyed/ final/ legs/)也要备份 |
| 25 | multivolumefile 默认后缀是 .0001 | 用 `MultiVolume(..., ext_digits=3)` |
| 26 | 用户电脑离线,CopyFromBox 失败 | 改用 Drive 上传 |
| 27 | 母版上的阴影留在可见像素里,动起来时跟着腿走 | 把投影区域也放进遮罩重画(祈 v3 已对吊袜带和裙摆投影这样处理) |
| 28 | 张嘴闭嘴时出现双线 | 关掉 `mouthOutlineEnabled` |
| 29 | 两侧大腿遮罩互相排除,导致大腿根中间有空隙 | 遮罩内侧要越过分割线,让两层有重叠(祈 v3 的已知问题) |

---

## 11. 交付前 QA 清单(全部打勾才交付)

**美术层**
- [ ] 头部特写的眼线角度 |θ| < 1°;耳朵等高;眼、鼻、嘴在脸的中线上
- [ ] 每层抠图后没有绿边,没有低 alpha 噪点(alpha 包围盒和内容范围相符)
- [ ] 每层叠在母版上检查过(头部各层、手臂、袖子、袜子、靴子),截图存档
- [ ] 腿部 `leg_check` 指标:可见区域内部 p99 ≤ 2,完全一致比例 ≥ 98%,`ov_legs` 差值图在可见区域接近全黑
- [ ] 隐藏裙子后:大腿从根部开始是完整的,没有截断、渐隐、竖棱、凹凸、碎片、缺口;两腿之间没有意外的空隙
- [ ] 只显示腿和靴:袜口、挂饰、膝盖没有浅色线和接缝
- [ ] 脖子延伸到下巴后面,低头时不露底;脖子不在肩头露出来
- [ ] 被遮挡的部分都来自图像生成(没有代码模糊或取色填充);例外写进 README

**PSD 与 PSD2Live**
- [ ] PSD 是 2048×3072,层名符合规范,层的顺序对(眼睛在刘海之上等)
- [ ] 导入后没有 Unknown,左右正确(看 Binding)
- [ ] 尾巴 swing(ParamTailA/B/C)、PhysicsTails、ParamLegSway 都重建了,而且目标网格对应正确(实际渲染摆一下确认)
- [ ] 关掉了 `mouthOutlineEnabled`;张嘴能看到口腔和牙齿;眨眼正常
- [ ] 渲染检查:默认;转头 X/Y/Z;身体摆动;张嘴;闭眼;尾巴摆动;腿部摆动;隐藏裙子 + 摆动;膝盖和头部特写。接缝处都不露底
- [ ] 导出 moc3、vtube-studio、webm 都成功(查看 report.json);文件名带版本号;旧版本没有被覆盖

**交付**
- [ ] README 写清楚:版本变更、文件清单、图层表、已知问题、解压方法
- [ ] 笔记更新了(流程、工具对比、PSD2Live 体验问题)
- [ ] 渲染图透明底和白底各一份
- [ ] 打包前做了备份;超过 100 MB 的包分卷成 `.7z.001…`;上传 Drive 后确认每卷的大小都对
- [ ] 汇报里只写已完成、可查看的内容,附上关键渲染图路径

---

## 12. 两个角色的已知问题

### 12.1 绯灯 祈 v3(`/workspace/deliver_inori/`,41 层)
(来源:`deliver_inori/体验与建模笔记.md`“已知不足”、`deliver_inori_v3/体验与建模笔记.md`)
- 右大腿是左大腿补画结果镜像后再做颜色校正得到的,两侧形状基本对称;右腿外侧靠近袜口处仍然有一个小缺口,袜口挂饰的位置有一处很淡的接缝。
- 两腿之间的大腿根处有空隙(两侧遮罩互相排除),隐藏裙子时能看到。
- 吊袜带和裙摆投影原来所在的皮肤是重画的,隐藏吊袜带后看到的是补画的皮肤,不是母版像素。(较早的 v3 草稿则相反:保留了母版上的投影,隐藏裙子时能看到阴影块。)
- 画面右腿的膝盖上方还有一个很短的浅色小点。
- ParamLegSway 只是腿部整体小幅左右摆动,没有接物理,也没有放进动作。
- grok 额度用完后,右大腿没法再用 grok 补画。
- 隐藏裙子时,膝盖下方两腿之间的缝里能看到后面的尾巴(和母版一致)。
- 吊袜带伸进裙下的部分没有补画(v2 起就是这样)。
- 辫子、双尾、尾巴来自 1024 宽的母版,放大 2 倍后细节比头部差。
- 第三条尾巴是 codex 补画的(母版里几乎看不到),藏在腿后面。
- 领子背面、裙子内衬没有单独补画。
- 没有在 Cubism Editor 和 VTube Studio 里实测。

### 12.2 雾岛 澪 v5(`/workspace/deliver_full3/`,27 层)
(来源:`deliver_full3/PSD2Live_体验笔记.md`、`deliver_full3/README.md`)
- 腿部皮肤层**不是图像生成补全的**(ChatGPT 拒绝了):取自母版,被裙子遮住的约 35 px 和袜口下约 10 px 用相邻像素向外延伸补出,是整个成品里唯一的例外。
- 头部特写和全身母版的发型有细微差别(用了特写的脸和全身的身体)。
- 鼻子高光是一个带描边的菱形,不透明度降到 40% 来弱化。
- 没有腮红层(抠图会抠坏);没有 eye_close 层(眨眼用睫毛形变)。
- 第四版重新生成正面特写时,ChatGPT 改变了脸宽、下巴位置和刘海形状,所以头部层是按眼、嘴、耳的位置逐层缩放放置的,脸底层做了横纵不同比例的缩放;刘海比母版更遮眼,所以眼睛放在前发之上。
- 第五版把脸(脸底层、五官、耳朵)整体放大了 16%,头发大小没变。
- 层数少(27 层):没有拆出头饰、尾巴之类的部件,头发物理只有前发和后发。
- 物理摆动的实际观感没有录屏检查;没有在 Cubism Editor 和 VTube Studio 里实测;预览 GIF 有 42 MB。

---

### 附:关键路径速查
- 角色目录:`/workspace/art/inori/`(master_1.png、head_1.png、gen/、keyed/、aligned3/ aligned5/、headfinal/、hr/、final/、legs/{jobs,jobs3,layers,layers3}、inori_v3.psd)
- 澪的素材:`/workspace/art/`(master.jpg、gpt/、mio.psd、edit_try/)
- 工具:`/workspace/tools/`;Real-ESRGAN 权重:`/workspace/tools/weights/`;venv:`/workspace/tools/venv-sr`、`venv-hf`
- MCP 客户端:`/workspace/notes/mcp_client.py`;工具列表:`/workspace/notes/mcp_tools_list.json`;安装记录:`/workspace/notes/install_log.md`
- 备份:`/workspace/backup_inori_v1/`、`/workspace/backup_v4/`、`/workspace/deliver_full_v3_backup/`
- 分卷:`/workspace/v3_7z/`
