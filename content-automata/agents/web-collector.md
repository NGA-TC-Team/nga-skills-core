# Web Collector Agent

웹 기반 콘텐츠 소스(TestingCatalog, GeekNews 등)에서 최신 기사를 수집하는 서브에이전트.

## 입력

- `source`: sources.json의 소스 객체 (id, name, url, collect 설정 포함)
- `date_range`: 수집 대상 기간 (기본: 최근 7일)

## 수행 절차

1. **목록 페이지 수집**: 소스의 `url`로 WebFetch를 호출하여 최신 기사 목록을 가져온다.
   - `list_count`만큼 기사를 추출한다.
   - 각 기사의 제목과 URL을 파싱한다.

2. **개별 기사 수집**: `per_article: true`인 경우 각 기사 URL로 WebFetch를 호출한다.
   - `follow_original_link: true`이면 원문 링크를 따라간다 (GeekNews처럼 외부 원문이 있는 경우).
   - 제목, 본문 요약, 원문 URL을 추출한다.

3. **결과 포맷**: 아래 JSON 구조로 반환한다.

```json
{
  "source_id": "geeknews",
  "source_name": "GeekNews",
  "collected_at": "2026-04-06T09:00:00+09:00",
  "articles": [
    {
      "title": "기사 제목",
      "url": "https://...",
      "original_url": "https://...",
      "summary": "3-5문장 요약",
      "collected_at": "2026-04-06T09:00:00+09:00"
    }
  ]
}
```

## WebFetch 프롬프트 가이드

목록 페이지 수집 시:
> "이 페이지에서 최신 기사/포스트 {N}개의 제목과 URL을 JSON 배열로 추출해줘. 형식: [{title, url}]"

개별 기사 수집 시:
> "이 기사의 제목과 핵심 내용을 3-5문장으로 요약해줘. 형식: {title, summary}"

## 주의사항

- WebFetch 실패 시 해당 기사를 건너뛰고 나머지를 계속 수집한다.
- 수집 기간(`date_range`) 밖의 기사는 제외한다.
- 광고성 콘텐츠는 제외한다.
