# Contributing

[中文](../../CONTRIBUTING.md) · [日本語](../ja/CONTRIBUTING.md) · [한국어](../ko/CONTRIBUTING.md)

Assets, projects, workflows, prompts, skills and MCP scenarios related to PSD2Live are all welcome. Unfinished or failed attempts are useful too.

**Minimum**: one example (assets, a project, a model, a prompt…) plus a sentence or two that says something useful, such as what you did, how it turned out or what tripped you up. Everything else below is optional.

**Any language**: contributions may be in any language; no translation needed.

**No ads**: no promotional links, contact details for drawing traffic, paid services or product promotion. Author credits and necessary asset sources are not ads.

## How to contribute

- **Issue**: no Git needed. Fill in the [case submission](https://github.com/tsunehimatoi/psd2live-examples/issues/new/choose) form; a maintainer arranges it according to the rules below and publishes it.
- **Pull request**: create the directory as described below and run the local checks before submitting.

## Contribution rules

### Layout

Each contribution is one directory under `cases/` holding everything related to it; create subdirectories as needed:

```text
cases/
└── <id>/
    ├── README.md         entry page (required)
    ├── manifest.json     asset manifest (with an asset pack; a maintainer can fill it in)
    ├── preview.webp      preview (optional; GIF also fine)
    ├── workflow/         methods, scripts and notes
    ├── prompts/          prompts
    ├── skills/           skills, in the native layout their host expects
    └── mcp/              MCP call scenarios
```

- `<id>` uses lowercase letters, digits, hyphens or underscores, e.g. `kirishima-mio`.
- Sharing just a prompt or a skill is a contribution too: a `README.md` and the matching subdirectory are enough.
- Content shared by several cases lives under one of them; the others link to it with relative links instead of copying it.
- Add an entry to the [case index](../../cases/README.md) and to the case table on the home page (a maintainer can do this); maintainers keep the other languages in sync.

### README

A sentence or two that says something useful is enough. Fill in any of the following as needed:

| Item | Description |
| --- | --- |
| Summary | What it does and how it turned out, with a [preview](#preview) |
| Environment | PSD2Live version; client and model when AI is involved |
| Usage | Inputs, steps, expected result |
| Known issues | Shortcomings, failed attempts |
| Source | Author, asset sources; license if not CC0 |

Mark untested content as "unverified" at the top. See [tml](../../cases/tml/README.md) for an example.

`mcp/` scenarios also state the asset version, psd2live commit, initial state, calls and assertions; scenarios that write use a separate workspace and output directory. A single agent run is not a regression test.

### Files

- No single file in Git may exceed 5 MB, and binaries such as `.psd`, `.cmo3`, `.moc3` and `.zip` are not committed. Assets, projects and export packs are distributed through Releases; a download link in the pull request is enough.
- Remove tokens, session IDs, account details and private paths; do not upload proprietary SDK binaries.

### Preview

Anything that shows the result clearly will do; format and size are up to you: a still image, GIF or WebP. You can create one in PSD2Live with **File → Export as → GIF…**. With an exported model you can also render it directly with the Cubism preview bridge built from the main project:

```sh
python scripts/render_preview.py <model>.model3.json cases/<id>/preview.webp --renderer <directory containing live2d_renderer>
```

This needs Pillow and ffmpeg with libwebp; see the main project's `native/live2d_renderer/README.md` for building the bridge.

### Asset manifest

Contributions with an asset pack need a `manifest.json`, registered in `catalog.json` with `scripts/fixtures.lock.json` updated. If you are not familiar with this, submit just the README and the asset link and a maintainer will complete it.

- Required: `schema_version: 1`, `id`, `version`, `title`, `description`, `author`, `tags`, `source`, `compatibility`. `license` defaults to `CC0-1.0`.
- `source`: a Git source pins the full SHA in `commit`; a local import uses `kind: local-import` and records `name`, the source inventory's `inventory_sha256` and `imported_on`, without inventing a Git source.
- `archive` records the HTTPS URL, `size_bytes` and `sha256`; `files` lists each `path`, `size_bytes` and `sha256`, with paths starting with `<id>/`. Follow an existing manifest.

## License

Contributions without a stated license are published under [CC0 1.0](../../LICENSE), with authors and sources kept in the README or manifest. By contributing you confirm you have the right to share the content.

## Local checks

```sh
python scripts/validate.py
python -m unittest discover -s scripts -p 'test_*.py'
```

CI runs the same checks.

## Publishing assets (maintainers)

```sh
python scripts/pack.py tml --source-repository ../psd2live --release-tag assets-v1
python scripts/validate.py
```

- The packer includes only the Git-tracked assets of the case, without Markdown.
- Upload the packs under `build/assets/` to the matching Release. When assets change, bump the case version and use a new attachment URL; never overwrite an existing attachment.
- Assets beyond GitHub's attachment size limit may use external HTTPS storage; the manifest format stays the same.
- The main project updates its asset lock file only after review, in a separate pull request.
