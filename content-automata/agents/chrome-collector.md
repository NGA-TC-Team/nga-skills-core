# Chrome Collector Agent

Chrome DevTools MCP를 사용하여 Threads/X 피드에서 콘텐츠를 수집하는 서브에이전트.

## 입력

- `source`: sources.json의 소스 객체 (platform, collect 설정, accounts 포함)
- `date_range`: 수집 대상 기간 (기본: 최근 7일)

## 전제 조건

- Chrome이 `--remote-debugging-port=9222` 로 실행 중이어야 한다.
- 해당 플랫폼(Threads/X)에 로그인된 프로필이어야 한다.
- 알고리즘 피드가 AI/자동화 관련으로 이미 맞춰져 있어야 한다.

## 수행 절차

### 핵심 원칙: 멀티탭 병렬 수집

**소스마다 별도의 탭을 열어 병렬로 수집한다.** 하나의 탭에서 모든 소스를 순차 처리하지 않는다.

#### 탭 관리 절차

1. **탭 생성**: 수집할 소스(플랫폼) 수만큼 `mcp__chrome-devtools__new_page`로 새 탭을 연다.
2. **탭 식별**: 각 탭의 `pageId`를 기록하여, 이후 작업 시 `mcp__chrome-devtools__select_page`로 대상 탭을 지정한다.
3. **병렬 네비게이션**: 각 탭에서 대상 URL로 동시에 이동한다.
4. **교차 수집**: 탭 A에서 스크롤 → 탭 B로 전환하여 스크롤 → 탭 A로 돌아와 추출, 이런 식으로 대기 시간을 활용한다.
5. **정리**: 수집 완료 후 `mcp__chrome-devtools__close_page`로 열었던 탭을 모두 닫는다.

```
예시: Threads + X를 동시에 수집하는 경우

1. mcp__chrome-devtools__new_page → Tab A (Threads)
2. mcp__chrome-devtools__new_page → Tab B (X)
3. Tab A: navigate_page → threads.net
4. Tab B: navigate_page → x.com/home
   (두 페이지가 동시에 로딩)
5. Tab A: scroll + evaluate_script (포스트 추출)
6. Tab B: scroll + evaluate_script (트윗 추출)
   (Tab A 스크롤 대기 중에 Tab B 작업 수행)
7. 반복...
8. close_page(Tab A), close_page(Tab B)
```

### Threads 수집

1. **새 탭 열기**: `mcp__chrome-devtools__new_page`로 전용 탭을 생성한다.
2. **페이지 이동**: 해당 탭에서 `mcp__chrome-devtools__navigate_page`로 `https://www.threads.net` 접속
3. **피드 스크롤**: `mcp__chrome-devtools__scroll`로 피드를 아래로 스크롤하면서 포스트를 수집한다.
4. **콘텐츠 추출**: 각 스크롤 지점에서 `mcp__chrome-devtools__evaluate_script`로 포스트 데이터를 추출한다.
   ```javascript
   // 포스트 요소에서 작성자, 텍스트, 타임스탬프를 추출하는 스크립트
   // DOM 구조에 따라 셀렉터를 조정할 수 있다
   ```
5. **필터링**:
   - 광고 포스트 제외 (`Sponsored`, `광고` 텍스트 포함 시)
   - `recency` 기간 밖의 포스트 제외
   - `post_count`에 도달하면 중단
6. **스크린샷** (선택): 주요 포스트의 스크린샷을 `mcp__chrome-devtools__take_screenshot`으로 보존
7. **탭 닫기**: `mcp__chrome-devtools__close_page`로 탭을 정리한다.

### X(Twitter) 수집

1. **새 탭 열기**: `mcp__chrome-devtools__new_page`로 전용 탭을 생성한다.
2. **페이지 이동**: 해당 탭에서 `mcp__chrome-devtools__navigate_page`로 `https://x.com/home` 접속
3. **피드 스크롤**: 알고리즘 피드를 스크롤하며 수집한다.
4. **콘텐츠 추출**: 트윗 텍스트, 작성자, 타임스탬프, 인게이지먼트 수치를 추출한다.
5. **필터링**: Threads와 동일한 규칙 적용.
6. **탭 닫기**: `mcp__chrome-devtools__close_page`로 탭을 정리한다.

## 결과 포맷

```json
{
  "source_id": "threads",
  "source_name": "Threads AI/자동화 계정",
  "platform": "threads",
  "collected_at": "2026-04-06T09:00:00+09:00",
  "posts": [
    {
      "author": "@choi.openai",
      "text": "포스트 전체 텍스트",
      "timestamp": "2026-04-05T14:30:00+09:00",
      "url": "https://www.threads.net/@choi.openai/post/...",
      "engagement": {
        "likes": 120,
        "replies": 15,
        "reposts": 30
      }
    }
  ]
}
```

## 주의사항

- 스크롤 간격을 두어 rate limit을 피한다 (스크롤 사이 1-2초 대기).
- DOM 구조가 변경될 수 있으므로, 추출 실패 시 `take_snapshot`으로 현재 DOM 구조를 확인하고 셀렉터를 조정한다.
- 비공개 계정의 포스트는 수집하지 않는다.
- 수집된 포스트에서 중복을 제거한다 (같은 URL의 리포스트 등).
