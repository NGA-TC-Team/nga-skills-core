#!/usr/bin/env python3
"""
Threads API 게시/예약 게시 스크립트.

환경변수:
  THREADS_ACCESS_TOKEN  - Threads API 장기 액세스 토큰
  THREADS_USER_ID       - Threads 사용자 ID

사용법:
  # 즉시 게시
  python publish_thread.py --text "게시할 내용"

  # 예약 게시 (로컬 스케줄러가 지정 시각에 실행)
  python publish_thread.py --text "게시할 내용" --schedule "2026-04-07T09:00:00+09:00"

  # 프로필 확인
  python publish_thread.py --profile

  # 컨테이너 상태 확인
  python publish_thread.py --status <container_id>
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

API_BASE = "https://graph.threads.net/v1.0"


def get_env():
    token = os.environ.get("THREADS_ACCESS_TOKEN")
    user_id = os.environ.get("THREADS_USER_ID")
    if not token:
        print("ERROR: THREADS_ACCESS_TOKEN 환경변수가 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)
    if not user_id:
        print("ERROR: THREADS_USER_ID 환경변수가 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)
    return token, user_id


def api_request(endpoint: str, params: dict | None = None, method: str = "GET") -> dict:
    token, _ = get_env()
    url = f"{API_BASE}/{endpoint}"

    if method == "GET":
        if params:
            params["access_token"] = token
        else:
            params = {"access_token": token}
        qs = urllib.parse.urlencode(params)
        url = f"{url}?{qs}"
        req = urllib.request.Request(url)
    else:
        data = params or {}
        data["access_token"] = token
        encoded = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(url, data=encoded, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"API Error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def get_profile() -> dict:
    """현재 토큰의 Threads 프로필을 조회한다."""
    return api_request("me", {
        "fields": "id,username,name,threads_profile_picture_url,threads_biography"
    })


def create_container(text: str, reply_control: str = "everyone") -> str:
    """텍스트 미디어 컨테이너를 생성한다."""
    _, user_id = get_env()
    result = api_request(f"{user_id}/threads", {
        "media_type": "TEXT",
        "text": text,
        "reply_control": reply_control,
    }, method="POST")
    return result["id"]


def check_container_status(container_id: str) -> str:
    """컨테이너의 처리 상태를 확인한다."""
    result = api_request(container_id, {"fields": "status,error_message"})
    return result.get("status", "UNKNOWN")


def publish(container_id: str) -> str:
    """컨테이너를 게시한다."""
    _, user_id = get_env()
    result = api_request(f"{user_id}/threads_publish", {
        "creation_id": container_id,
    }, method="POST")
    return result["id"]


def post_text(text: str, reply_control: str = "everyone", max_wait: int = 30) -> dict:
    """텍스트를 Threads에 게시한다. 컨테이너 생성 → 상태 확인 → 게시."""
    container_id = create_container(text, reply_control)
    print(f"Container created: {container_id}")

    # 컨테이너 처리 완료 대기
    for i in range(max_wait):
        status = check_container_status(container_id)
        if status == "FINISHED":
            break
        if status == "ERROR":
            print("ERROR: 컨테이너 처리 실패", file=sys.stderr)
            sys.exit(1)
        print(f"  Status: {status}, waiting... ({i+1}/{max_wait})")
        time.sleep(1)
    else:
        print(f"WARNING: {max_wait}초 후에도 FINISHED 아님, 게시 시도합니다.")

    media_id = publish(container_id)
    print(f"Published! media_id: {media_id}")
    return {"container_id": container_id, "media_id": media_id, "status": "published"}


def main():
    parser = argparse.ArgumentParser(description="Threads API 게시 스크립트")
    parser.add_argument("--text", help="게시할 텍스트")
    parser.add_argument("--reply-control", default="everyone",
                        choices=["everyone", "accounts_you_follow", "mentioned_only"],
                        help="답글 허용 범위")
    parser.add_argument("--schedule", help="예약 시각 (ISO 8601). 이 시각까지 대기 후 게시.")
    parser.add_argument("--profile", action="store_true", help="프로필 조회")
    parser.add_argument("--status", help="컨테이너 상태 확인 (container_id)")
    parser.add_argument("--json", action="store_true", help="결과를 JSON으로 출력")

    args = parser.parse_args()

    if args.profile:
        profile = get_profile()
        if args.json:
            print(json.dumps(profile, ensure_ascii=False, indent=2))
        else:
            print(f"ID: {profile.get('id')}")
            print(f"Username: @{profile.get('username')}")
            print(f"Name: {profile.get('name')}")
            print(f"Bio: {profile.get('threads_biography', 'N/A')}")
        return

    if args.status:
        status = check_container_status(args.status)
        print(f"Container {args.status}: {status}")
        return

    if not args.text:
        parser.error("--text 또는 --profile 중 하나를 지정해야 합니다.")

    if args.schedule:
        # 예약 게시: 지정 시각까지 대기
        target = datetime.fromisoformat(args.schedule)
        now = datetime.now(timezone.utc)
        if target.tzinfo is None:
            target = target.replace(tzinfo=timezone.utc)
        wait_seconds = (target - now).total_seconds()
        if wait_seconds > 0:
            print(f"예약 게시: {target.isoformat()} 까지 {wait_seconds:.0f}초 대기")
            # 컨테이너 TTL이 24시간이므로, 24시간 이내만 허용
            if wait_seconds > 86400:
                print("ERROR: 예약 시각이 24시간 초과입니다. 컨테이너 TTL 제한으로 불가.", file=sys.stderr)
                sys.exit(1)
            time.sleep(wait_seconds)

    result = post_text(args.text, args.reply_control)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
