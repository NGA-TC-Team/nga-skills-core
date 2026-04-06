# nca 바이너리 빌드 스크립트 (Windows PowerShell)
# 사용법:
#   .\build.ps1                 # 현재 플랫폼용 빌드
#   .\build.ps1 -Install        # 빌드 후 설치
#
# 필요: Rust toolchain (https://rustup.rs)

param(
    [switch]$Install
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillDir = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# 프로젝트 소스 경로 탐색
$ProjectDir = $null
$Candidates = @(
    (Join-Path $env:USERPROFILE "Desktop\ProjectMac\NextGenAI\nga-tc\nga-content-automata"),
    (Join-Path $SkillDir "..\nga-content-automata"),
    (Get-Location).Path
)

foreach ($candidate in $Candidates) {
    if (Test-Path (Join-Path $candidate "Cargo.toml")) {
        $ProjectDir = $candidate
        break
    }
}

if (-not $ProjectDir) {
    Write-Error "nga-content-automata 프로젝트를 찾을 수 없습니다. Cargo.toml이 있는 디렉토리에서 실행하세요."
    exit 1
}

Write-Host "프로젝트: $ProjectDir"
Write-Host "빌드 시작..."

Push-Location $ProjectDir
try {
    cargo build --release
} finally {
    Pop-Location
}

# 바이너리 복사
$BinSrc = Join-Path $ProjectDir "target\release\nca.exe"
$BinDst = Join-Path $ScriptDir "nca-windows-x64.exe"

if (-not (Test-Path $BinSrc)) {
    Write-Error "빌드된 바이너리를 찾을 수 없습니다: $BinSrc"
    exit 1
}

Copy-Item $BinSrc $BinDst -Force
$size = (Get-Item $BinDst).Length / 1MB
Write-Host "바이너리 생성: $BinDst ($([math]::Round($size, 1))MB)"

# --Install 옵션
if ($Install) {
    $InstallDir = Join-Path $env:LOCALAPPDATA "bin"
    if (-not (Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    }
    $InstallPath = Join-Path $InstallDir "nca.exe"
    Copy-Item $BinDst $InstallPath -Force
    Write-Host "설치 완료: $InstallPath"

    # PATH에 포함되어 있는지 확인
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($currentPath -notlike "*$InstallDir*") {
        Write-Host ""
        Write-Host "PATH에 $InstallDir 을 추가하려면:" -ForegroundColor Yellow
        Write-Host "  [Environment]::SetEnvironmentVariable('PATH', `"`$env:PATH;$InstallDir`", 'User')"
    }
}
