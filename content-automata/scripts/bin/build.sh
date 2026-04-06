#!/usr/bin/env bash
# nca 바이너리 빌드 스크립트
# macOS Intel 또는 Windows에서 실행하여 해당 플랫폼 바이너리를 생성한다.
#
# 사용법:
#   ./build.sh                      # 현재 플랫폼용 빌드
#   ./build.sh --install            # 빌드 후 ~/.local/bin/nca에 설치
#
# 필요: Rust toolchain (https://rustup.rs)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 프로젝트 소스 경로 — Cargo.toml이 있는 곳
# 소스가 없으면 안내
PROJECT_DIR=""
for candidate in \
    "$HOME/Desktop/ProjectMac/NextGenAI/nga-tc/nga-content-automata" \
    "$SKILL_DIR/../../nga-content-automata" \
    "$(pwd)"; do
    if [ -f "$candidate/Cargo.toml" ]; then
        PROJECT_DIR="$candidate"
        break
    fi
done

if [ -z "$PROJECT_DIR" ]; then
    echo "ERROR: nga-content-automata 프로젝트를 찾을 수 없습니다."
    echo "Cargo.toml이 있는 프로젝트 디렉토리에서 이 스크립트를 실행하세요."
    exit 1
fi

echo "프로젝트: $PROJECT_DIR"
echo "빌드 시작..."

cd "$PROJECT_DIR"
cargo build --release

# 플랫폼 감지
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS-$ARCH" in
    Darwin-arm64)  SUFFIX="darwin-arm64" ;;
    Darwin-x86_64) SUFFIX="darwin-x64" ;;
    Linux-x86_64)  SUFFIX="linux-x64" ;;
    MINGW*|MSYS*)  SUFFIX="windows-x64.exe" ;;
    *)             SUFFIX="$OS-$ARCH" ;;
esac

BIN_SRC="$PROJECT_DIR/target/release/nca"
BIN_DST="$SCRIPT_DIR/nca-$SUFFIX"

cp "$BIN_SRC" "$BIN_DST"
chmod +x "$BIN_DST"
echo "바이너리 생성: $BIN_DST ($(du -h "$BIN_DST" | cut -f1))"

# --install 옵션
if [ "${1:-}" = "--install" ]; then
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
    cp "$BIN_DST" "$INSTALL_DIR/nca"
    chmod +x "$INSTALL_DIR/nca"
    echo "설치 완료: $INSTALL_DIR/nca"
    echo "PATH에 $INSTALL_DIR이 포함되어 있는지 확인하세요."
fi
