# PSD2Live Examples

[中文](../../README.md) · [日本語](../ja/README.md) · [한국어](../ko/README.md)

[Main project](https://github.com/tsunehimatoi/psd2live) · [Case index](CASES.md) · [Downloads](https://github.com/tsunehimatoi/psd2live-examples/releases) · [Submit a case](https://github.com/tsunehimatoi/psd2live-examples/issues/new/choose) · [Contributing](CONTRIBUTING.md)

Example assets, projects and exported models for PSD2Live, along with production notes, prompts and skills. Download one to reproduce it, and share your own.

## Cases

| Case | Contents | Tags |
| --- | --- | --- |
| [tml](../../cases/tml/README.md) | Layered PSD import, automatic generation and export | Getting started, generation, export |
| [ds](../../cases/ds/README.md) | A complete character with motions and physics | Generation, motion, physics |
| [star_lan](../../cases/star_lan/README.md) | Joint deformation, multiple textures and notes on working with AI | Skeleton, textures, MCP |
| [Hiakari Inori](../../cases/hiakari-inori/README.md) | grok bot + GPT Image: splitting without see-through, complex simulation | Splitting, simulation, grok |
| [Kirishima Mio](../../cases/kirishima-mio/README.md) | The run-up to Hiakari Inori: generated layers, alignment and occlusion fill | Layers, alignment, grok |

See the [case index](CASES.md) for the full list with previews. Case pages are written in the contributor's language.

## Download

Download a zip from [Releases](https://github.com/tsunehimatoi/psd2live-examples/releases) and extract it, or download and verify with the script (Python 3.11+, no third-party packages):

```sh
python scripts/fetch.py --case tml
```

`--all` downloads everything. Files go to `examples/<case ID>/`.

## Contributing

No Git needed: attach an example to a [case submission](https://github.com/tsunehimatoi/psd2live-examples/issues/new/choose) (link large files from cloud storage) and add a sentence or two on what you did and how it turned out; a maintainer arranges and publishes it. Any language is fine, unfinished or failed attempts are welcome, and ads are not accepted.

For pull requests and content rules, see [Contributing](CONTRIBUTING.md).

## Layout

```text
cases/<id>/        one directory per contribution
├── README.md
├── manifest.json  asset manifest (when there is an asset pack)
├── workflow/      methods, scripts and notes
├── prompts/
├── skills/
└── mcp/
scripts/           download, validation, packing and MCP check scripts
```

Create subdirectories as needed; see [Contribution rules](CONTRIBUTING.md#contribution-rules).

## MCP service check

Enable the service under **Tools → MCP…** in PSD2Live, set the endpoint and token as the environment variables `PSD2LIVE_MCP_ENDPOINT` and `PSD2LIVE_MCP_TOKEN`, then run:

```sh
python scripts/mcp_discovery.py
```

It checks initialization, paged tool discovery and a `workspace_list_operations` call. It does not change the project or store the token, and connects only to local endpoints by default. The interface follows the main project's [MCP documentation](https://github.com/tsunehimatoi/psd2live/blob/master/docs/zh/agent/MCP_AUTHORING.md).

## License

Unless marked otherwise, the content of this repository and the Release assets are published under [CC0 1.0](../../LICENSE): free to use, modify and use commercially, with authors and sources kept in each case. Contributions are published this way by default; state any other license when you submit. The main project's software license is unaffected.

<details>
<summary>Technical notes</summary>

- The repository holds only descriptions, manifests and scripts; PSDs, projects and export packs are distributed as versioned Release attachments. The script checks size and SHA-256 against the manifest on download and extraction, and writes to the target directory only when everything passes; archives are cached in `build/example-assets/`.
- The main project has its own lock file and the same entry point (`python tools/examples/fetch.py --case tml`), so asset updates do not change its acceptance inputs automatically.
- Existing exports are for showcase only. Generated results change with versions and settings and are not a fixed visual acceptance baseline.
- Cases are categorized by the manifest's `tags`; assets are not duplicated.
- Regression tests for internal interfaces, sessions, replay and save/restore live in the main repository.

</details>
