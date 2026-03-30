#!/usr/bin/env bash
# Next Titan 스킬 설치 스크립트

set -e

SKILL_DIR="$HOME/.claude/skills/nexttitan"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 Next Titan 스킬 설치 중..."

mkdir -p "$SKILL_DIR"
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"

echo "✅ 설치 완료: $SKILL_DIR/SKILL.md"
echo ""
echo "─────────────────────────────────────────────"
echo "다음 환경 변수를 ~/.zshrc 또는 ~/.bashrc에 추가하세요:"
echo ""
echo "  export NEXT_TITAN_API_KEY=\"ntk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\""
echo "  export NEXT_TITAN_BASE_URL=\"https://your-nexttitan-domain.com\""
echo ""
echo "추가 후 실행:"
echo "  source ~/.zshrc"
echo "─────────────────────────────────────────────"
