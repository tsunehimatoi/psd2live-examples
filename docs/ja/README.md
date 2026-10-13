# PSD2Live Examples

[中文](../../README.md) · [English](../en/README.md) · [한국어](../ko/README.md)

[本体プロジェクト](https://github.com/tsunehimatoi/psd2live) · [ケース一覧](CASES.md) · [素材のダウンロード](https://github.com/tsunehimatoi/psd2live-examples/releases) · [ケース投稿](https://github.com/tsunehimatoi/psd2live-examples/issues/new/choose) · [投稿ガイド](CONTRIBUTING.md)

PSD2Live のサンプル素材、プロジェクト、書き出したモデル、制作ノート、プロンプト、Skill をまとめています。ダウンロードすればそのまま再現でき、あなたのケースの投稿も歓迎します。

## ケース

| ケース | 内容 | タグ |
| --- | --- | --- |
| [tml](../../cases/tml/README.md) | レイヤー分け PSD の読み込み、自動生成、書き出し | 入門、生成、書き出し |
| [ds](../../cases/ds/README.md) | モーションと物理を含む完成キャラクター | 生成、モーション、物理 |
| [star_lan](../../cases/star_lan/README.md) | 関節の変形、複数テクスチャ、AI との協働ノート | スケルトン、テクスチャ、MCP |
| [緋灯祈（Hiakari Inori）](../../cases/hiakari-inori/README.md) | grok bot + GPT Image、see-through なしの分割と複雑なシミュレーション | 分割、シミュレーション、grok |
| [霧島澪（Kirishima Mio）](../../cases/kirishima-mio/README.md) | 緋灯祈の前段の試み：生成レイヤー、位置合わせ、隠れ部分の補完 | レイヤー、位置合わせ、grok |

プレビュー付きの一覧は [ケース一覧](CASES.md) を参照してください。各ケースのページは投稿者の言語で書かれています。

## ダウンロード

[Releases](https://github.com/tsunehimatoi/psd2live-examples/releases) から zip をダウンロードして展開するか、スクリプトでダウンロードと検証を行います（Python 3.11 以上、サードパーティのライブラリ不要）：

```sh
python scripts/fetch.py --case tml
```

`--all` ですべてをダウンロードします。ファイルは `examples/<ケース ID>/` に書き込まれます。

## 投稿

Git は不要です：[ケース投稿](https://github.com/tsunehimatoi/psd2live-examples/issues/new/choose) にサンプルを添付し（大きなファイルはクラウドストレージのリンク）、何をしてどうなったかを一、二文書くだけで、メンテナーが整理して公開します。言語は問わず、未完成や失敗の試みも歓迎します。広告は受け付けません。

プルリクエストと内容のルールは [投稿ガイド](CONTRIBUTING.md) を参照してください。

## 構成

```text
cases/<id>/        投稿ごとに 1 ディレクトリ
├── README.md
├── manifest.json  素材マニフェスト（素材パックがある場合）
├── workflow/      手法、スクリプト、ノート
├── prompts/
├── skills/
└── mcp/
scripts/           ダウンロード、検証、パッケージ化、MCP チェックのスクリプト
```

サブディレクトリは必要に応じて作成します。詳しくは [投稿ルール](CONTRIBUTING.md#投稿ルール) を参照してください。

## MCP サービスのチェック

PSD2Live の **ツール → MCP…** でサービスを有効にし、エンドポイントとトークンを環境変数 `PSD2LIVE_MCP_ENDPOINT`、`PSD2LIVE_MCP_TOKEN` に設定して実行します：

```sh
python scripts/mcp_discovery.py
```

初期化、ツールのページング取得、`workspace_list_operations` の呼び出しを確認します。プロジェクトは変更せず、トークンも保存せず、既定ではローカルのエンドポイントにのみ接続します。インターフェースは本体プロジェクトの [MCP ドキュメント](https://github.com/tsunehimatoi/psd2live/blob/master/docs/zh/agent/MCP_AUTHORING.md) に従います。

## ライセンス

特に記載がない限り、このリポジトリの内容と Release の素材は [CC0 1.0](../../LICENSE) で公開されています。自由に利用、改変、商用利用でき、作者と出典は各ケースに残しています。投稿は既定でこの方式で公開されます。別のライセンスを希望する場合は投稿時に明記してください。本体プロジェクトのソフトウェアライセンスには影響しません。

<details>
<summary>技術メモ</summary>

- リポジトリには説明、マニフェスト、スクリプトのみを置き、PSD、プロジェクト、書き出しパックなどの大きなファイルはバージョン付きの Release 添付ファイルで配布します。スクリプトはダウンロード時と展開時にマニフェストのサイズと SHA-256 を照合し、すべて通った場合にのみ書き込みます。アーカイブは `build/example-assets/` にキャッシュされます。
- 本体プロジェクトには独自のロックファイルと同じ入口（`python tools/examples/fetch.py --case tml`）があり、素材を更新しても本体の受け入れ入力は自動では変わりません。
- 既存の書き出しは展示用です。生成結果はバージョンや設定によって変わり、固定の視覚的な受け入れ基準ではありません。
- ケースの分類はマニフェストの `tags` で行い、素材は複製しません。
- 内部インターフェース、セッション、リプレイ、保存と復元の回帰テストは本体リポジトリにあります。

</details>
