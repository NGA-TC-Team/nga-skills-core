---
name: nexttitan
description: |
  Next Titan 커뮤니티 사이트의 콘텐츠와 댓글을 외부 API로 관리하는 스킬.
  콘텐츠 조회·생성·수정·예약발행·취소, 댓글 조회·작성·수정·삭제를 처리한다.

  트리거 상황:
  - "넥스트 타이탄에 [콘텐츠] 올려줘 / 등록해줘 / 작성해줘"
  - "넥스트 타이탄 콘텐츠 수정 / 삭제 / 예약"
  - "넥스트 타이탄 댓글 달아줘 / 지워줘"
  - "Next Titan API로 [작업]"
  - "NT 콘텐츠 자동화", "사이트에 글 발행"
  - "에이전트 스킬 [등록 / 추가 / 한글 번역 추가]" — agentSkill 타입 처리
  - SKILL.md 마크다운을 받아 사이트에 등록해달라는 요청
  - 콘텐츠 자동화, 발행 스케줄링, 커뮤니티 운영 관련 요청

  이 스킬은 Next Titan 운영 자동화와 관련된 모든 요청에서 사용해야 한다.
  명시적으로 "넥스트 타이탄"을 언급하지 않더라도, 콘텐츠 자동 발행·스케줄링·커뮤니티 관리 맥락이면 적극적으로 활용한다.
---

# Next Titan 스킬

Next Titan 외부 API를 통해 콘텐츠와 댓글을 관리한다.

---

## 0. 시작 전 필수 확인: API 키 및 베이스 URL 설정

**스킬을 실행하기 전에 반드시 아래 두 가지를 확인한다.**

```bash
echo $NEXT_TITAN_API_KEY
echo $NEXT_TITAN_BASE_URL
```

둘 중 하나라도 비어 있으면 아래 안내를 사용자에게 보여준 뒤 중단한다:

> **환경 변수 설정이 필요합니다.**
>
> `~/.zshrc` 또는 `~/.bashrc`에 아래 두 줄을 추가하세요:
>
> ```bash
> export NEXT_TITAN_API_KEY="ntk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
> export NEXT_TITAN_BASE_URL="https://your-nexttitan-domain.com"
> ```
>
> 추가 후 셸을 재시작하거나 `source ~/.zshrc` (또는 `~/.bashrc`)를 실행하세요.
> API 키는 Next Titan 관리자 대시보드에서 발급받을 수 있습니다.

두 값 모두 확인된 경우에만 이후 단계로 진행한다.

---

## 1. 실행 모드 감지 및 시작 절차

### 직접 대화 세션 (loop/schedule 없이 호출된 경우)

스킬이 트리거되면 **반드시 먼저 메뉴를 제시하고 사용자의 선택을 기다린다.** 어떤 작업을 할지 추측해서 먼저 실행하지 않는다.

사용자에게 다음 형식으로 물어본다:

```
Next Titan에서 어떤 작업을 할까요?

[콘텐츠]
1. 콘텐츠 목록 조회
2. 콘텐츠 상세 조회
3. 콘텐츠 생성
4. 콘텐츠 수정
5. 예약 발행 설정
6. 예약 발행 취소

[에이전트 스킬]
7. 에이전트 스킬 등록 (SKILL.md 마크다운 → 콘텐츠)
8. 에이전트 스킬 한글 번역 추가/수정 (bodyKo)

[댓글]
9. 댓글 목록 조회
10. 댓글 작성
11. 댓글 수정
12. 댓글 삭제

번호 또는 원하는 작업을 말씀해 주세요.
```

선택을 받은 뒤 섹션 3의 "최소 질문 원칙"에 따라 필요한 정보만 추가로 묻고 API를 호출한다.

### 자동화 세션 (loop 또는 schedule 스킬을 통해 호출된 경우)

loop/schedule로 실행되는 경우 대화형 메뉴 없이 바로 지정된 작업을 수행한다.
**모든 파일 입출력은 현재 열린 프로젝트 디렉토리 아래 `contents/` 폴더를 사용한다.**

```bash
# 세션 시작 시 contents/ 폴더가 없으면 자동 생성
mkdir -p ./contents
```

파일 용도별 위치:
- 발행할 콘텐츠 초안: `./contents/drafts/`
- API 조회 결과 저장: `./contents/fetched/`
- 발행 완료 로그: `./contents/published/`

파일명 형식: `YYYYMMDD_HHMMSS_[타입]_[제목슬러그].md` 또는 `.json`

---

## 2. API 호출 규칙

모든 요청에 공통 헤더를 포함한다:

```bash
BASE="${NEXT_TITAN_BASE_URL}"
KEY="${NEXT_TITAN_API_KEY}"

# GET
curl -s -H "X-API-KEY: $KEY" "$BASE/api/external/contents?..."

# POST / PATCH
curl -s -X POST \
  -H "X-API-KEY: $KEY" \
  -H "Content-Type: application/json" \
  -d '{...}' \
  "$BASE/api/external/contents/create"
```

응답 코드별 처리:
- `401` → API 키 누락 또는 유효하지 않음 → 키 재확인 안내
- `403` → 사용 중지된 키 → 관리자에게 키 활성화 요청 안내
- `4xx/5xx` → 오류 메시지와 함께 원인 분석 후 사용자에게 보고

---

## 3. 최소 질문 원칙 (핵심)

**사용자가 직접 입력해야 하는 콘텐츠 정보만 질문한다.** 나머지 필드는 스펙에 맞는 합리적인 기본값으로 자동 채운다.

### 사용자에게 반드시 물어볼 것 (콘텐츠 생성 기준)

| 항목 | 이유 |
|---|---|
| **제목** | 고유한 내용, 자동 생성 불가 |
| **본문** | 핵심 창작물, 자동 생성 불가 |
| **콘텐츠 타입** | 요청에서 명확하지 않을 때만 질문 |

타입별로 **의미 없이는 채울 수 없는 전용 필드**만 추가로 질문한다. 예:
- `guide` → `difficulty` (어느 수준 독자를 대상으로 하나요?)
- `event` → `eventStartAt`, `eventEndAt`, `location`
- `resource` → `url`
- `prompt` → `promptType`
- `agentSkill` → `bodyKo` (한글 번역 본문, 있으면), `skillVersion` (있으면)

### 자동으로 채울 것 (묻지 않음)

| 필드 | 자동 기본값 |
|---|---|
| `status` | **반드시 페이로드에 명시한다.** "올려줘 / 발행해줘 / 등록해줘 / 업로드 / 게시 / 포스팅" → `"published"`. "초안으로 / 임시저장 / 나중에 발행" → `"draft"`. "예약" → `"draft"` + `scheduledPublishAt`. 의도가 불분명할 때만 1회 질문한다. **status 누락 = 서버 default `draft` = 카드 날짜 미표시.** |
| `sort` | `-createdAt` |
| `page` | `1` |
| `limit` | `20` |
| `isSolved` | `false` |
| `isPaidPrompt` | `false` |
| `discussionStatus` | `open` |
| `galleryLayout` | `grid` |
| `maxParticipants` | `0` (무제한) |
| `scheduledPublishAt` 포맷 | 사용자가 날짜/시간만 말하면 → `ISO 8601 +09:00` 자동 변환 |
| `summary` | 본문 앞 150자로 자동 생성 (사용자가 제공하지 않은 경우) |
| `tags` | 본문 내용 기반으로 제안 → 확인 요청 (단, 사용자가 "알아서 해줘"라고 하면 확인 없이 사용) |

### 날짜 필드 주의 (중요: 카드에 날짜가 안 뜨는 문제 방지)

공개 페이지의 발행일 라벨은 `publishedAt` 기준이다. **`publishedAt`이 비어 있으면 카드/리스트에서 날짜가 표시되지 않는다.** 자주 발생하는 누락 원인과 회피 규칙:

1. **CREATE 시 status 누락 금지** — `status`를 안 보내면 서버는 `draft`로 저장하고 `publishedAt`은 NULL이다. "올려줘 / 등록 / 발행 / 게시 / 업로드 / 포스팅" 중 하나라도 사용자가 말했다면, **CREATE 페이로드에 반드시 `"status": "published"`를 명시**한다.
2. **PATCH로 발행 전환 시에도 status 명시** — draft를 published로 바꿀 때도 `"status": "published"`를 PATCH 본문에 포함해야 한다. 이때 기존 `publishedAt`이 NULL이면 API가 현재 시각으로 자동 세팅한다.
3. **예약 발행** — `scheduledPublishAt`만 세팅하고 status는 자동으로 `draft`가 된다. 크론이 발행 시점에 `publishedAt`을 채운다.

#### 발행 검증 (모든 발행 작업 직후 필수 실행)

CREATE/PATCH로 published 상태를 의도한 직후 반드시 다음을 호출해 `publishedAt`을 확인한다:

```bash
curl -s -H "X-API-KEY: $NEXT_TITAN_API_KEY" \
  "$NEXT_TITAN_BASE_URL/api/external/contents/read?id={id}" \
  | jq '{id, status, publishedAt}'
```

- `publishedAt`이 `null`이고 `status`가 `published`면 즉시 보정 PATCH를 보낸다:

```bash
curl -s -X PATCH \
  -H "X-API-KEY: $NEXT_TITAN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"id": <id>, "status": "published"}' \
  "$NEXT_TITAN_BASE_URL/api/external/contents/update"
```

- 보정 후 다시 read 호출로 `publishedAt`이 채워졌는지 확인한 뒤 출력 형식의 결과 메시지를 사용자에게 보여준다.

### 사용자 재정의 허용

사용자가 특정 필드를 직접 지정하고 싶다고 하면 언제든지 받아들인다.
"태그를 `AI, n8n`으로 해줘", "상태를 바로 published로 해줘" 같은 요청이면 그 값을 그대로 사용한다.
스펙에 맞지 않는 값이면 교정 후 확인을 구한다.

---

## 4. 콘텐츠 API

### 콘텐츠 목록 조회

```
GET /api/external/contents
```

| 파라미터 | 기본값 | 설명 |
|---|---|---|
| `type` | (없음) | 콘텐츠 타입 필터 |
| `category` | (없음) | 카테고리 ID |
| `tag` | (없음) | 태그 (예: `AI`) |
| `from` / `to` | (없음) | ISO 8601 생성일 범위 |
| `sort` | `-createdAt` | 정렬 |
| `page` | `1` | 페이지 |
| `limit` | `20` | 최대 `100` |

타입별 서브카테고리 파라미터:
- `guide` → `difficulty`: `beginner | intermediate | advanced`
- `toolIntro` → `toolIntroCategory`: `aiChatbot | imageGen | videoGen | musicGen | coding | productivity | marketing | other`
- `workflow` → `platform`: `chatgpt | claude | n8n | zapier | other`
- `column` → `columnCategory`: `aiBusiness | aiTool | trend`
- `resource` → `resourceType`: `tool | article | video | repository | course | other`

`type=agentSkill`로 list 조회 시 응답 항목에 `skillVersion`이 포함된다 (값이 있을 때).

### 콘텐츠 상세 조회

```
GET /api/external/contents/read?id={id}
```

응답에는 공통 `markdown` 외에 타입별 전용 필드가 추가로 포함된다.
`agentSkill`인 경우 `markdownKo` (한글 번역 마크다운, 없으면 `null`)와 `skillVersion`, `skillAuthorHandle`, `skillIconColor`가 함께 반환된다.

### 콘텐츠 생성

```
POST /api/external/contents/create
```

공통 필드 (전체 스펙):

| 필드 | 필수 | 자동/수동 |
|---|---|---|
| `title` | ✅ | 수동 |
| `type` | ✅ | 수동 |
| `body` | | 수동 (Markdown 문자열 가능) |
| `summary` | | 자동 (본문 앞 150자) |
| `status` | ✅ (의도가 발행이면 필수) | "올려줘/발행/포스팅" → `"published"`, "초안" → `"draft"` — 페이로드에 반드시 명시 (섹션 3 "날짜 필드 주의" 참고) |
| `tags` | | 자동 제안 후 확인 |
| `category` | | 필요 시만 질문 |
| `featuredImage` | | 필요 시만 질문 |
| `scheduledPublishAt` | | 예약 발행 요청 시만 |

### 콘텐츠 수정

```
PATCH /api/external/contents/update
```

`id` (필수) + 변경할 필드만 포함한다.

### 예약 발행 설정

```
POST /api/external/contents/schedule
{ "id": 123, "scheduledPublishAt": "2026-04-01T09:00:00+09:00" }
```

사용자가 "4월 1일 오전 9시"처럼 자연어로 말해도 ISO 8601 KST 형식으로 자동 변환한다.

### 예약 발행 취소

```
POST /api/external/contents/schedule/cancel
{ "id": 123 }
```

---

## 5. 댓글 API

| 작업 | 엔드포인트 | 수동 입력 |
|---|---|---|
| 목록 조회 | `GET /api/external/comments?contentId={id}` | 콘텐츠 ID |
| 작성 | `POST /api/external/comments/create` | 콘텐츠 ID, 댓글 본문 |
| 수정 | `POST /api/external/comments/update` | 댓글 ID, 수정 본문 |
| 삭제 | `POST /api/external/comments/delete` | 댓글 ID |

---

## 6. 지원 콘텐츠 타입 및 전용 필드

| 타입 | 설명 | 수동 입력 전용 필드 |
|---|---|---|
| `post` | 게시글 | - |
| `guide` | 가이드 | `difficulty` |
| `resource` | 리소스 | `url`, `resourceType` |
| `event` | 이벤트 | `eventStartAt`, `eventEndAt`, `location`, `eventMode`, `registrationUrl` |
| `question` | 질문 | - (`isSolved` 자동 `false`) |
| `discussion` | 토론 | - (`discussionStatus` 자동 `open`) |
| `gallery` | 갤러리 | `images` (미디어 ID 목록) |
| `faq` | FAQ | `answer`, `faqCategory` |
| `changelog` | 변경 로그 | `version`, `changeType` |
| `column` | 칼럼 | `columnCategory` |
| `caseStudy` | 성공 사례 | `companyOrPerson`, `achievement` |
| `workflow` | 워크플로우 | `platform`, `workflowFileUrl` |
| `toolIntro` | 툴 소개 | `toolLandingUrl`, `toolIntroCategory` |
| `prompt` | 프롬프트 | `promptType` |
| `announcement` | 공지사항 | `announcementSubtype` |
| `showOff` | 자랑하기 | - |
| `greeting` | 가입인사 | - |
| `agentSkill` | 에이전트 스킬 | `bodyKo` (한글 번역 본문, 마크다운 문자열도 가능), `skillVersion`, `skillAuthorHandle`, `skillIconColor` (`emerald \| sky \| amber \| orange \| violet \| rose`) |

#### `agentSkill` 처리 규칙

- 본문 `body`는 SKILL.md 원문(영문 또는 원어). 마크다운 문자열을 보내면 자동으로 Lexical JSON으로 변환된다.
- `bodyKo`는 한글 번역 본문. 마크다운 문자열도 동일하게 자동 변환된다. 없으면 상세 페이지에서 "한글 번역" 탭이 비활성화된다.
- `skillVersion`은 제목 옆 뱃지로 노출된다. 예: `v2.1.1`.
- `skillAuthorHandle`이 있으면 리스트/카드의 `@핸들`로 사용된다 (없으면 작성자 정보 fallback).
- `skillIconColor`는 6개 옵션 중 하나. 비우면 기본 `sky`.

생성 예시:

```json
{
  "title": "Senior Devops",
  "type": "agentSkill",
  "summary": "Comprehensive DevOps skill for CI/CD ...",
  "body": "# Senior Devops\n\nComplete toolkit ...",
  "bodyKo": "# 시니어 데브옵스\n\n현대적인 도구 ...",
  "skillVersion": "v2.1.1",
  "skillAuthorHandle": "alirezarezvani",
  "skillIconColor": "emerald",
  "tags": ["devops", "cicd"],
  "status": "published"
}
```

---

## 7. 출력 형식

작업 완료 후 항상 아래 형식으로 결과를 요약한다:

```
✅ 완료: [작업 설명]
- 콘텐츠 ID: 123
- 제목: "..."
- 상태: draft / published / scheduled
- 예약 발행: 2026-04-01 09:00 KST (있을 경우)
- URL: {NEXT_TITAN_BASE_URL}/.../{slug} (slug 알 경우)
```

자동화 세션(loop/schedule)에서는 추가로 결과를 `./contents/published/YYYYMMDD_HHMMSS.json`에 저장한다.

오류 발생 시:

```
❌ 오류: [HTTP 상태 코드] [오류 메시지]
- 원인: ...
- 조치: ...
```
