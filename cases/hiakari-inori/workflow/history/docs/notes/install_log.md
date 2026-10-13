> 历史资料：保留当时的描述与版本信息，文件列表可能与本次导入不一致。以案例首页及 manifest.json 为准。

# PSD2Live v3.4.2 安装与启动日志(Linux box, x86_64, Debian 13 trixie)

记录时间:2026-10-12 00:12 – 00:18 (CST)。所有操作均在 box 上完成。

## 0. 环境确认(00:12:48)
- 架构 x86_64;系统 Debian GNU/Linux 13 (trixie)。
- `java` 未安装(符合预期)——**但不需要**:发布包 tar.gz 自带 jlink 精简 Java 运行时(`PSD2Live/lib/runtime`)。
- box 已有 X 显示:`DISPLAY=:10`(`xdpyinfo -display :10` 正常,另有 :1/:8/:9 的 Xvfb + x11vnc)。已有 ffmpeg、git、curl、Xvfb。
- 提示:`/workspace/psd2live/` 在我动手前就已存在——是一份 2026-10-10 克隆的仓库(含 .git,HEAD `ebb01220`),并非空目录。tar 解压后新增的目录是 `/workspace/psd2live/PSD2Live/`,与仓库文件并存、互不覆盖(git status 仅显示 `?? PSD2Live/`)。【体验不佳/需注意:目标目录不干净】

## 1. 下载(00:12)
命令:`curl -fL -o psd2live.tar.gz https://github.com/tsunehimatoi/psd2live/releases/download/v3.4.2/PSD2Live-3.4.2-linux-x64.tar.gz`
- 结果:HTTP 200,96,573,207 字节(≈92 MB),耗时约 3.6 秒(≈25 MB/s)。无问题。

## 2. 解压(00:12–00:13)
命令:`tar xzf psd2live.tar.gz -C /workspace/psd2live`
- 耗时 1.4 秒。tar 内仅 257 个条目,全部位于 `PSD2Live/` 下:`bin/PSD2Live`(启动器)、`lib/app/*.jar` + `PSD2Live.cfg`、`lib/runtime`(自带 JRE)、`lib/libapplauncher.so`、`lib/PSD2Live.png`。
- 解压后占用约 475 MB(含目录里原有的仓库文件)。
- 启动器:`/workspace/psd2live/PSD2Live/bin/PSD2Live`;主类 `io.github.psd2live.MainKt`。
- `ldd` 检查:没有缺失的共享库("not found" 为空)。

## 3. 克隆源码仓库只为读文档(00:12–00:13)
命令:`git clone https://github.com/tsunehimatoi/psd2live /workspace/psd2live-src`
- 约 5 秒,1218 个文件。仓库内含示例 PSD(`examples/ds|tml|star_lan`)与中/英/日/韩文档(`docs/zh|en|ja|ko`)。
- 注意:release tar.gz **不含** README/docs/示例PSD,必须靠仓库获取。【不便】

## 4. GUI 启动(00:13:28)
命令:`cd /workspace/psd2live && DISPLAY=:10 nohup PSD2Live/bin/PSD2Live > /workspace/notes/psd2live_gui.log 2>&1 &`(后台,不阻塞)
- 无需安装任何依赖(未装 GTK/ffmpeg 以外的东西;box 已有 ffmpeg)。
- 约 2 秒出现窗口,约 6 秒可交互;进程 PID 65378,窗口标题 "PSD2Live — Unsaved project",1280x820,**在 box 桌面 :10 上可见**(用 PIL ImageGrab 截图确认,截图 `/workspace/notes/gui_start.png`)。
- 控制台输出的警告/报错:
  1. `dbind-WARNING: AT-SPI: Error retrieving accessibility bus address ... org.a11y.Bus was not provided` —— 无障碍总线缺失,无害。
  2. `[SKIKO] warn: Fallback to next API` / `org.jetbrains.skiko.RenderException: Cannot create Linux GL context` —— **【问题/体验不佳】** Skiko 在 Xvfb 下创建不了 GL 上下文,自动回退到软件渲染。GUI 日志面板确认:`Window renderer: SOFTWARE_FAST`、`Editing canvas renderer: software, GPU unavailable (The window draws with LinuxSoftwareRedrawer)`。功能可用,只是纯 CPU 绘制,画布较慢(未做性能测量)。
- 用户界面是**英文**(GUI 无 `--lang` 参数时按系统语言;CLI 才有 `--lang`)。欢迎页"最近打开"里有 `/workspace/p2l-test/smoke.psd2live` 和 `/workspace/psd2live/examples/ds.psd`,说明此前别的 agent 用过。
- MCP 端点随 GUI 启动自动监听:日志 `AI endpoint running: http://127.0.0.1:23871/mcp (core)`;`ss -ltn` 确认 23871 在监听。

## 5. CLI 无头试跑(00:14–00:15)
- `PSD2Live/bin/PSD2Live --help` 0.4 秒返回帮助(版本 3.4.2)。`PSD2Live/bin/PSD2Live targets` 列出 17 个导出目标。
- 命令:`PSD2Live/bin/PSD2Live --lang zh --input /workspace/psd2live-src/examples/ds/psd-input/ds.psd --output /workspace/notes/cli_out/ds`
- **成功,退出码 0,总耗时 4.9 秒**(与 GUI 同时在跑,互不影响;CLI 不需要 DISPLAY)。输出 12 个文件:`ds.moc3`(295,360 B)、`ds.cmo3`(5.0 MB)、`ds.can3`、`ds.model3.json`、`ds.cdi3.json`、`ds.physics3.json`、4 个 motion3.json(idle/blink/nod/shake)、`ds.4096/texture_00.png`、`ds.psd2live.json`。
- 警告(无害):`检测到同名图层:ears, eyebrow, handwear, eyewhite, irides, eyelash;已通过稳定图层 ID 区分`。
- 生成摘要(来自 ds.psd2live.json):26 层 → 26 drawable、30 deformer、20 参数、1 张 4096 贴图集。
- 注意:CLI 只出导出文件,**不产生可继续编辑的 .psd2live 工程**。

## 6. MCP 无头试跑(00:15–00:17)
- 直接 curl 无令牌 → `HTTP 401, WWW-Authenticate: Bearer`。令牌不在文档里,默认随机生成,保存在 Java Preferences。
- 【问题/体验不佳】**没有命令行/配置文件的方式查看令牌**,只能在 GUI「Tools → MCP…」对话框里看(默认是掩码,「Show」显示、「Copy」复制)。box 上没有 xclip,无法读剪贴板;肉眼从截图抄 24 位随机串又容易把 l/I 看混。我的做法:在该对话框里**把令牌手动改成自己填的值**(文档允许,32–256 位字母数字 - _),点「Apply and restart」。注意:输入框里 Ctrl+A 全选无效(xdotool 下),要用 Home → Shift+End → Delete;令牌不足 32 位会报红字 "The token must be 32–256 letters, digits, - or _" 且 Apply 灰掉。
- 本次 MCP 令牌已被我改为 `[REDACTED_MCP_TOKEN]`(仅 127.0.0.1 可用;如需恢复随机令牌,在该对话框点 Regenerate)。测试客户端:`/workspace/notes/mcp_client.py`。
- 握手成功:`serverInfo = psd2live 3.4.2`,精简工具集 25 个工具(列表见 `/workspace/notes/mcp_tools_list.json`)。
- 通过 MCP 完成:`project`(op=import_psd) 导入 ds.psd(1.9 秒)→ `workspace_overview`(26 层,20 参数,画布 1280×1280)→ `project`(op=export_model) 导出到 `/workspace/notes/mcp_out/ds/`(1.6 秒,与 CLI 结果文件名/字节数一致:moc3 295,360 B)→ `project`(op=save_as) 保存工程 `/workspace/notes/mcp_out/ds_mcp.psd2live` → `project`(op=export_target, target=png-sequence, clip=idle, size=256) 导出 40 帧到 `/workspace/notes/mcp_out/ds_png/`。
- 小坑:`wait_ms` 最大 30000,我第一次填 60000 报 `invalid_request: expected 0..30000`。
- MCP 导入后,GUI 窗口同步显示该模型(层级树、图层表、画布里蓝发女仆角色),截图 `/workspace/notes/gui_ds_loaded.png`。说明 MCP 与 GUI 共用同一个工作区,**脚本操作会改动正在运行的 GUI 工程**(这次它把 GUI 的"未保存工程"换成了 ds_mcp.psd2live)。

## 7. 总结:体验不佳 / 需注意清单
1. GUI 在 Xvfb 上无 GL → 软件渲染(能用但慢);Cubism Native 预览依赖 GLX,同样会回退到内置渲染。
2. MCP 令牌拿不到(只能 GUI 对话框),无头场景下不方便;建议首次启动后在对话框里自行设置令牌。
3. release tar.gz 里没有文档和示例 PSD,要另外 clone 仓库。
4. `/workspace/psd2live` 目录原本已有仓库克隆,与解压出来的 `PSD2Live/` 混在一起;启动器真实路径是 `/workspace/psd2live/PSD2Live/bin/PSD2Live`(不是 `/workspace/psd2live/bin/...`)。
5. GUI 无 `--lang` 参数,界面按系统语言(此处英文);CLI 的 `--lang` 只影响日志。
6. 同名图层会触发警告(靠稳定 ID 区分,不影响结果)。
7. GUI 进程仍在运行:PID 65378(`ps aux | grep PSD2Live`),如需关闭 `kill 65378`。
