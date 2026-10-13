# 기여 가이드

[中文](../../CONTRIBUTING.md) · [English](../en/CONTRIBUTING.md) · [日本語](../ja/CONTRIBUTING.md)

PSD2Live와 관련된 소재, 프로젝트, 제작 흐름, 프롬프트, Skill, MCP 시나리오를 환영합니다. 미완성이나 실패한 시도도 참고할 가치가 있습니다.

**최소 요건**: 예제 하나(소재, 프로젝트, 모델, 프롬프트 등)와 의미 있는 설명 한두 문장. 무엇을 했는지, 결과가 어땠는지, 어디서 막혔는지 등입니다. 아래의 나머지 내용은 모두 선택 사항입니다.

**언어 무관**: 투고는 어떤 언어로 해도 되며 번역은 필요 없습니다.

**광고 금지**: 홍보 링크, 유입을 위한 연락처, 유료 서비스나 상품 홍보를 넣지 마세요. 작성자 표기와 필요한 소재 출처는 광고가 아닙니다.

## 투고 방법

- **Issue**: Git이 필요 없습니다. [케이스 투고](https://github.com/tsunehimatoi/psd2live-examples/issues/new/choose) 양식을 작성하면 메인테이너가 아래 규칙에 따라 정리해 공개합니다.
- **풀 리퀘스트**: 아래 규칙에 따라 디렉터리를 만들고, 제출 전에 로컬 점검을 실행합니다.

## 투고 규칙

### 구성

투고는 각각 `cases/` 아래의 디렉터리 하나이며, 관련 내용을 모두 그 안에 둡니다. 하위 디렉터리는 필요할 때 만듭니다:

```text
cases/
└── <id>/
    ├── README.md         진입 페이지(필수)
    ├── manifest.json     소재 매니페스트(소재 패키지가 있을 때. 메인테이너가 채울 수 있음)
    ├── preview.webp      미리보기(선택. GIF도 가능)
    ├── workflow/         방법, 스크립트, 노트
    ├── prompts/          프롬프트
    ├── skills/           Skill. 호스트가 요구하는 기본 구조 그대로
    └── mcp/              MCP 호출 시나리오
```

- `<id>`에는 소문자, 숫자, 하이픈, 밑줄을 씁니다. 예: `kirishima-mio`.
- 프롬프트나 Skill만 공유해도 투고 한 건입니다. `README.md`와 해당 하위 디렉터리만 있으면 됩니다.
- 여러 케이스가 공유하는 내용은 그중 한 케이스에 두고, 다른 케이스에서는 상대 링크로 참조합니다. 복사하지 마세요.
- [케이스 목록](../../cases/README.md)과 첫 페이지의 케이스 표에 각각 항목을 추가합니다(메인테이너가 해도 됩니다). 다른 언어 버전은 메인테이너가 동기화합니다.

### README

의미 있는 설명 한두 문장이면 충분합니다. 아래 항목은 필요에 따라 작성합니다:

| 항목 | 설명 |
| --- | --- |
| 개요 | 무엇을 하는지, 결과는 어떤지. [미리보기](#미리보기)와 함께 |
| 환경 | PSD2Live 버전. AI를 쓸 때는 클라이언트와 모델 |
| 사용법 | 입력, 단계, 예상 결과 |
| 알려진 문제 | 부족한 점, 실패한 시도 |
| 출처 | 작성자, 소재 출처. CC0가 아니면 라이선스 |

검증하지 않은 내용은 맨 앞에 "미검증"이라고 표시합니다. 예시는 [tml](../../cases/tml/README.md)을 참고하세요.

`mcp/` 시나리오에는 소재 버전, psd2live commit, 초기 상태, 호출, 단언도 적습니다. 쓰기 작업이 있는 시나리오는 별도의 작업 공간과 출력 디렉터리를 씁니다. Agent를 한 번 실행한 결과는 회귀 테스트를 대신하지 않습니다.

### 파일

- Git 안의 파일 하나는 5 MB를 넘지 않아야 하며, `.psd`, `.cmo3`, `.moc3`, `.zip` 같은 바이너리는 커밋하지 않습니다. 소재, 프로젝트, 내보내기 패키지는 Release로 배포하므로 풀 리퀘스트에는 다운로드 링크만 붙이면 됩니다.
- 토큰, 세션 ID, 계정 정보, 개인 경로를 지우고, 독점 SDK 바이너리는 올리지 마세요.

### 미리보기

결과가 잘 보이면 충분하며 형식과 크기는 자유입니다. 정지 이미지, GIF, WebP 모두 됩니다. PSD2Live의 **파일 → 다른 형식으로 내보내기 → GIF…**로 만들 수 있습니다. 내보낸 모델이 있으면 메인 프로젝트에서 빌드한 Cubism 미리보기 라이브러리로 직접 렌더링할 수도 있습니다:

```sh
python scripts/render_preview.py <모델>.model3.json cases/<id>/preview.webp --renderer <live2d_renderer가 있는 디렉터리>
```

Pillow와 libwebp를 지원하는 ffmpeg가 필요합니다. 미리보기 라이브러리 빌드는 메인 프로젝트의 `native/live2d_renderer/README.md`를 참고하세요.

### 소재 매니페스트

소재 패키지가 있는 투고에는 `manifest.json`이 필요하며, `catalog.json`에 등록하고 `scripts/fixtures.lock.json`을 갱신합니다. 익숙하지 않으면 README와 소재 링크만 제출하면 메인테이너가 채워 넣습니다.

- 필수: `schema_version: 1`, `id`, `version`, `title`, `description`, `author`, `tags`, `source`, `compatibility`. `license`의 기본값은 `CC0-1.0`.
- `source`: Git 출처는 `commit`에 전체 SHA를 고정합니다. 로컬에서 가져온 경우 `kind: local-import`로 하고 `name`, 원본 파일 목록의 `inventory_sha256`, `imported_on`을 기록합니다. Git 출처를 지어내지 마세요.
- `archive`에는 HTTPS URL, `size_bytes`, `sha256`을, `files`에는 파일마다 `path`, `size_bytes`, `sha256`을 기록하며 경로는 `<id>/`로 시작합니다. 기존 매니페스트를 참고하세요.

## 라이선스

라이선스를 밝히지 않은 투고는 [CC0 1.0](../../LICENSE)으로 공개되며, 작성자와 출처는 README나 매니페스트에 남깁니다. 투고하면 해당 내용을 공유할 권리가 있음을 확인한 것으로 봅니다.

## 로컬 점검

```sh
python scripts/validate.py
python -m unittest discover -s scripts -p 'test_*.py'
```

CI에서도 같은 점검을 실행합니다.

## 소재 공개(메인테이너)

```sh
python scripts/pack.py tml --source-repository ../psd2live --release-tag assets-v1
python scripts/validate.py
```

- 패키저는 케이스 안에서 Git이 추적하는 소재만 포함하며 Markdown은 포함하지 않습니다.
- `build/assets/` 아래의 패키지를 해당 Release에 올립니다. 소재가 바뀌면 케이스 버전을 올리고 새 첨부 파일 주소를 쓰며, 기존 첨부 파일은 덮어쓰지 않습니다.
- GitHub 첨부 파일 크기 제한을 넘는 소재는 외부 HTTPS 저장소를 쓸 수 있으며, 매니페스트 형식은 그대로입니다.
- 메인 프로젝트는 검토를 거친 뒤 별도의 풀 리퀘스트로만 소재 잠금 파일을 갱신합니다.
