#!/usr/bin/env bash
# Pinocchio 스킬 설치 스크립트

set -e

SKILL_DIR="$HOME/.claude/skills/pinocchio"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 Pinocchio 스킬 설치 중..."

mkdir -p "$SKILL_DIR"
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"

echo "✅ 설치 완료: $SKILL_DIR/SKILL.md"
echo ""
echo "─────────────────────────────────────────────"
echo "사용 방법:"
echo "  /pinocchio 또는 '페르소나 만들어줘' 라고 입력하세요."
echo "─────────────────────────────────────────────"
