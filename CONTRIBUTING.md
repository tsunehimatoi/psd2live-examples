# 投稿指南

欢迎分享与 PSD2Live 相关的素材、工程、制作流程、Prompt、Skill 和 MCP 场景。未完成或失败的尝试同样有参考价值。

## 投稿方式

- **Issue**：无需 Git。在 [案例投稿](https://github.com/tsunehimatoi/psd2live-examples/issues/new/choose) 中按表单填写，维护者按下方规范整理后发布。
- **PR**：按下方规范新建目录，提交前运行本地检查。

## 投稿规范

### 目录

每份投稿是 `cases/` 下的一个目录，相关内容都放在里面，按需创建子目录：

```text
cases/
└── <id>/
    ├── README.md         入口说明（必需）
    ├── manifest.json     素材清单（有素材包时必需）
    ├── preview.webp      预览图（可选，GIF 亦可）
    ├── workflow/         方法、脚本与经验
    ├── prompts/          Prompt
    ├── skills/           Skill，保留宿主所需的原生结构
    └── mcp/              MCP 调用场景
```

- `<id>` 使用小写字母、数字、短横线或下划线，例如 `kirishima-mio`。
- 只分享 Prompt 或 Skill 也是一份投稿，目录里放 `README.md` 和对应子目录即可。
- 多个案例共用的内容放在其中一个案例下，其他案例用相对链接引用，不要复制。

### README

写清以下内容，无关项可省略：

| 项目 | 说明 |
| --- | --- |
| 简介 | 做什么，效果如何，附[预览图](#预览图) |
| 环境 | PSD2Live 版本；使用 AI 时注明客户端与模型 |
| 用法 | 输入、步骤、预期结果 |
| 已知问题 | 效果不足、失败的尝试 |
| 来源 | 作者、素材来源；非 CC0 时注明许可 |

未实测的内容在开头标注“未验证”。可参考 [tml](cases/tml/README.md)。

`mcp/` 场景另注明素材版本、psd2live commit、前置状态、调用与断言，写入类场景使用独立工作区和输出目录。单次 Agent 体验不等同于回归测试。

### 文件

- Git 中单个文件不超过 5 MB，不提交 `.psd`、`.cmo3`、`.moc3`、`.zip` 等二进制。素材、工程和导出包通过 Release 分发，PR 中附下载链接即可。
- 移除令牌、会话 ID、账号信息和私人路径；不上传专有 SDK 二进制。

### 预览图

可在 PSD2Live 中通过“文件 → 导出为 → GIF…”生成。有导出模型时，也可用主项目编译的 Cubism 预览库直接渲染，得到与素材包一致、规格统一（320×480、15 fps、物理开启）的动图：

```sh
python scripts/render_preview.py <模型>.model3.json cases/<id>/preview.webp --renderer <live2d_renderer 所在目录>
```

需要 Pillow 和带 libwebp 的 ffmpeg；预览库的编译见主项目 `native/live2d_renderer/README.md`。

### 素材清单

有素材包的投稿需要 `manifest.json`，并在 `catalog.json` 注册、更新 `scripts/fixtures.lock.json`。不熟悉可只提交 README 和素材链接，由维护者补全。

- 必填：`schema_version: 1`、`id`、`version`、`title`、`description`、`author`、`tags`、`source`、`compatibility`。`license` 缺省为 `CC0-1.0`。
- `source`：Git 来源用 `commit` 固定完整 SHA；本地导入用 `kind: local-import`，记录 `name`、原文件清单的 `inventory_sha256` 和 `imported_on`，不虚构 Git 来源。
- `archive` 记录 HTTPS URL、`size_bytes`、`sha256`；`files` 逐项记录 `path`、`size_bytes`、`sha256`，路径以 `<id>/` 开头。参考已有清单。

## 许可

未单独注明的投稿按 [CC0 1.0](LICENSE) 发布，作者与来源保留在 README 或清单中。投稿即确认你有权分享这些内容。

## 本地检查

```sh
python scripts/validate.py
python -m unittest discover -s scripts -p 'test_*.py'
```

CI 执行相同检查。

## 发布素材（维护者）

```sh
python scripts/pack.py tml --source-repository ../psd2live --release-tag assets-v1
python scripts/validate.py
```

- 打包器只收录案例中 Git 已跟踪的资产，不含 Markdown。
- 上传 `build/assets/` 下的包到对应 Release。素材变化时递增案例版本并使用新附件地址，不覆盖既有附件。
- 超出 GitHub 附件大小限制的素材可使用外部 HTTPS 存储，清单格式不变。
- 主项目仅在审核后通过单独 PR 更新其素材锁文件。
