#!/usr/bin/env python3
"""
Perplexity API 기반 팩트 체크 스크립트.
수집된 콘텐츠 풀의 주요 주장을 검증하고, 신뢰도 점수와 출처를 부여한다.

환경변수:
  PERPLEXITY_API_KEY  — Perplexity API 키 (pplx-...)

사용법:
  # 단일 주장 팩트 체크
  python fact_check.py --claim "OpenAI가 GPT-5를 2026년 3월에 출시했다"

  # JSON 파일 일괄 팩트 체크 (수집 결과)
  python fact_check.py --file collected_items.json

  # SQLite DB에서 직접 팩트 체크 (content_pool 테이블)
  python fact_check.py --db ~/.claude/skills/content-automata/data/content_pool.db

  # 결과를 JSON으로 출력
  python fact_check.py --db ... --json
"""

import argparse
import json
import os
import sqlite3
import sys
import urllib.request
import urllib.error

API_URL = "https://api.perplexity.ai/v1/sonar"
# sonar: 가볍고 빠름, sonar-pro: 더 깊은 검색
MODEL = "sonar"

SYSTEM_PROMPT = """\
You are a fact-checker for AI/automation industry news.
For each claim, do the following:
1. Verify whether the claim is accurate, partially accurate, or inaccurate.
2. Provide a confidence score from 0 to 100.
3. Cite specific sources that support or contradict the claim.
4. Note any important context or nuance.

Respond in JSON format:
{
  "verdict": "accurate" | "partially_accurate" | "inaccurate" | "unverifiable",
  "confidence": 0-100,
  "explanation": "Brief explanation in Korean",
  "sources": ["url1", "url2"],
  "context": "Additional context if needed, in Korean"
}

Respond ONLY with the JSON object, no markdown fences or extra text.\
"""


def get_api_key():
    key = os.environ.get("PERPLEXITY_API_KEY", "")
    if not key:
        return None
    return key


def fact_check_claim(claim: str, api_key: str) -> dict:
    """단일 주장을 Perplexity API로 팩트 체크한다."""
    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"다음 주장을 팩트 체크하라:\n\n{claim}"},
        ],
        "max_tokens": 1000,
        "temperature": 0.1,
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {
            "verdict": "error",
            "confidence": 0,
            "explanation": f"API 오류 {e.code}: {body[:200]}",
            "sources": [],
            "context": "",
        }
    except Exception as e:
        return {
            "verdict": "error",
            "confidence": 0,
            "explanation": f"요청 실패: {e}",
            "sources": [],
            "context": "",
        }

    content = data["choices"][0]["message"]["content"]
    # API 응답의 citations 필드도 활용
    api_citations = data.get("citations", [])

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 텍스트 응답 그대로 반환
        result = {
            "verdict": "unverifiable",
            "confidence": 0,
            "explanation": content[:500],
            "sources": api_citations,
            "context": "",
        }

    # API citations를 sources에 병합
    if api_citations:
        existing = set(result.get("sources", []))
        for c in api_citations:
            if c not in existing:
                result.setdefault("sources", []).append(c)

    return result


def extract_claims_from_items(items: list[dict]) -> list[dict]:
    """수집된 콘텐츠 아이템에서 팩트 체크 대상 주장을 추출한다."""
    claims = []
    for item in items:
        title = item.get("title", "")
        summary = item.get("summary", "") or item.get("text", "")
        source_id = item.get("source_id", "") or item.get("id", "")

        if title or summary:
            claim_text = title
            if summary:
                claim_text = f"{title}\n{summary}" if title else summary
            claims.append({
                "source_id": source_id,
                "original_title": title,
                "claim": claim_text.strip(),
            })
    return claims


def load_from_db(db_path: str) -> list[dict]:
    """SQLite content_pool 테이블에서 미체크 콘텐츠를 로드한다."""
    db_path = os.path.expanduser(db_path)
    if not os.path.exists(db_path):
        print(f"DB 파일 없음: {db_path}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # fact_check_result 컬럼이 없으면 추가
    try:
        conn.execute("ALTER TABLE content_pool ADD COLUMN fact_check_result TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # 이미 존재

    rows = conn.execute(
        "SELECT id, title, summary, source_id FROM content_pool "
        "WHERE fact_check_result IS NULL "
        "ORDER BY created_at DESC"
    ).fetchall()

    items = [dict(r) for r in rows]
    conn.close()
    return items


def save_to_db(db_path: str, item_id: int, result: dict):
    """팩트 체크 결과를 DB에 저장한다."""
    db_path = os.path.expanduser(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "UPDATE content_pool SET fact_check_result = ? WHERE id = ?",
        (json.dumps(result, ensure_ascii=False), item_id),
    )
    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Perplexity API 팩트 체크")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--claim", help="단일 주장 텍스트")
    group.add_argument("--file", help="수집 결과 JSON 파일 경로")
    group.add_argument("--db", help="SQLite DB 경로")
    parser.add_argument("--json", action="store_true", help="JSON 출력")
    args = parser.parse_args()

    api_key = get_api_key()
    if not api_key:
        msg = {"skipped": True, "reason": "PERPLEXITY_API_KEY 환경변수 미설정"}
        if args.json:
            print(json.dumps(msg, ensure_ascii=False))
        else:
            print("⏭ 팩트 체크 스킵: PERPLEXITY_API_KEY 환경변수가 설정되지 않음", file=sys.stderr)
        sys.exit(0)

    # 단일 주장
    if args.claim:
        result = fact_check_claim(args.claim, api_key)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_result(args.claim, result)
        return

    # JSON 파일 일괄
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            items = json.load(f)
        if isinstance(items, dict):
            items = items.get("items", items.get("posts", [items]))
        claims = extract_claims_from_items(items)
        results = process_claims(claims, api_key, args.json)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    # DB 모드
    if args.db:
        items = load_from_db(args.db)
        if not items:
            msg = {"skipped": True, "reason": "팩트 체크 대상 콘텐츠 없음"}
            if args.json:
                print(json.dumps(msg, ensure_ascii=False))
            else:
                print("팩트 체크 대상 콘텐츠가 없음")
            return

        claims = extract_claims_from_items(items)
        results = []
        for item, claim_info in zip(items, claims):
            result = fact_check_claim(claim_info["claim"], api_key)
            save_to_db(args.db, item["id"], result)
            results.append({
                "content_pool_id": item["id"],
                "title": item.get("title", ""),
                **result,
            })
            if not args.json:
                print_result(claim_info["claim"], result)
                print()

        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))

        # 요약 통계
        stats = summarize(results)
        if not args.json:
            print_stats(stats)
        return


def process_claims(claims: list[dict], api_key: str, json_mode: bool) -> list[dict]:
    """주장 목록을 순차 팩트 체크한다."""
    results = []
    for c in claims:
        result = fact_check_claim(c["claim"], api_key)
        entry = {**c, **result}
        results.append(entry)
        if not json_mode:
            print_result(c["claim"], result)
            print()
    if not json_mode:
        print_stats(summarize(results))
    return results


def summarize(results: list[dict]) -> dict:
    """팩트 체크 결과 요약 통계."""
    total = len(results)
    verdicts = {}
    for r in results:
        v = r.get("verdict", "unknown")
        verdicts[v] = verdicts.get(v, 0) + 1
    avg_confidence = (
        sum(r.get("confidence", 0) for r in results) / total if total else 0
    )
    return {
        "total": total,
        "verdicts": verdicts,
        "avg_confidence": round(avg_confidence, 1),
    }


def print_result(claim: str, result: dict):
    """팩트 체크 결과를 사람이 읽을 수 있는 형태로 출력한다."""
    verdict_map = {
        "accurate": "✅ 정확",
        "partially_accurate": "⚠️ 부분 정확",
        "inaccurate": "❌ 부정확",
        "unverifiable": "❓ 검증 불가",
        "error": "💥 오류",
    }
    v = verdict_map.get(result.get("verdict", ""), result.get("verdict", ""))
    conf = result.get("confidence", 0)
    expl = result.get("explanation", "")

    print(f"주장: {claim[:100]}...")
    print(f"판정: {v} (신뢰도: {conf}%)")
    print(f"설명: {expl}")
    if result.get("sources"):
        print(f"출처: {', '.join(result['sources'][:3])}")


def print_stats(stats: dict):
    """요약 통계를 출력한다."""
    print("=" * 50)
    print(f"팩트 체크 완료: {stats['total']}건")
    print(f"평균 신뢰도: {stats['avg_confidence']}%")
    for v, count in stats["verdicts"].items():
        print(f"  {v}: {count}건")


if __name__ == "__main__":
    main()
