# PSD2Live Examples

[中文](../../README.md) · [English](../en/README.md) · [日本語](../ja/README.md)

[메인 프로젝트](https://github.com/tsunehimatoi/psd2live) · [케이스 목록](CASES.md) · [소재 다운로드](https://github.com/tsunehimatoi/psd2live-examples/releases) · [케이스 투고](https://github.com/tsunehimatoi/psd2live-examples/issues/new/choose) · [기여 가이드](CONTRIBUTING.md)

PSD2Live의 예제 소재, 프로젝트, 내보낸 모델과 제작 노트, 프롬프트, Skill을 모았습니다. 내려받으면 그대로 재현할 수 있고, 여러분의 케이스 투고도 환영합니다.

## 케이스

| 케이스 | 내용 | 태그 |
| --- | --- | --- |
| [tml](../../cases/tml/README.md) | 레이어 PSD 가져오기, 자동 생성, 내보내기 | 입문, 생성, 내보내기 |
| [ds](../../cases/ds/README.md) | 모션과 물리가 포함된 완성 캐릭터 | 생성, 모션, 물리 |
| [star_lan](../../cases/star_lan/README.md) | 관절 변형, 다중 텍스처, AI 협업 노트 | 스켈레톤, 텍스처, MCP |
| [히아카리 이노리(Hiakari Inori)](../../cases/hiakari-inori/README.md) | grok bot + GPT Image, see-through 없는 분할과 복잡한 시뮬레이션 | 분할, 시뮬레이션, grok |
| [키리시마 미오(Kirishima Mio)](../../cases/kirishima-mio/README.md) | 히아카리 이노리의 사전 시도: 생성 레이어, 정렬, 가려진 부분 보완 | 레이어, 정렬, grok |

미리보기가 포함된 전체 목록은 [케이스 목록](CASES.md)을 참고하세요. 각 케이스 페이지는 투고자의 언어로 작성되어 있습니다.

## 다운로드

[Releases](https://github.com/tsunehimatoi/psd2live-examples/releases)에서 zip을 내려받아 압축을 풀거나, 스크립트로 다운로드와 검증을 합니다(Python 3.11 이상, 서드파티 라이브러리 불필요):

```sh
python scripts/fetch.py --case tml
```

`--all`로 전부 내려받습니다. 파일은 `examples/<케이스 ID>/`에 저장됩니다.

## 투고

Git은 필요 없습니다. [케이스 투고](https://github.com/tsunehimatoi/psd2live-examples/issues/new/choose)에 예제를 첨부하고(큰 파일은 클라우드 저장소 링크), 무엇을 했고 결과가 어땠는지 한두 문장만 쓰면 메인테이너가 정리해 공개합니다. 언어는 상관없고, 미완성이나 실패한 시도도 환영합니다. 광고는 받지 않습니다.

풀 리퀘스트와 내용 규칙은 [기여 가이드](CONTRIBUTING.md)를 참고하세요.

## 구성

```text
cases/<id>/        투고마다 디렉터리 하나
├── README.md
├── manifest.json  소재 매니페스트(소재 패키지가 있을 때)
├── workflow/      방법, 스크립트, 노트
├── prompts/
├── skills/
└── mcp/
scripts/           다운로드, 검증, 패키징, MCP 점검 스크립트
```

하위 디렉터리는 필요할 때 만듭니다. 자세한 내용은 [투고 규칙](CONTRIBUTING.md#투고-규칙)을 참고하세요.

## MCP 서비스 점검

PSD2Live의 **도구 → MCP…**에서 서비스를 켜고, 엔드포인트와 토큰을 환경 변수 `PSD2LIVE_MCP_ENDPOINT`, `PSD2LIVE_MCP_TOKEN`으로 설정한 뒤 실행합니다:

```sh
python scripts/mcp_discovery.py
```

초기화, 도구 페이지 조회, `workspace_list_operations` 호출을 확인합니다. 프로젝트를 수정하거나 토큰을 저장하지 않으며, 기본적으로 로컬 엔드포인트에만 연결합니다. 인터페이스는 메인 프로젝트의 [MCP 문서](https://github.com/tsunehimatoi/psd2live/blob/master/docs/zh/agent/MCP_AUTHORING.md)를 따릅니다.

## 라이선스

별도 표기가 없는 한 이 저장소의 내용과 Release 소재는 [CC0 1.0](../../LICENSE)으로 공개됩니다. 자유롭게 사용, 수정, 상업적으로 이용할 수 있으며 작성자와 출처는 각 케이스에 남겨 둡니다. 투고는 기본적으로 이 방식으로 공개되며, 다른 라이선스를 원하면 투고할 때 밝혀 주세요. 메인 프로젝트의 소프트웨어 라이선스에는 영향이 없습니다.

<details>
<summary>기술 메모</summary>

- 저장소에는 설명, 매니페스트, 스크립트만 두고 PSD, 프로젝트, 내보내기 패키지 같은 큰 파일은 버전이 붙은 Release 첨부 파일로 배포합니다. 스크립트는 다운로드와 압축 해제 시 매니페스트의 크기와 SHA-256을 대조하고, 모두 통과해야만 대상 디렉터리에 씁니다. 압축 파일은 `build/example-assets/`에 캐시됩니다.
- 메인 프로젝트에는 별도의 잠금 파일과 같은 진입점(`python tools/examples/fetch.py --case tml`)이 있어, 소재가 갱신되어도 메인 프로젝트의 검수 입력은 자동으로 바뀌지 않습니다.
- 기존 내보내기 결과는 전시용입니다. 생성 결과는 버전과 설정에 따라 달라지며 고정된 시각 검수 기준이 아닙니다.
- 케이스 분류는 매니페스트의 `tags`로 하며 소재를 복제하지 않습니다.
- 내부 인터페이스, 세션, 재생, 저장과 복원의 회귀 테스트는 메인 저장소에 있습니다.

</details>
