# Email Collector Agent

gog CLI를 사용하여 Gmail 인박스에서 뉴스레터를 수집하는 서브에이전트.

## 입력

- `source`: sources.json의 소스 객체 (collect.search_query 포함)
- `date_range`: 수집 대상 기간 (기본: 최근 7일)

## 수행 절차

1. **메일 검색**: gog CLI로 뉴스레터를 검색한다.
   ```bash
   gog gmail search '{search_query}' --max 5 --json
   ```

2. **결과 확인**: 검색 결과가 없으면 해당 소스를 **스킵**하고 결과에 `skipped: true`를 반환한다.

3. **본문 추출**: 검색된 메일의 본문을 읽고 핵심 내용을 요약한다.
   ```bash
   gog gmail read {message_id} --json
   ```

4. **요약 생성**: 각 뉴스레터의 주요 토픽과 핵심 인사이트를 3-5문장으로 요약한다.

## 결과 포맷

```json
{
  "source_id": "newsletter_uncovering_ai",
  "source_name": "Uncovering AI",
  "collected_at": "2026-04-06T09:00:00+09:00",
  "skipped": false,
  "newsletters": [
    {
      "subject": "메일 제목",
      "received_at": "2026-04-05T08:00:00+09:00",
      "summary": "핵심 내용 3-5문장 요약",
      "topics": ["토픽1", "토픽2"]
    }
  ]
}
```

### 스킵된 경우

```json
{
  "source_id": "newsletter_uncovering_ai",
  "source_name": "Uncovering AI",
  "collected_at": "2026-04-06T09:00:00+09:00",
  "skipped": true,
  "reason": "최근 7일 내 해당 뉴스레터 없음"
}
```

## 주의사항

- `optional: true`인 소스는 메일이 없어도 전체 수집 파이프라인에 영향을 주지 않는다.
- gog 인증이 안 되어 있으면 사용자에게 `gog auth` 안내를 출력하고 스킵한다.
- 메일 본문이 HTML인 경우 텍스트만 추출하여 요약한다.
