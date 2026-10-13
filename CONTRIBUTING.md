# 分享案例、素材与工作流

## 投稿方式

可以提交 PR，也可以在 Issue 中提供素材链接、使用步骤和效果。大文件交给维护者发布到 Release，不直接加入 Git。建议先提交一个可以复现的完整案例。

未单独标注许可证的投稿默认按 CC0 1.0 发布。投稿者须有权提交并按所选方式发布这些内容；另有许可时在说明与清单中明确列出。保留原作者与来源信息，不上传令牌、个人会话数据或专有 SDK 二进制。

## 案例内容

1. 在 `cases/<id>/` 下创建 `README.md` 和 `manifest.json`。ID 使用小写字母、数字、短横线或下划线。
2. README 写清问题、输入、操作步骤、预期效果、已知问题，以及 psd2live 版本；Agent 案例还记录客户端、模型、Prompt 和 Skill 版本。
3. 清单写入 `schema_version: 1`、`id`、`version`、`title`、`description`、`author`、`tags`、`source` 和 `compatibility`。`source.commit` 固定完整来源 commit；`license` 缺省为 `CC0-1.0`。
4. 素材包中的路径以 `<id>/` 开始。`archive` 记录 HTTPS URL、`size_bytes` 与 `sha256`；`files` 逐项记录 `path`、`size_bytes` 与 `sha256`。参考已有案例的清单。
5. 在 `catalog.json` 注册案例，更新 `scripts/fixtures.lock.json`。维护者可使用 `scripts/pack.py` 打包已跟踪的素材并生成清单字段。

案例可以包含 `prompts/`、`skills/`、`scenarios/`。通用内容放在根目录对应分类下；Skill 保留其宿主需要的原生格式，并说明适用客户端、前置条件和兼容版本。

## 发布素材

维护者从明确的源仓库和案例目录打包，例如：

```sh
python scripts/pack.py tml --source-repository ../psd2live --release-tag assets-v1
python scripts/validate.py
```

打包器只读取指定案例中 Git 已跟踪的资产，不包含 Markdown；说明以案例 README 为准。上传 `build/assets/` 下的包到对应 Release。每次素材变化递增案例版本，并使用新的附件地址，避免覆盖既有附件。

单个 Release 附件必须符合 GitHub 的大小限制。更大的素材可以使用外部 HTTPS 存储，清单格式不变。

## 验证与验收

```sh
python scripts/validate.py
python -m unittest discover -s scripts -p 'test_*.py'
```

目录 CI 校验案例清单、锁文件一致性，并阻止模型和大二进制进入 Git。Release 附件在下载时再次检查。

固定 MCP 调用场景注明输入与断言；Agent 自由执行场景注明模型与运行结果，不能把一次体验等同于稳定的产品回归测试。主项目仅在审核后通过单独 PR 更新所采用的素材锁文件。
