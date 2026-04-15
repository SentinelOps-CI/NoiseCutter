# Install pinned Syft on Windows from GitHub release (SHA-256 verified).
param(
    [string]$SyftVersion = "1.16.0",
    [string]$InstallDir = "bin"
)

$ErrorActionPreference = "Stop"
$base = "https://github.com/anchore/syft/releases/download/v$SyftVersion"
$checksumsUrl = "$base/syft_${SyftVersion}_checksums.txt"
$zipName = "syft_${SyftVersion}_windows_amd64.zip"
$zipUrl = "$base/$zipName"

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
$checksumsPath = Join-Path $InstallDir "syft_checksums.txt"
Invoke-WebRequest -Uri $checksumsUrl -OutFile $checksumsPath

$expectedLine = (Get-Content $checksumsPath | Where-Object { $_ -match [regex]::Escape($zipName) })
if (-not $expectedLine) { throw "install-syft: no checksum line for $zipName" }
$expectedHash = ($expectedLine -split '\s+')[0]

$zipPath = Join-Path $InstallDir $zipName
Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
$actualHash = (Get-FileHash -Algorithm SHA256 -Path $zipPath).Hash.ToLowerInvariant()
if ($actualHash -ne $expectedHash) {
    throw "install-syft: checksum mismatch for $zipPath"
}

Expand-Archive -Path $zipPath -DestinationPath $InstallDir -Force
Remove-Item $zipPath -Force
Write-Host "install-syft: installed syft v$SyftVersion to $InstallDir"
