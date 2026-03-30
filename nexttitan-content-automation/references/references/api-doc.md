# Next Titan External API

개요

Next Titan External API는 `API KEY` 인증 방식으로 댓글과 콘텐츠 리소스에 접근할 수 있는 REST API입니다.  
모든 요청은 사용량이 자동으로 기록되며, 관리자 대시보드에서 확인할 수 있습니다.

인증

모든 요청에 `X-API-KEY` 헤더가 필수입니다.

```http
X-API-KEY: ntk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

상태 코드별 인증 오류:

`401` - 헤더 누락 또는 유효하지 않은 키
`403` - 사용 중지된 키

---

콘텐츠 API

`GET /api/external/contents`

발행된 콘텐츠 목록을 조회합니다.

쿼리 파라미터

`type` (`string`, 선택) - 콘텐츠 타입 필터. 지원 타입 목록 참고
`category` (`number`, 선택) - 카테고리 ID 필터
`tag` (`string`, 선택) - 태그 필터. 예: `tag=AI`
`from` (`ISO 8601`, 선택) - 생성일 시작
`to` (`ISO 8601`, 선택) - 생성일 종료
`sort` (`string`, 기본값: `-createdAt`) - `-createdAt | createdAt | -publishedAt | publishedAt | -viewCount | viewCount | -likeCount | likeCount`
`page` (`number`, 기본값: `1`)
`limit` (`number`, 기본값: `20`, 최대: `100`)

서브카테고리 필터

해당 `type`과 함께 사용합니다.

`difficulty` (`string`) - `guide` 타입. `beginner | intermediate | advanced`
`toolIntroCategory` (`string`) - `toolIntro` 타입. `aiChatbot | imageGen | videoGen | musicGen | coding | productivity | marketing | other`
`platform` (`string`) - `workflow` 타입. `chatgpt | claude | n8n | zapier | other`
`columnCategory` (`string`) - `column` 타입. `aiBusiness | aiTool | trend`
`resourceType` (`string`) - `resource` 타입. `tool | article | video | repository | course | other`

응답 필드

각 항목:

`id`
`title`
`type`
`summary`
`slug`
`status`
`category` (`id`)
`featuredImage` (`id`)
`tags` (`string[]`)
`viewCount`
`likeCount`
`commentCount`
`publishedAt`
`createdAt`

---

`GET /api/external/contents/read`

콘텐츠 본문과 타입별 메타데이터를 반환합니다.

쿼리 파라미터

`id` (`number`, 필수) - 콘텐츠 ID

응답 필드

공통:

`id`
`title`
`type`
`summary`
`markdown`
`slug`
`status`
`category` (`{ id, name }`)
`featuredImage` (`{ id, url, alt }`)
`tags` (`string[]`)
`viewCount`
`likeCount`
`commentCount`
`publishedAt`
`createdAt`

타입별 전용 필드도 함께 반환됩니다.  
예: `difficulty`, `url`, `eventStartAt` 등

---

`POST /api/external/contents/create`

콘텐츠를 등록합니다. `API KEY`에 사용자가 할당되어 있어야 합니다.

공통 필드

`title` (`string`, 필수) - 제목
`type` (`string`, 필수) - 콘텐츠 타입. 지원 타입 목록 참고
`summary` (`string`, 선택) - 요약. 최대 `300`자
`body` (`Lexical JSON | string`, 선택) - 본문  
  `string`을 보내면 Markdown으로 처리되어 자동으로 Lexical JSON으로 변환됩니다.
`status` (`string`, 선택) - `draft | published | archived`
  - 기본값: `draft`
`category` (`number`, 선택) - 카테고리 ID
`featuredImage` (`number`, 선택) - 대표 이미지 미디어 ID
`tags` (`string[]`, 선택) - 태그 문자열 배열. 예: `["AI", "GPT"]`
`scheduledPublishAt` (`ISO 8601`, 선택) - 예약 발행 일시
  - 값이 있으면 자동으로 `draft` 상태로 저장됩니다.

---

`PATCH /api/external/contents/update`

콘텐츠를 수정합니다. `API KEY`에 할당된 사용자가 작성한 콘텐츠만 수정할 수 있습니다.

공통 필드

`id` (`number`, 필수) - 수정할 콘텐츠 ID
`title` (`string`, 선택) - 제목
`type` (`string`, 선택) - 콘텐츠 타입
`summary` (`string`, 선택) - 요약
`body` (`Lexical JSON | string`, 선택) - 본문
  - `string`이면 Markdown으로 처리되어 자동 변환됩니다.
`status` (`string`, 선택) - `draft | published | archived`
`category` (`number | null`, 선택) - 카테고리 ID
`featuredImage` (`number | null`, 선택) - 대표 이미지 미디어 ID
`tags` (`string[]`, 선택) - 태그 배열
`scheduledPublishAt` (`ISO 8601 | null`, 선택) - 예약 발행 일시
  - 값 지정 시 예약 발행 설정
  - `null` 지정 시 예약 해제

타입별 전용 필드도 동일하게 수정 가능합니다.

---

`POST /api/external/contents/schedule`

콘텐츠 발행을 예약합니다. `API KEY`에 할당된 사용자가 작성한 콘텐츠만 예약할 수 있습니다.

요청 필드

`id` (`number`, 필수) - 콘텐츠 ID
`scheduledPublishAt` (`ISO 8601`, 필수) - 예약 발행 일시

동작

콘텐츠 상태를 자동으로 `draft`로 변경합니다.
`publishedAt`은 `null`로 초기화됩니다.
예약 시점이 되면 예약 발행 작업이 자동으로 콘텐츠를 발행합니다.

---

`POST /api/external/contents/schedule/cancel`

콘텐츠 예약 발행을 취소합니다. `API KEY`에 할당된 사용자가 작성한 콘텐츠만 취소할 수 있습니다.

요청 필드

`id` (`number`, 필수) - 콘텐츠 ID

동작

`scheduledPublishAt` 값을 `null`로 변경합니다.

---

지원 콘텐츠 타입 및 타입별 전용 필드

`post` - 게시글

타입 전용 필드 없음. 공통 필드만 사용합니다.

`guide` - 가이드

`difficulty` (`string`) - `beginner | intermediate | advanced`
`estimatedReadTime` (`number`) - 예상 소요 시간(분)
`prerequisites` (`number[]`) - 선행 가이드 콘텐츠 ID 배열

`resource` - 리소스

`url` (`string`) - 외부 링크 URL
`resourceType` (`string`) - `tool | article | video | repository | course | other`

`event` - 이벤트

`eventStartAt` (`ISO 8601`) - 이벤트 시작 일시
`eventEndAt` (`ISO 8601`) - 이벤트 종료 일시
`location` (`string`) - 장소 또는 온라인 플랫폼명
`eventMode` (`string`) - `online | offline | hybrid`
`registrationUrl` (`string`) - 참가 신청 링크
`maxParticipants` (`number`) - 최대 참가 인원. `0`은 무제한

`question` - 질문

`isSolved` (`boolean`) - 해결 여부. 기본값: `false`

`discussion` - 토론

`discussionStatus` (`string`) - `open | closed | pinned`

`gallery` - 갤러리

`galleryLayout` (`string`) - `grid | masonry | slideshow`
`images` (`array`) - 이미지 목록
  - `image` (`number`, 필수) - 미디어 ID
  - `caption` (`string`, 선택) - 캡션

`faq` - FAQ

`answer` (`Lexical JSON`, 선택) - FAQ 답변
`order` (`number`) - 표시 순서
`faqCategory` (`string`) - FAQ 분류명

`changelog` - 변경 로그

`version` (`string`) - 버전명
`changeType` (`string[]`) - `feature | improvement | bugfix | policy | deprecation`

`column` - 칼럼

`columnCategory` (`string`) - `aiBusiness | aiTool | trend`

`caseStudy` - 성공 사례

`companyOrPerson` (`string`) - 기업 또는 인물명
`achievement` (`string`) - 핵심 성과 한 문장 요약
`testimonial` (`string`) - 추천사 또는 소감

`workflow` - 워크플로우

`platform` (`string`) - `chatgpt | claude | n8n | zapier | other`
`workflowFileUrl` (`string`) - 워크플로우 파일 다운로드 URL

`toolIntro` - 툴 소개

`toolLandingUrl` (`string`) - 툴 랜딩 페이지 URL
`toolIntroCategory` (`string`) - `aiChatbot | imageGen | videoGen | musicGen | coding | productivity | marketing | other`
`toolIconName` (`string`) - LobeHub Icons 아이콘명. 예: `OpenAI`, `Claude`

`prompt` - 프롬프트

`promptType` (`string`) - `text | imageGen | videoGen | musicGen`
`isPaidPrompt` (`boolean`) - 유료 여부. 기본값: `false`
`promptPrice` (`number`) - 유료 프롬프트 가격(원)

`announcement` - 공지사항

`announcementSubtype` (`string`) - `notice | mustRead`

`showOff` - 자랑하기

현재 외부 API에서는 공통 필드 중심으로 사용합니다.

`greeting` - 가입인사

현재 외부 API에서는 공통 필드 중심으로 사용합니다.

---

댓글 API

`GET /api/external/comments`

댓글 목록을 조회합니다.

쿼리 파라미터

`contentId` (`number`, 필수) - 콘텐츠 ID
`page` (`number`, 기본값: `1`)
`limit` (`number`, 기본값: `20`, 최대: `100`)

---

`POST /api/external/comments/create`

댓글을 작성합니다. `API KEY`에 사용자가 할당되어 있어야 합니다.

요청 필드

`contentId` (`number`, 필수) - 댓글을 달 콘텐츠 ID
`bodyMarkdown` (`string`, 필수) - 댓글 본문(Markdown)

---

`POST /api/external/comments/update`

댓글을 수정합니다.

요청 필드

`id` (`number`, 필수) - 수정할 댓글 ID
`bodyMarkdown` (`string`, 필수) - 수정할 본문(Markdown)

---

`POST /api/external/comments/delete`

댓글을 삭제합니다. `API KEY`에 할당된 사용자가 작성한 댓글만 삭제 가능합니다.

요청 필드

`id` (`number`, 필수) - 삭제할 댓글 ID

---

요청 예시

콘텐츠 생성: Markdown 본문

```json
{
  "title": "AI 자동화 시작 가이드",
  "type": "guide",
  "summary": "초보자를 위한 AI 자동화 입문 가이드",
  "body": "# AI 자동화 시작하기\n\n이 문서는 **Markdown** 으로 작성되었습니다.\n\n- n8n 설치\n- 워크플로우 만들기\n- 테스트하기",
  "status": "draft",
  "tags": ["AI", "Automation"],
  "difficulty": "beginner",
  "estimatedReadTime": 10
}
```

콘텐츠 수정

```json
{
  "id": 123,
  "title": "수정된 제목",
  "body": "## 수정된 본문\n\n발행 후에도 수정 가능합니다."
}
```

예약 발행 설정

```json
{
  "id": 123,
  "scheduledPublishAt": "2026-03-18T09:00:00+09:00"
}
```

예약 발행 취소

```json
{
  "id": 123
}
```

