#!/usr/bin/env bash
# Figma Extract Tokens 스킬 설치 스크립트

set -e

FIGMA_SKILLS_DIR="$HOME/.claude/plugins/cache/claude-plugins-official/figma"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="figma-extract-tokens"

echo "📦 Figma Extract Tokens 스킬 설치 중..."

# Figma 플러그인 버전 디렉토리 자동 감지
FIGMA_VERSION_DIR=$(find "$FIGMA_SKILLS_DIR" -maxdepth 1 -type d -name "[0-9]*" | sort -V | tail -1)

if [ -z "$FIGMA_VERSION_DIR" ]; then
  echo "❌ Figma MCP 플러그인이 설치되어 있지 않습니다."
  echo "   Claude Code에서 Figma MCP 서버를 먼저 연결해주세요."
  exit 1
fi

TARGET_DIR="$FIGMA_VERSION_DIR/skills/$SKILL_NAME"

echo "  감지된 Figma 플러그인: $FIGMA_VERSION_DIR"

# 기존 설치 확인
if [ -d "$TARGET_DIR" ]; then
  echo "  기존 설치 발견 — 업데이트합니다."
  rm -rf "$TARGET_DIR"
fi

# 복사
mkdir -p "$TARGET_DIR/scripts"
cp "$SCRIPT_DIR/SKILL.md" "$TARGET_DIR/SKILL.md"
cp "$SCRIPT_DIR/scripts/"*.js "$TARGET_DIR/scripts/"

echo ""
echo "✅ 설치 완료: $TARGET_DIR"
echo ""
echo "─────────────────────────────────────────────"
echo "사용법:"
echo "  1. Claude Code에서 Figma MCP 서버가 연결되어 있어야 합니다"
echo "  2. Figma 파일 URL과 함께 '토큰 추출해줘' 라고 요청하세요"
echo "─────────────────────────────────────────────"
