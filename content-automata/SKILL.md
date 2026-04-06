---
name: content-automata
description: >
  AI·자동화 분야 콘텐츠 자동 수집·분류·초안 작성·이메일 전송·쓰레드 발행 파이프라인.
  웹(TestingCatalog, GeekNews), SNS(Threads, X), 뉴스레터(Gmail)에서 콘텐츠를 병렬 수집하고,
  콘텐츠 풀을 형성한 뒤, 페르소나 기반 쓰레드 초안 7개를 작성하여 이메일로 보고한다.
  /content-automata publish로 쓰레드 직접 발행도 지원한다.
  트리거: 콘텐츠 자동화, 콘텐츠 수집, 쓰레드 초안, AI 뉴스 수집, content automata,
  콘텐츠 파이프라인, 뉴스 큐레이션, 쓰레드 발행, 콘텐츠 풀, 쓰레드 예약 발행
---

# content-automata — AI 콘텐츠 자동화 파이프라인

다채널 소스에서 AI·자동화 관련 콘텐츠를 수집하고, 분류·요약한 뒤,
페르소나 기반 쓰레드 초안 7개를 생성하여 이메일로 전송하는 엔드투엔드 파이프라인이다.

---

## When to Apply

### Must Use
- "콘텐츠 자동화", "/content-automata", "콘텐츠 수집 시작"
- "AI 뉴스 수집해줘", "쓰레드 초안 만들어줘"
- "콘텐츠 파이프라인 돌려줘", "뉴스 큐레이션"
- "/content-automata publish" — 쓰레드 발행 모드

### Skip
- 단순 웹 스크래핑만 필요한 경우 → web-automator 스킬
- Gmail 단순 조회만 필요한 경우 → gog 스킬
- 페르소나만 만들고 싶은 경우 → pinocchio 스킬

---

## Prerequisites

| 도구 | 용도 | 필수 |
|------|------|------|
| WebFetch | 웹 기사 수집 | O |
| Chrome DevTools MCP | Threads/X 피드 수집 | O |
| gog CLI | 뉴스레터 수집 + 이메일 발송 | O |
| pinocchio 페르소나 | 콘텐츠 작성 톤 | O (없으면 기본 페르소나 사용) |
| Agent 도구 | 병렬 수집 서브에이전트 | O |
| SQLite (Python) | 콘텐츠 풀 저장 | O |

### 환경변수

```
THREADS_ACCESS_TOKEN   # Threads API 장기 액세스 토큰 (발행 시)
THREADS_USER_ID        # Threads 사용자 ID (발행 시)
PERPLEXITY_API_KEY     # Perplexity API 키 (팩트 체크 시, 미설정 시 자동 스킵)
GEMINI_API_KEY         # Gemini API 키 (이미지 생성 시, 미설정 시 갤러리 비활성화)
GEMINI_IMAGE_MODEL     # Gemini 이미지 모델 (기본: gemini-2.0-flash-exp)
```

#### 환경변수 설정 방법 (플랫폼별)

**macOS / Linux** — `~/.zshrc` 또는 `~/.bashrc`에 추가:
```bash
export THREADS_ACCESS_TOKEN="your-token"
export PERPLEXITY_API_KEY="pplx-..."
export GEMINI_API_KEY="AIza..."
```

**Windows** — PowerShell에서 영구 설정:
```powershell
[Environment]::SetEnvironmentVariable("THREADS_ACCESS_TOKEN", "your-token", "User")
[Environment]::SetEnvironmentVariable("PERPLEXITY_API_KEY", "pplx-...", "User")
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "AIza...", "User")
```
또는 시스템 설정 → 환경 변수에서 직접 추가한다.
설정 후 터미널을 재시작해야 반영된다.

---

## First Run — 사용자 설정

이 스킬을 처음 사용하는 사용자에게는 아래 항목을 물어본다.
응답을 `config.json`에 저장한다.

1. **이름** (닉네임 또는 실명)
2. **이메일** (초안 리포트를 받을 Gmail 주소)
3. **Chrome 프로필** (Threads/X 로그인된 프로필명)
4. **Threads 발행 계정** (선택사항, 나중에 설정 가능)

현재 설정된 기본 사용자:
- 이름: 단주 (임재호)
- 이메일: danju@starlight-sangdan.com

---

## 핵심 워크플로우

### Phase 1: 콘텐츠 수집 (병렬)

`sources.json`에서 활성화된(`enabled: true`) 소스를 읽어 **타입별로 서브에이전트를 병렬 실행**한다.

#### 소스 타입별 에이전트 매핑

| 타입 | 에이전트 | 설명서 |
|------|---------|--------|
| `web` | web-collector | `agents/web-collector.md` 참조 |
| `chrome` | chrome-collector | `agents/chrome-collector.md` 참조 |
| `email` | email-collector | `agents/email-collector.md` 참조 |

#### 실행 방법

```
1. sources.json을 읽는다.
2. enabled: true인 소스를 타입별로 그룹핑한다.
3. 각 소스에 대해 Agent 도구로 서브에이전트를 생성한다.
   - 에이전트 프롬프트: 해당 agents/*.md 파일의 내용 + 소스 객체를 전달한다.
   - run_in_background: true로 설정하여 병렬 실행한다.
4. 모든 에이전트의 완료를 기다린다.
5. 결과를 통합한다.
```

**소스 추가 방법**: `sources.json`의 `sources` 배열에 새 객체를 추가하면 된다.
기존 에이전트 타입(`web`, `chrome`, `email`)에 해당하면 별도 코드 수정 없이 동작한다.
새 타입이 필요하면 `agents/` 디렉토리에 새 에이전트 명세를 추가한다.

#### web 소스 수집 (서브에이전트)

서브에이전트에게 전달할 프롬프트:
```
agents/web-collector.md를 읽고 그 절차에 따라 아래 소스를 수집하라.

소스 정보:
{sources.json에서 해당 소스 객체를 JSON으로 전달}

수집 기간: 최근 7일
결과는 JSON 형식으로 반환하라.
```

#### chrome 소스 수집 (서브에이전트)

**중요: 멀티탭 병렬 수집**
chrome 소스가 여러 개(예: Threads + X)일 때, 소스마다 **별도의 탭을 열어 병렬로 수집**한다.
하나의 탭에서 순차적으로 처리하지 않는다.

서브에이전트에게 전달할 프롬프트:
```
agents/chrome-collector.md를 읽고 그 절차에 따라 아래 소스를 수집하라.

소스 정보:
{sources.json에서 해당 소스 객체를 JSON으로 전달}

수집 기간: 최근 7일
Chrome DevTools MCP 도구를 사용하여 수집하라.
광고 콘텐츠는 반드시 제외하라.

중요: 각 소스(Threads, X 등)에 대해 mcp__chrome-devtools__new_page로 별도 탭을 열어
병렬로 수집하라. 하나의 탭에서 순차적으로 처리하지 마라.
작업 완료 후 열었던 탭은 mcp__chrome-devtools__close_page로 정리하라.

결과는 JSON 형식으로 반환하라.
```

#### email 소스 수집 (서브에이전트)

서브에이전트에게 전달할 프롬프트:
```
agents/email-collector.md를 읽고 그 절차에 따라 아래 소스를 수집하라.

소스 정보:
{sources.json에서 해당 소스 객체를 JSON으로 전달}

gog CLI를 사용하여 Gmail에서 뉴스레터를 검색하라.
검색 결과가 없으면 skipped: true로 반환하라.
결과는 JSON 형식으로 반환하라.
```

### Phase 1.5: 팩트 체크 (Perplexity API)

수집 완료 후, 콘텐츠 풀 형성 전에 수집된 주장들의 사실 여부를 검증한다.
**`PERPLEXITY_API_KEY` 환경변수가 설정되지 않으면 이 페이즈는 자동으로 스킵한다.**

#### 실행 방법

```bash
# DB 모드 — content_pool 테이블의 미체크 콘텐츠를 일괄 검증
python ~/.claude/skills/content-automata/scripts/fact_check.py \
  --db ~/.claude/skills/content-automata/data/content_pool.db --json

# 수집 결과 JSON 파일 직접 검증
python ~/.claude/skills/content-automata/scripts/fact_check.py \
  --file /tmp/collected_items.json --json
```

#### 팩트 체크 결과 활용

스크립트 반환 JSON 구조:
```json
[
  {
    "content_pool_id": 1,
    "title": "...",
    "verdict": "accurate|partially_accurate|inaccurate|unverifiable",
    "confidence": 85,
    "explanation": "검증 결과 설명",
    "sources": ["https://..."],
    "context": "추가 맥락"
  }
]
```

- `verdict`가 `inaccurate`인 콘텐츠는 Phase 2 분류 시 **제외하거나 경고 태그**를 붙인다.
- `partially_accurate`인 콘텐츠는 `context` 필드의 보정 정보를 초안 작성 시 반영한다.
- `unverifiable`인 콘텐츠는 "미검증" 라벨을 달고 진행한다.
- 결과는 `content_pool.fact_check_result` 컬럼에 JSON으로 자동 저장된다.

#### 스킵 조건

- `PERPLEXITY_API_KEY` 미설정 → `{"skipped": true, "reason": "..."}` 반환, 정상 진행
- API 오류 발생 → 해당 항목만 `verdict: "error"`로 표시, 나머지 계속 진행

### Phase 2: 콘텐츠 풀 형성

모든 수집 결과가 도착하면:

1. **통합**: 전체 수집 결과를 하나로 합친다.
2. **팩트 체크 결과 반영**: Phase 1.5의 검증 결과를 확인한다.
   - `inaccurate` 판정 콘텐츠 → 제외 또는 경고 태그
   - `partially_accurate` → 보정 맥락 포함
   - 팩트 체크 스킵된 경우 → 검증 없이 진행
3. **분류**: `agents/content-classifier.md`를 참조하여 콘텐츠를 분류한다.
   - **속보(Breaking)**: 시의성 높은 단일 뉴스
   - **칼럼(Column)**: 2개 이상 소스에서 교차 확인된 주제 → 앵글 지정
4. **콘텐츠 풀 저장**: 결과를 SQLite에 저장한다.

```bash
# DB 초기화 (최초 1회)
python ~/.claude/skills/content-automata/scripts/init_db.py
```

콘텐츠 풀 = [수집 날짜 + 기간] + [소스별 요약] + [분류 판단에 따른 드래프트 목록]

### Phase 3: 쓰레드 초안 7개 작성

1. **페르소나 로드**: `~/.claude/personas/ai-trend-curator.md`를 읽어 톤·스타일을 적용한다.
2. **레퍼런스 참조**: `references/thread-examples.md`를 읽어 퓨샷 예시로 활용한다.
3. **초안 작성**: Phase 2에서 확정된 7개 콘텐츠 항목에 대해 각각 쓰레드 글을 작성한다.
   - 속보형: 150-250자
   - 칼럼형: 300-500자
   - 7개 글의 구조가 모두 같으면 안 된다 — 다양한 포맷을 섞는다.
4. **SQLite 저장**: drafts 테이블에 저장한다.

### Phase 3.5: 인터랙티브 편집 (HITL)

초안이 생성되면 사용자와 AI 에이전트가 함께 퇴고하는 단계다.
이 단계는 자동 파이프라인 중간에 삽입되며, 사용자가 만족할 때까지 반복한다.

#### 웹 UI 실행

```bash
nca --ui
```

사용자에게 `http://localhost:3847`을 안내한다. 사용자가 UI에서 초안을 선택하면 편집 영역이 열리고, AI 수정 제안이 있으면 자동으로 표시된다 (3초 폴링).

#### AI 에이전트의 수정 제안 흐름

에이전트는 사용자에게 "수정할 부분이 있는지" 물어보거나, 직접 초안을 분석하여 개선점을 찾는다.

1. **초안 확인**:
   ```bash
   nca show <draft_id>
   ```

2. **수정 제안 등록** — 에이전트가 개선된 버전과 이유를 함께 제출한다:
   ```bash
   nca suggest <draft_id> -c "수정된 내용 전체" -r "수정 이유 설명"
   ```
   또는 API로:
   ```
   POST /api/drafts/:id/suggest
   {"content": "수정된 내용", "reason": "수정 이유"}
   ```

3. **사용자 검토** — UI에 실시간으로 제안이 나타난다:
   - **현재 내용**과 **제안 내용**이 나란히 diff 뷰로 표시된다
   - 글자수 변화(+N자 / -N자)가 표시된다
   - 수정 이유가 이탤릭으로 표시된다

4. **사용자 결정** — 세 가지 선택지:
   - **수락**: 제안 내용으로 초안 전체를 교체한다
   - **부분 반영**: 사용자가 에디터에서 일부만 반영한 뒤 "부분 반영" 클릭
   - **거절**: 제안을 무시한다

5. **반복** — 사용자가 추가 수정을 요청하면 에이전트가 다시 `suggest`를 실행한다.

#### CLI 기반 인터랙티브 (UI 없이)

UI 없이 채팅으로만 작업할 때는:

```
사용자: "3번 초안 첫 문장을 좀 더 임팩트 있게 바꿔줘"
에이전트: nca show 3 → 내용 확인 → nca suggest 3 -c "..." -r "..."
사용자: nca suggestions 3 → 제안 확인
사용자: nca accept 1   (또는 nca reject 1)
```

#### 제안 CLI 커맨드 요약

| 명령 | 용도 |
|------|------|
| `nca suggest <id> -c "내용" -r "이유"` | 수정 제안 등록 |
| `nca suggestions <id>` | 초안의 제안 목록 |
| `nca accept <suggestion_id>` | 제안 수락 (초안 교체) |
| `nca reject <suggestion_id>` | 제안 거절 |

#### 제안 API 엔드포인트

| 엔드포인트 | Method | 용도 |
|-----------|--------|------|
| `/api/drafts/:id/suggest` | POST | 수정 제안 등록 |
| `/api/drafts/:id/suggestions` | GET | 제안 목록 (status 필터 가능) |
| `/api/suggestions/:id/resolve` | POST | 수락/거절/부분반영 |

### Phase 4: Gmail 전송

1. `scripts/email_report.html` 템플릿을 읽는다.
2. 7개 초안을 HTML로 렌더링하여 플레이스홀더를 치환한다.
   - `{{REPORT_TITLE}}` → "콘텐츠 자동화 — 오늘의 초안 7선"
   - `{{REPORT_DATE}}` → 오늘 날짜
   - `{{TOTAL_SOURCES}}` → 수집된 소스 수
   - `{{DRAFT_COUNT}}` → 7
   - `{{PERIOD}}` → 수집 기간
   - `{{DRAFTS_HTML}}` → 초안 7개의 HTML (draft 클래스 사용)
3. gog로 자신에게 이메일을 전송한다.

```bash
gog gmail send \
  --to "{config.user.email}" \
  --subject "🗞️ [content-automata] 오늘의 쓰레드 초안 7선 — {날짜}" \
  --html-file /tmp/content-automata-report.html
```

### Phase 5: 보고

파이프라인 완료 후 아래를 사용자에게 보고한다:
- 수집된 소스 총 수 (소스별 내역)
- 스킵된 소스 (이유 포함)
- 생성된 콘텐츠 유형별 수 (속보/칼럼)
- 이메일 전송 결과
- 총 소요 시간

---

## nca CLI — 콘텐츠 관리 도구

`scripts/bin/` 에 빌드된 바이너리와 빌드 스크립트가 포함되어 있다.

| 파일 | 설명 |
|------|------|
| `scripts/bin/nca-darwin-arm64` | macOS Apple Silicon 바이너리 (사전 빌드됨) |
| `scripts/bin/build.sh` | 기타 플랫폼(macOS Intel, Windows, Linux)용 빌드 스크립트 |

### 초기 설정

스킬 첫 실행 시 사용자의 OS·아키텍처를 감지하여 적합한 바이너리를 설치한다.

**macOS Apple Silicon** — 사전 빌드된 바이너리를 바로 사용한다:
```bash
NCA_BIN="$HOME/.claude/skills/content-automata/scripts/bin/nca-darwin-arm64"
mkdir -p ~/.local/bin && cp "$NCA_BIN" ~/.local/bin/nca && chmod +x ~/.local/bin/nca
```

**macOS Intel / Linux** — 빌드 스크립트를 실행한다 (Rust 툴체인 필요):
```bash
~/.claude/skills/content-automata/scripts/bin/build.sh --install
```

**Windows** — PowerShell에서 빌드 스크립트를 실행한다:
```powershell
& "$env:USERPROFILE\.claude\skills\content-automata\scripts\bin\build.ps1" -Install
```
또는 프로젝트 디렉토리에서 직접 빌드:
```powershell
cargo build --release
Copy-Item target\release\nca.exe "$env:LOCALAPPDATA\bin\nca.exe"
```

바이너리가 없거나 설치가 안 된 경우, 프로젝트 디렉토리에서 직접 실행해도 된다:
```bash
cargo run -- list          # 서브커맨드 직접 실행
cargo run -- --ui          # 웹 UI 서버
```

### 크로스 플랫폼 참고

| 항목 | macOS / Linux | Windows |
|------|--------------|---------|
| 홈 디렉토리 | `$HOME` (`~/`) | `%USERPROFILE%` (`$env:USERPROFILE`) |
| 스킬 경로 | `~/.claude/skills/content-automata/` | `%USERPROFILE%\.claude\skills\content-automata\` |
| Python 실행 | `python3` | `python` |
| 임시 디렉토리 | `/tmp/` | `%TEMP%` |
| 바이너리 설치 | `~/.local/bin/nca` | `%LOCALAPPDATA%\bin\nca.exe` |
| 환경변수 설정 | `.zshrc` / `.bashrc` | 시스템 환경 변수 또는 PowerShell |
| 빌드 스크립트 | `build.sh` | `build.ps1` |

스킬 내부의 Python 스크립트들은 `os.path.expanduser('~')`로 경로를 처리하므로 macOS/Linux/Windows 모두에서 동작한다.
Rust CLI(`nca`)는 `HOME` → `USERPROFILE` 순서로 홈 디렉토리를 감지한다.

### CLI 서브커맨드

| 명령 | 용도 |
|------|------|
| `nca list` | 초안 목록 (ID, 유형, 상태, 글자수, 날짜) |
| `nca show <id>` | 초안 상세 + 글자수 카운트 |
| `nca edit <id> -c "내용"` | 초안 내용 수정 |
| `nca publish <id>` | 발행 요청 JSON 출력 |
| `nca pool` | 콘텐츠 풀 보기 |
| `nca runs` | 수집 실행 이력 |
| `nca --ui` | 웹 UI 서버 실행 (http://localhost:3847) |

### 웹 UI (`--ui`)

`nca --ui`를 실행하면 로컬 웹 서버가 시작된다.

- **테이블 뷰**: 역대 콘텐츠 풀의 초안을 표 형태로 표시
- **기간 필터**: 전체 / 7일 / 14일 / 30일 / 90일 버튼으로 필터링
- **검색**: 실시간 검색 (제목, 본문 대상)
- **편집**: 행 클릭 → 하단 textarea에서 직접 편집, 글자수 실시간 표시
- **이미지 생성** (선택사항): 편집 패널 우측에 Gemini 기반 이미지 갤러리
  - 프롬프트 입력 또는 "자동 생성"으로 콘텐츠 맞춤 이미지 생성
  - 비율 지원: 1:1, 4:3, 3:4, 16:9, 9:16, 3:2, 2:3, 직접 지정(너비x높이)
  - 1~4장 동시 생성, 개별 다운로드 지원
  - `GEMINI_API_KEY` 미설정 시 자동 비활성화
- **원본 소스**: 초안별 원본 소스 링크 "더보기" 토글 → 브라우저에서 원본 열기
- **연결 상태**: 고정 navbar에 Threads/Gemini/Perplexity API 연결 상태 표시
- **Export**: navbar의 "Export .md" 버튼으로 전체 초안+소스+최종 수정본을 마크다운 파일로 내보내기
- **발행**: 발행 버튼 클릭 → Threads API 호출 → DB 상태 자동 업데이트

### REST API (AI 에이전트 연동용)

`nca --ui` 실행 중일 때 아래 API를 사용하여 에이전트가 프로그래밍 방식으로 초안을 조작할 수 있다.

| 엔드포인트 | Method | 용도 |
|-----------|--------|------|
| `/api/drafts?days=7&search=AI` | GET | 필터링된 초안 목록 |
| `/api/drafts/:id` | GET | 초안 상세 |
| `/api/drafts/:id` | PUT | 초안 수정 (`{"content": "..."}`) |
| `/api/drafts/:id/publish` | POST | 발행 실행 |
| `/api/runs` | GET | 수집 실행 이력 |
| `/api/pool` | GET | 콘텐츠 풀 |
| `/api/drafts/:id/sources` | GET | 초안의 원본 소스 링크 목록 |
| `/api/status` | GET | 외부 서비스 연결 상태 (Threads/Gemini/Perplexity) |
| `/api/generate-image` | POST | Gemini 이미지 생성 프록시 |

---

## 발행 모드: `/content-automata publish`

사용자가 `/content-automata publish`를 실행하면 **HITL(Human-in-the-Loop) 발행 플로우**를 시작한다.
사람이 최종 퇴고·검증한 뒤에만 발행되므로, AI가 생성한 초안이 무검증으로 게시되는 것을 방지한다.

### Step 1: nca UI 실행

```bash
nca --ui --port 3847
```

웹 UI가 열리면 사용자에게 URL을 안내한다: `http://localhost:3847`

### Step 2: 초안 검토 및 인터랙티브 편집 (HITL)

사용자와 AI 에이전트가 함께 퇴고하는 단계:

1. **초안 목록 확인** — 테이블에서 미발행 초안을 확인한다.
2. **초안 선택** — 행을 클릭하면 하단 편집 영역이 열린다.
3. **직접 퇴고** — textarea에서 직접 수정한다.
   - 글자수가 실시간으로 표시되어 분량 조절이 용이하다.
   - 500자 초과 시 경고가 표시된다.
4. **AI 수정 제안 활용** — 에이전트가 `nca suggest` 또는 API로 수정 제안을 보내면 UI에 실시간(3초 폴링)으로 나타난다.
   - 현재/제안 내용의 diff 뷰가 표시된다.
   - **수락**: 제안 전체 반영
   - **부분 반영**: 에디터에서 원하는 부분만 수정 후 반영
   - **거절**: 무시
5. **저장** — 저장 버튼을 눌러 DB에 반영한다.

에이전트 사용 예시:
```bash
# 에이전트가 초안 확인 후 수정 제안
nca show 3
nca suggest 3 -c "개선된 내용..." -r "첫 문장 임팩트 강화"

# 사용자가 UI에서 수락/거절, 또는 CLI로:
nca accept 1
```

에이전트와 사용자가 UI/CLI 양쪽에서 동시에 작업하며, UI는 자동 폴링으로 새 제안을 감지한다.

### Step 3: 발행 계정 확인

사용자가 발행 버튼을 누르기 전, Threads 계정을 확인한다.

```bash
python ~/.claude/skills/content-automata/scripts/publish_thread.py --profile
```

계정 정보를 사용자에게 보여주고, 맞는지 확인을 받는다.

### Step 4: 발행 방식 선택

사용자에게 질문한다:

1. **즉시 발행** — 지금 바로 게시
2. **예약 발행** — 원하는 시각 입력 (24시간 이내만 가능 — API 컨테이너 TTL 제한)

### Step 5: 발행 실행

**방법 A — 웹 UI에서 직접 발행:**
사용자가 편집 패널의 "발행" 버튼을 클릭한다.
UI가 `/api/drafts/:id/publish` API를 호출하고, 내부적으로 `publish_thread.py`를 실행한다.

**방법 B — CLI를 통해 발행 (에이전트 주도):**
```bash
# 발행 요청 JSON 생성
nca publish <id>

# 위 JSON을 확인한 뒤 실제 발행
python ~/.claude/skills/content-automata/scripts/publish_thread.py \
  --text "최종 확정된 내용" --json

# 예약 발행
python ~/.claude/skills/content-automata/scripts/publish_thread.py \
  --text "최종 확정된 내용" --schedule "2026-04-07T09:00:00+09:00" --json
```

### Step 6: 결과 기록 및 보고

발행 성공 시:
1. SQLite drafts 테이블 업데이트: `published = 1`, `published_at`, `publish_platform = 'threads'`
2. 사용자에게 발행 결과를 보고한다 (media_id, 계정, 발행 시각).
3. 웹 UI에서도 해당 초안이 "발행됨" 상태로 변경된다.

### Threads API 제한사항

| 항목 | 제한 |
|------|------|
| 게시 | 250 posts / 24h |
| API 호출 | 500 calls / 24h |
| 컨테이너 TTL | 생성 후 24시간 |
| 예약 | 네이티브 미지원 → 로컬 대기 후 발행 방식 |

---

## 소스 확장 가이드

새 소스를 추가하려면:

### 기존 타입(web/chrome/email)에 해당하는 경우

`sources.json`의 `sources` 배열에 객체를 추가한다:

```json
{
  "id": "new_source_id",
  "name": "새 소스 이름",
  "type": "web",
  "enabled": true,
  "url": "https://example.com",
  "collect": {
    "method": "web_fetch",
    "list_count": 5,
    "per_article": true,
    "extract": ["title", "url", "summary"]
  },
  "agent": "web-collector"
}
```

### 새 타입이 필요한 경우

1. `agents/` 디렉토리에 `{new-type}-collector.md` 파일을 만든다.
2. 입력/절차/결과 포맷을 기존 에이전트와 동일한 구조로 작성한다.
3. `sources.json`에 `"agent": "new-type-collector"`로 참조한다.

---

## 파일 구조

```
content-automata/
├── SKILL.md                  ← 이 파일
├── config.json               ← 사용자 설정
├── sources.json              ← 수집 대상 (확장 가능)
├── agents/
│   ├── web-collector.md          ← 웹 기사 수집 에이전트
│   ├── chrome-collector.md       ← Threads/X 피드 수집 에이전트
│   ├── email-collector.md        ← 뉴스레터 수집 에이전트
│   └── content-classifier.md     ← 콘텐츠 분류 에이전트
├── references/
│   └── thread-examples.md        ← 쓰레드 퓨샷 예시 (TODO: 실제 예시로 교체)
├── scripts/
│   ├── bin/
│   │   ├── nca-darwin-arm64      ← macOS Apple Silicon 바이너리 (사전 빌드)
│   │   ├── build.sh              ← macOS/Linux 빌드 스크립트
│   │   └── build.ps1             ← Windows PowerShell 빌드 스크립트
│   ├── init_db.py                ← SQLite 초기화
│   ├── fact_check.py             ← Perplexity API 팩트 체크
│   ├── publish_thread.py         ← Threads API 발행
│   └── email_report.html         ← 이메일 리포트 템플릿
└── data/
    └── content_pool.db           ← SQLite DB (자동 생성)
```

---

## 크론/스케줄 실행

이 스킬은 사용자가 직접 실행할 수도 있고, 스케줄에 등록하여 자동 실행할 수도 있다.

예시: 매일 새벽 3시에 실행
```bash
# /schedule 스킬을 사용하거나 crontab으로 등록
0 3 * * * claude -p "/content-automata"
```

---

## 에러 처리

- **개별 소스 실패**: 해당 소스만 스킵하고 나머지를 계속 진행한다.
- **뉴스레터 없음**: `optional: true`인 소스는 조용히 스킵한다.
- **Chrome 미실행**: Chrome DevTools 연결 실패 시 사용자에게 Chrome 실행 안내를 출력하고, web 타입 소스만으로 파이프라인을 계속 진행한다.
- **팩트 체크 스킵**: `PERPLEXITY_API_KEY` 미설정 시 Phase 1.5를 자동 스킵하고 검증 없이 Phase 2로 진행한다.
- **팩트 체크 API 오류**: 개별 항목의 API 호출 실패 시 해당 항목만 `verdict: "error"`로 기록하고 나머지를 계속 처리한다.
- **Threads API 실패**: 에러 메시지를 표시하고 발행을 중단한다. 초안은 DB에 보존되어 재시도 가능하다.
- **gog 인증 실패**: 이메일 전송을 스킵하고 초안을 콘솔에 직접 출력한다.
