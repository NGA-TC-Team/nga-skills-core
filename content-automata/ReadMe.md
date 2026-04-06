# content-automata — AI 콘텐츠 자동화 파이프라인

> AI·자동화 분야 콘텐츠를 여러 채널에서 수집하고, 분류·요약한 뒤, 쓰레드 초안 7개를 만들어 이메일로 전송하는 자동화 스킬

---

## 이 스킬이 하는 일

콘텐츠를 매번 직접 찾아보고, 정리하고, 글 초안을 쓰는 작업을 자동화합니다.

```
웹사이트 (TestingCatalog, GeekNews) ┐
Threads 피드                        ├──▶ 수집 ──▶ 분류·요약 ──▶ 초안 7개 ──▶ 이메일 전송
X(Twitter) 피드                     ┤
Gmail 뉴스레터                       ┘
```

한 번 명령하면 Claude가 알아서 뉴스를 읽고, 중요한 것을 골라 글 초안까지 써서 보내줍니다.

---

## 사전 준비사항

스킬을 처음 사용하기 전에 아래 항목을 순서대로 준비합니다.

---

### 1단계 — 필수 프로그램 설치

#### Claude Code

이 스킬을 실행하는 기반 환경입니다. 아직 없다면 먼저 설치합니다.

- 다운로드: [claude.ai/code](https://claude.ai/code)

#### Google Chrome

Threads, X(Twitter) 피드를 수집할 때 사용합니다.  
이미 설치되어 있다면 별도 조치 불필요합니다.

- 다운로드: [google.com/chrome](https://www.google.com/chrome/)

> 반드시 **Google Chrome**이어야 합니다. Safari, Firefox, Edge 등 다른 브라우저는 지원하지 않습니다.

#### Python 3

팩트 체크, DB 초기화, Threads 발행 스크립트가 Python 3로 작성되어 있습니다.

**macOS** — 터미널에서 확인:
```bash
python3 --version
# Python 3.x.x 가 출력되면 설치된 것
```

설치되어 있지 않다면:
```bash
# Homebrew가 있는 경우
brew install python3

# Homebrew가 없는 경우 → https://python.org/downloads 에서 설치
```

> **용어 설명**: *Homebrew*는 macOS에서 프로그램을 명령어 한 줄로 설치할 수 있게 해주는 패키지 관리자입니다. 없다면 [brew.sh](https://brew.sh)에서 먼저 설치합니다.

**Windows** — [python.org/downloads](https://www.python.org/downloads/) 에서 설치.  
설치 시 **"Add Python to PATH"** 체크박스를 반드시 선택합니다.

#### Rust 툴체인 (macOS Intel / Linux / Windows만 해당)

**macOS Apple Silicon(M1/M2/M3)은 건너뜁니다** — 사전 빌드된 바이너리가 포함되어 있습니다.

macOS Intel, Linux, Windows에서 `nca` 도구를 직접 빌드할 때 필요합니다.

**macOS / Linux:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
# 설치 후 터미널 재시작
rustc --version   # 확인
```

**Windows** — [rustup.rs](https://rustup.rs) 에서 `rustup-init.exe` 다운로드 후 실행.

> **용어 설명**: *Rust*는 프로그래밍 언어입니다. `nca` CLI 도구가 Rust로 만들어졌기 때문에, Apple Silicon 맥이 아닌 환경에서는 직접 빌드(컴파일)해야 합니다.

---

### 2단계 — CLI 프로그램 설치

> **용어 설명**: *CLI(Command Line Interface)*는 터미널에서 명령어를 입력해 사용하는 도구입니다.

#### nca — 콘텐츠 관리 도구 (이 스킬 전용)

초안 조회·편집·발행을 담당하는 도구입니다.

**macOS Apple Silicon (M1/M2/M3):**
```bash
NCA_BIN="$HOME/.claude/skills/content-automata/scripts/bin/nca-darwin-arm64"
mkdir -p ~/.local/bin
cp "$NCA_BIN" ~/.local/bin/nca
chmod +x ~/.local/bin/nca
```

이후 `~/.local/bin`이 PATH에 있는지 확인합니다:
```bash
echo $PATH | grep -q ".local/bin" && echo "OK" || echo "PATH에 추가 필요"
```

PATH에 없다면 `~/.zshrc`에 아래 줄을 추가합니다:
```bash
export PATH="$HOME/.local/bin:$PATH"
```
저장 후 `source ~/.zshrc` 실행.

**macOS Intel / Linux:**
```bash
~/.claude/skills/content-automata/scripts/bin/build.sh --install
```

**Windows (PowerShell):**
```powershell
& "$env:USERPROFILE\.claude\skills\content-automata\scripts\bin\build.ps1" -Install
```

설치 확인:
```bash
nca --version
```

#### gog — Google Workspace CLI

Gmail 뉴스레터 수집과 이메일 발송에 사용합니다.

**macOS:**
```bash
brew install gog
# 또는
pip3 install gog-cli
```

**Windows:**
```powershell
pip install gog-cli
```

설치 후 Google 계정 연결:
```bash
gog auth
# 브라우저가 열리면 Google 계정으로 로그인
```

> `gog` 스킬이 별도로 설치되어 있어야 위 명령이 작동합니다. 아래 "3단계 — 스킬 설치" 참조.

---

### 3단계 — Claude Code 스킬 설치

Claude Code에서 `/find-skills` 명령으로 검색하거나, 아래 스킬들을 직접 설치합니다.

#### 필수 스킬

| 스킬 | 용도 | 없을 때 |
|------|------|---------|
| **gog** | Gmail 뉴스레터 수집 + 이메일 발송 | 뉴스레터 수집 불가, 이메일 전송 불가 |
| **Chrome DevTools MCP** | Threads/X 피드 수집 | Threads, X 수집 불가 |

#### 선택 스킬

| 스킬 | 용도 | 없을 때 |
|------|------|---------|
| **pinocchio** | 페르소나 기반 글쓰기 톤 설정 | 기본 페르소나로 대체됨 |

스킬 설치 방법:
```
Claude Code에서 입력:
/find-skills gog
/find-skills pinocchio
```

#### Chrome DevTools MCP 설정

Claude Code의 `settings.json`에 MCP 서버를 추가합니다.

**macOS** (`~/.claude/settings.json`):
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-chrome-devtools"]
    }
  }
}
```

**Windows** (`%USERPROFILE%\.claude\settings.json`):
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-chrome-devtools"]
    }
  }
}
```

> **용어 설명**: *MCP(Model Context Protocol)*는 Claude가 외부 프로그램(Chrome 등)을 제어할 수 있게 해주는 연결 방식입니다. *npx*는 Node.js와 함께 설치되는 패키지 실행 도구입니다. `npx`가 없다면 [nodejs.org](https://nodejs.org)에서 Node.js를 설치합니다.

---

### 4단계 — API 키 발급 및 환경변수 설정

> **용어 설명**: *API 키*는 외부 서비스에 접근할 때 사용하는 고유 비밀번호입니다. *환경변수*는 프로그램이 실행 중에 읽는 시스템 설정값입니다. 민감한 정보를 코드에 직접 쓰지 않고 안전하게 관리하는 방법입니다.

#### API 키 목록

| 키 이름 | 필수 여부 | 용도 | 발급 위치 |
|---------|----------|------|----------|
| `THREADS_ACCESS_TOKEN` | 발행 시 필수 | Threads에 글 게시 | Meta 개발자 콘솔 |
| `THREADS_USER_ID` | 발행 시 필수 | Threads 계정 식별 | Meta 개발자 콘솔 |
| `PERPLEXITY_API_KEY` | 선택 | 팩트 체크 | Perplexity AI 대시보드 |
| `GEMINI_API_KEY` | 선택 | 이미지 생성 | Google AI Studio |
| `GEMINI_IMAGE_MODEL` | 선택 | 이미지 모델 지정 | (값: `gemini-2.0-flash-exp`) |

> 발행 기능을 쓰지 않는다면 `THREADS_ACCESS_TOKEN`, `THREADS_USER_ID` 없이도 수집·초안 작성·이메일 전송까지 모두 가능합니다.

#### Threads API 키 발급 방법

1. [developers.facebook.com](https://developers.facebook.com) 접속 후 로그인
2. **My Apps → Create App → Business** 선택
3. 앱 생성 후 **Threads API** 제품 추가
4. **Threads API → 사용자 토큰 생성** 에서 장기 액세스 토큰(Long-lived Token) 발급
5. **사용자 ID**는 토큰 발급 페이지 또는 Graph API Explorer에서 확인

#### Perplexity API 키 발급 방법

1. [perplexity.ai](https://www.perplexity.ai) 가입 후 로그인
2. 우측 상단 프로필 → **API** 메뉴 이동
3. **Generate** 버튼으로 키 생성
4. `pplx-`로 시작하는 키를 복사

#### Gemini API 키 발급 방법

1. [aistudio.google.com](https://aistudio.google.com) 접속 (Google 계정 필요)
2. 좌측 메뉴 **Get API key** 클릭
3. **Create API key** 후 복사

---

#### 환경변수 설정 — macOS

터미널을 열고 아래 명령으로 `~/.zshrc` 파일을 편집합니다:

```bash
open -e ~/.zshrc
# 텍스트 편집기가 열리면 아래 내용을 파일 맨 아래에 추가
```

추가할 내용:
```bash
# content-automata 스킬 환경변수
export THREADS_ACCESS_TOKEN="여기에_토큰_붙여넣기"
export THREADS_USER_ID="여기에_유저ID_붙여넣기"
export PERPLEXITY_API_KEY="pplx-여기에_키_붙여넣기"
export GEMINI_API_KEY="AIza여기에_키_붙여넣기"
```

저장 후 적용:
```bash
source ~/.zshrc
```

확인:
```bash
echo $THREADS_ACCESS_TOKEN   # 토큰이 출력되면 정상
```

---

#### 환경변수 설정 — Windows

**방법 A: 시스템 설정 (GUI, 권장)**

1. 시작 메뉴에서 **"환경 변수"** 검색 → **"시스템 환경 변수 편집"** 클릭
2. 하단 **"환경 변수(N)..."** 버튼 클릭
3. 위쪽 **"사용자 변수"** 영역에서 **"새로 만들기"** 클릭
4. 변수 이름과 값을 입력 후 확인

| 변수 이름 | 값 |
|----------|-----|
| `THREADS_ACCESS_TOKEN` | 발급받은 토큰 |
| `THREADS_USER_ID` | 발급받은 유저 ID |
| `PERPLEXITY_API_KEY` | 발급받은 키 |
| `GEMINI_API_KEY` | 발급받은 키 |

5. 설정 후 **터미널(PowerShell) 완전히 재시작** 필수

**방법 B: PowerShell 명령어**

```powershell
[Environment]::SetEnvironmentVariable("THREADS_ACCESS_TOKEN", "여기에_토큰", "User")
[Environment]::SetEnvironmentVariable("THREADS_USER_ID", "여기에_유저ID", "User")
[Environment]::SetEnvironmentVariable("PERPLEXITY_API_KEY", "pplx-여기에_키", "User")
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "AIza여기에_키", "User")
```

확인:
```powershell
$env:THREADS_ACCESS_TOKEN   # 토큰이 출력되면 정상
```

---

### 5단계 — 데이터베이스 초기화 (최초 1회)

수집 데이터를 저장할 DB 파일을 생성합니다.

**macOS / Linux:**
```bash
python3 ~/.claude/skills/content-automata/scripts/init_db.py
# → "DB initialized at ..." 메시지가 나오면 성공
```

**Windows (PowerShell):**
```powershell
python "$env:USERPROFILE\.claude\skills\content-automata\scripts\init_db.py"
```

---

### 준비 완료 체크리스트

모두 완료했는지 확인합니다:

- [ ] Claude Code 설치됨
- [ ] Google Chrome 설치됨
- [ ] Python 3 설치됨 (`python3 --version` 확인)
- [ ] `nca` 설치됨 (`nca --version` 확인)
- [ ] `gog` 설치 및 `gog auth` 완료
- [ ] Chrome DevTools MCP 설정 완료 (`settings.json` 등록)
- [ ] Threads API 키 환경변수 설정 완료 (발행 기능 사용 시)
- [ ] Perplexity API 키 설정 완료 (팩트 체크 사용 시)
- [ ] DB 초기화 완료 (`init_db.py` 실행)

---

### 공식 다운로드 링크 모음

| 도구 | 공식 링크 | 비고 |
|------|-----------|------|
| **Claude Code** | [claude.com/download](https://claude.com/download) | Mac, Windows 지원 |
| **Google Chrome** | [google.com/chrome](https://www.google.com/chrome/) | Mac, Windows 지원 |
| **Python 3** | [python.org/downloads](https://www.python.org/downloads/) | Mac, Windows 지원 |
| **Rust (rustup)** | [rustup.rs](https://rustup.rs/) | Mac Intel/Linux/Windows용 (Apple Silicon 불필요) |
| **Homebrew** | [brew.sh](https://brew.sh/) | macOS 패키지 관리자 (Mac 전용) |
| **Node.js** | [nodejs.org](https://nodejs.org/) | Chrome DevTools MCP 실행에 필요한 npx 포함 |
| **gog CLI** | [gogcli.sh](https://gogcli.sh/) · [GitHub](https://github.com/steipete/gogcli) | Gmail·캘린더·드라이브 CLI |

---

## 폴더 구조 설명

```
content-automata/
├── SKILL.md                    ← 스킬 핵심 명세 (Claude가 읽는 설명서)
├── config.json                 ← 사용자 설정 (이름, 이메일, Chrome 프로필 등)
├── sources.json                ← 수집할 소스 목록 (어디서 뉴스를 가져올지)
│
├── agents/                     ← 수집 작업별 세부 지침서
│   ├── web-collector.md        ← 웹사이트에서 기사 수집하는 방법
│   ├── chrome-collector.md     ← Threads/X 피드를 브라우저로 수집하는 방법
│   ├── email-collector.md      ← Gmail 뉴스레터를 수집하는 방법
│   └── content-classifier.md  ← 수집한 내용을 분류하는 방법
│
├── references/
│   └── thread-examples.md     ← 쓰레드 글 작성 예시 및 가이드라인
│
├── scripts/                    ← 실행 가능한 프로그램 파일들
│   ├── init_db.py              ← DB 초기화 스크립트 (최초 1회 실행)
│   ├── fact_check.py           ← 팩트 체크 스크립트 (Perplexity API 사용)
│   ├── publish_thread.py       ← Threads에 글을 직접 발행하는 스크립트
│   ├── email_report.html       ← 이메일 보고서 HTML 템플릿
│   └── bin/
│       ├── nca-darwin-arm64    ← macOS Apple Silicon용 nca 실행 파일 (사전 빌드)
│       ├── build.sh            ← macOS Intel/Linux용 빌드 스크립트
│       └── build.ps1           ← Windows용 빌드 스크립트
│
└── data/
    └── content_pool.db         ← 수집·분류·초안 데이터 저장소 (SQLite DB)
```

---

## 각 파일·폴더가 하는 역할

### `SKILL.md` — 스킬의 두뇌

Claude가 이 스킬을 실행할 때 가장 먼저 읽는 파일입니다.  
"어떤 순서로 일을 처리할지", "각 단계에서 무엇을 해야 할지"를 정의합니다.

> **용어 설명**: *스킬(Skill)*이란 Claude에게 특정 일을 시키는 방법을 미리 정의해 놓은 명세서입니다. 마치 직원에게 "이 업무는 이렇게 처리하세요"라고 작성한 업무 매뉴얼과 같습니다.

---

### `config.json` — 사용자 설정

```json
{
  "user": {
    "name": "단주",
    "email": "danju@starlight-sangdan.com"
  },
  "chrome": {
    "profile_name": "Default"
  }
}
```

처음 스킬을 실행할 때 이름·이메일·Chrome 프로필 등을 물어보고 여기에 저장합니다.  
다음 실행부터는 다시 묻지 않습니다.

---

### `sources.json` — 수집 소스 목록

**어디서 콘텐츠를 가져올지** 정의하는 파일입니다. 현재 설정된 소스:

| 소스 | 종류 | 설명 |
|------|------|------|
| TestingCatalog | 웹사이트 | AI 뉴스 전문 미디어 |
| GeekNews | 웹사이트 | 국내 개발자 커뮤니티 뉴스 |
| Threads AI 계정 40개 | SNS 피드 | AI·자동화 관련 한국 계정들 |
| X(Twitter) 알고리즘 피드 | SNS 피드 | AI 관련 트윗 |
| Uncovering AI | 뉴스레터 | Gmail로 받는 AI 뉴스레터 |
| Simplifying AI | 뉴스레터 | Gmail로 받는 AI 뉴스레터 |
| The Information | 뉴스레터 | Gmail로 받는 IT 뉴스레터 |

**소스 추가 방법**: `sources.json`의 `sources` 배열에 새 항목을 추가하면 다음 실행부터 자동으로 포함됩니다. 코드 수정 없이 JSON 파일만 편집하면 됩니다.

> **용어 설명**: *JSON*이란 사람도 읽을 수 있는 데이터 저장 형식입니다. `{"키": "값"}` 구조로 설정을 표현합니다.

---

### `agents/` — 수집 방법별 지침서

> **용어 설명**: *에이전트(Agent)*란 특정 작업을 독립적으로 수행하는 AI 보조 프로그램입니다. 여기서는 각 소스에서 콘텐츠를 수집하는 전문 역할을 맡습니다.

#### `web-collector.md` — 웹사이트 수집 에이전트

TestingCatalog, GeekNews 같은 웹사이트에서 기사를 가져옵니다.
- 기사 목록 페이지 → 개별 기사 본문 순서로 수집
- 수집 실패한 기사는 건너뛰고 나머지를 계속 진행

#### `chrome-collector.md` — 브라우저 기반 수집 에이전트

Threads, X(Twitter) 피드처럼 **로그인이 필요한 SNS**에서 수집합니다.  
사용자의 Chrome 브라우저를 원격으로 제어해 피드를 스크롤하며 게시글을 읽어옵니다.

- 여러 플랫폼을 동시에 탭을 열어 병렬 수집 (시간 절약)
- 광고 게시글 자동 제외
- 수집 완료 후 열었던 탭 자동 닫기

> **용어 설명**: *병렬 수집*이란 여러 작업을 동시에 처리하는 것입니다. Threads와 X를 각각 다른 탭에서 동시에 여는 방식으로, 순서대로 처리할 때보다 시간이 절반으로 줄어듭니다.

**전제 조건**: Chrome이 원격 제어 모드(`--remote-debugging-port=9222`)로 실행 중이어야 합니다.

#### `email-collector.md` — 뉴스레터 수집 에이전트

Gmail에 도착한 AI 관련 뉴스레터를 읽어 핵심 내용을 요약합니다.  
해당 기간에 메일이 없으면 자동으로 건너뜁니다.

#### `content-classifier.md` — 분류 에이전트

수집된 전체 콘텐츠를 분석하여 두 가지로 분류합니다:

| 유형 | 조건 | 설명 |
|------|------|------|
| **속보 (Breaking)** | 단일 소스 | 시의성 높은 신규 소식 (신모델 출시, 서비스 업데이트 등) |
| **칼럼 (Column)** | 2개 이상 소스 | 여러 매체에서 교차 확인된 주제, 깊이 있는 분석 가능 |

분류 후 총 7개의 콘텐츠 초안 주제를 확정합니다.

---

### `references/thread-examples.md` — 글쓰기 가이드

Claude가 쓰레드 글을 쓸 때 참고하는 **예시 모음과 작성 규칙**입니다.

- 속보형: 150-250자, 핵심 메시지 중심
- 칼럼형: 300-500자, 근거 2-3개 + 인사이트
- 이모지는 구조 표시용으로만 사용
- 출처 불명확한 수치 사용 금지

---

### `scripts/` — 실행 가능한 프로그램들

#### `init_db.py` — 데이터베이스 초기화

**최초 1회만 실행**하면 됩니다. 콘텐츠를 저장할 데이터베이스 구조를 만듭니다.

```bash
python3 ~/.claude/skills/content-automata/scripts/init_db.py
```

> **용어 설명**: *데이터베이스(DB)*란 데이터를 체계적으로 저장하고 검색할 수 있는 저장소입니다. 여기서는 수집한 기사, 분류 결과, 초안 내용을 저장하는 데 사용합니다. *SQLite*는 별도 서버 없이 파일 하나로 동작하는 가벼운 DB입니다.

저장되는 데이터:

| 테이블 | 저장 내용 |
|--------|----------|
| `collection_runs` | 수집 실행 이력 (언제 실행했는지) |
| `raw_sources` | 수집된 원본 기사·게시글 |
| `content_pool` | 분류된 콘텐츠 풀 (속보/칼럼) |
| `drafts` | 생성된 쓰레드 초안 7개 |

#### `fact_check.py` — 팩트 체크 (선택사항)

`PERPLEXITY_API_KEY` 환경변수가 설정된 경우에만 동작합니다.  
수집된 내용의 사실 여부를 검증하고 결과를 4단계로 표시합니다:

| 결과 | 의미 |
|------|------|
| `accurate` | 사실 확인됨 |
| `partially_accurate` | 일부 사실, 보정 필요 |
| `inaccurate` | 사실 아님 → 초안에서 제외 |
| `unverifiable` | 확인 불가 → "미검증" 라벨 부착 |

#### `publish_thread.py` — Threads 직접 발행

작성된 초안을 Threads에 바로 게시합니다.

```bash
# 즉시 게시
python3 publish_thread.py --text "게시할 내용"

# 예약 게시 (최대 24시간 이내)
python3 publish_thread.py --text "게시할 내용" --schedule "2026-04-07T09:00:00+09:00"

# 내 프로필 확인
python3 publish_thread.py --profile
```

**필요한 환경변수**: `THREADS_ACCESS_TOKEN`, `THREADS_USER_ID`

#### `email_report.html` — 이메일 보고서 템플릿

초안 7개를 정리해서 이메일로 보낼 때 사용하는 HTML 디자인 템플릿입니다.  
Claude가 자동으로 날짜, 수집 소스 수, 초안 내용을 채워 넣습니다.

---

### `data/content_pool.db` — 데이터 저장소

모든 수집 결과와 초안이 저장되는 파일입니다. 직접 편집할 필요 없이 `nca` CLI로 조회·관리합니다.

---

## 사용 방법

### 1. 최초 설치

**macOS Apple Silicon (M1/M2/M3):**
```bash
NCA_BIN="$HOME/.claude/skills/content-automata/scripts/bin/nca-darwin-arm64"
mkdir -p ~/.local/bin && cp "$NCA_BIN" ~/.local/bin/nca && chmod +x ~/.local/bin/nca
```

**macOS Intel / Linux** (Rust 빌드 도구 필요):
```bash
~/.claude/skills/content-automata/scripts/bin/build.sh --install
```

**Windows** (PowerShell):
```powershell
& "$env:USERPROFILE\.claude\skills\content-automata\scripts\bin\build.ps1" -Install
```

> **용어 설명**: *Apple Silicon*은 M1/M2/M3 칩이 탑재된 맥입니다. *Intel Mac*은 그 이전 세대 맥입니다. 어느 쪽인지 모르면 애플 메뉴 → "이 Mac에 관하여"에서 확인할 수 있습니다.

**데이터베이스 초기화 (최초 1회):**
```bash
python3 ~/.claude/skills/content-automata/scripts/init_db.py
```

### 2. 환경변수 설정

`~/.zshrc` (macOS 기본 셸)에 아래 내용을 추가합니다:

```bash
# Threads 발행용 (발행 기능 사용 시 필수)
export THREADS_ACCESS_TOKEN="your-token"
export THREADS_USER_ID="your-user-id"

# 팩트 체크용 (선택사항)
export PERPLEXITY_API_KEY="pplx-..."
```

저장 후 터미널을 재시작하거나 `source ~/.zshrc`를 실행합니다.

> **용어 설명**: *환경변수*란 프로그램이 실행될 때 참조하는 시스템 설정값입니다. API 키처럼 민감한 정보를 코드에 직접 쓰지 않고 안전하게 관리하는 방법입니다.

### 3. Chrome 원격 제어 활성화 (Threads/X 수집 시 필요)

Chrome을 원격 제어 모드로 실행합니다:

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 --profile-directory="Default"
```

이미 Chrome이 열려 있다면 완전히 종료한 후 위 명령으로 다시 실행합니다.

### 4. 파이프라인 실행

Claude Code에서 아래 중 하나를 입력합니다:

```
콘텐츠 자동화 시작
```
```
/content-automata
```
```
AI 뉴스 수집해줘
```

### 5. 쓰레드 직접 발행 모드

초안 검토 후 바로 발행하려면:

```
/content-automata publish
```

---

## 파이프라인 전체 흐름

```
Phase 1   수집 (병렬)
          ├─ web-collector    : TestingCatalog, GeekNews 기사 수집
          ├─ chrome-collector : Threads, X 피드 수집 (멀티탭 병렬)
          └─ email-collector  : Gmail 뉴스레터 수집
              ↓
Phase 1.5 팩트 체크 (PERPLEXITY_API_KEY 있을 때만)
              ↓
Phase 2   콘텐츠 풀 형성
          └─ content-classifier : 속보/칼럼 분류 → 7개 주제 확정
              ↓
Phase 3   쓰레드 초안 7개 작성
          └─ 페르소나 + 레퍼런스 예시 참조하여 작성
              ↓
Phase 3.5 인터랙티브 편집 (HITL)
          └─ 사용자와 Claude가 함께 초안 퇴고
              ↓
Phase 4   Gmail 전송
          └─ HTML 보고서 형태로 자신에게 이메일 발송
              ↓
Phase 5   결과 보고
          └─ 수집 소스 수, 스킵 항목, 소요 시간 요약
```

> **용어 설명**: *HITL(Human In The Loop)*은 자동화 중간에 사람이 개입해 검토·수정하는 방식입니다. 100% 자동화하지 않고 최종 판단은 사람이 하는 구조입니다.

---

## nca CLI — 초안 관리 도구

**nca**는 수집된 콘텐츠와 초안을 관리하는 전용 명령줄 도구입니다.

> **용어 설명**: *CLI(Command Line Interface)*는 터미널에서 명령어를 입력해 사용하는 프로그램입니다. 앱처럼 클릭하는 게 아니라 텍스트 명령으로 조작합니다.

### 기본 명령어

| 명령 | 설명 | 예시 |
|------|------|------|
| `nca list` | 초안 목록 보기 | ID, 유형, 글자수, 날짜 표시 |
| `nca show <번호>` | 초안 내용 보기 | `nca show 3` → 3번 초안 전문 |
| `nca edit <번호> -c "내용"` | 초안 수정 | `nca edit 3 -c "수정된 내용"` |
| `nca publish <번호>` | 발행 준비 | 발행 요청 정보 출력 |
| `nca pool` | 콘텐츠 풀 보기 | 분류된 주제 목록 |
| `nca runs` | 실행 이력 | 과거 수집 기록 조회 |
| `nca --ui` | 웹 UI 실행 | 브라우저로 초안 편집 |

### 수정 제안 명령어 (Claude가 사용)

Claude가 초안을 분석하고 개선안을 제안할 때 쓰는 명령어입니다.

| 명령 | 설명 |
|------|------|
| `nca suggest <번호> -c "내용" -r "이유"` | 수정 제안 등록 |
| `nca suggestions <번호>` | 해당 초안의 제안 목록 |
| `nca accept <제안번호>` | 제안 수락 (초안 내용 교체) |
| `nca reject <제안번호>` | 제안 거절 |

### 웹 UI (`nca --ui`)

터미널 명령어가 불편하다면 웹 인터페이스를 사용할 수 있습니다.

```bash
nca --ui
# → http://localhost:3847 에서 브라우저로 접속
```

웹 UI에서 할 수 있는 것:
- 초안 7개를 한 눈에 확인
- 클릭 한 번으로 내용 편집
- Claude의 수정 제안을 나란히 비교 (diff 뷰)
- 수락·거절·부분 반영 선택

> **용어 설명**: *localhost*는 자신의 컴퓨터를 가리킵니다. `http://localhost:3847`은 내 컴퓨터에서 실행 중인 웹 서버에 접속하는 주소입니다. 인터넷이 아니라 로컬에서만 동작합니다.

### nca 설치 확인

```bash
nca --version    # 버전 출력되면 정상 설치
which nca        # 설치 경로 확인
```

---

## 플랫폼별 경로 참고

| 항목 | macOS / Linux | Windows |
|------|--------------|---------|
| 스킬 위치 | `~/.claude/skills/content-automata/` | `%USERPROFILE%\.claude\skills\content-automata\` |
| DB 위치 | `~/.claude/skills/content-automata/data/content_pool.db` | `%USERPROFILE%\.claude\skills\content-automata\data\content_pool.db` |
| nca 설치 위치 | `~/.local/bin/nca` | `%LOCALAPPDATA%\bin\nca.exe` |
| Python 실행 | `python3` | `python` |
| 환경변수 설정 | `~/.zshrc` 또는 `~/.bashrc` | 시스템 환경 변수 또는 PowerShell |

---

## 자주 묻는 질문

**Q. Chrome 없이도 되나요?**  
웹사이트(TestingCatalog, GeekNews)와 뉴스레터(Gmail)는 Chrome 없이 수집됩니다. Threads, X 피드만 Chrome이 필요합니다.

**Q. 팩트 체크가 뭔가요?**  
Perplexity AI를 사용해 수집된 내용이 사실인지 검증하는 단계입니다. API 키가 없으면 자동으로 건너뜁니다.

**Q. 초안 7개가 항상 생성되나요?**  
네, 수집된 소스가 충분하면 속보·칼럼 합산 7개를 항상 생성합니다.

**Q. 발행은 자동으로 되나요?**  
아닙니다. 초안을 이메일로 받고, 검토한 뒤 `nca publish`나 `/content-automata publish`로 직접 발행합니다. 사람이 최종 확인하는 구조입니다.

**Q. 소스를 추가하거나 빼고 싶어요.**  
`sources.json`에서 해당 소스의 `"enabled": true`를 `"enabled": false`로 바꾸면 수집에서 제외됩니다. 새 소스 추가도 같은 파일에서 합니다.
