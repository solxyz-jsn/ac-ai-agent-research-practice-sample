Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$distDir = Join-Path $projectRoot "dist"
$packageDir = Join-Path $distDir ("package_" + [guid]::NewGuid().ToString("N"))
$zipPath = Join-Path $distDir "agentcore_github_agent.zip"
$sourceRoot = Join-Path $projectRoot "src"
$requirementsPath = Join-Path $projectRoot "requirements.txt"
$uvCacheDir = Join-Path $projectRoot ".uv-cache"

if (-not (Test-Path $sourceRoot)) {
    throw "src directory was not found: $sourceRoot"
}

if (-not (Test-Path $requirementsPath)) {
    throw "requirements.txt was not found: $requirementsPath"
}

New-Item -ItemType Directory -Force $distDir | Out-Null

New-Item -ItemType Directory -Force $packageDir | Out-Null

Copy-Item -Recurse (Join-Path $sourceRoot '*') $packageDir

$readmePath = Join-Path $projectRoot 'README.md'
if (Test-Path $readmePath) {
    Copy-Item $readmePath $packageDir
}

$env:UV_CACHE_DIR = $uvCacheDir
$env:UV_LINK_MODE = "copy"

uv pip install `
    --python-platform aarch64-manylinux2014 `
    --python-version 3.14 `
    --target $packageDir `
    --only-binary=:all: `
    -r $requirementsPath

Start-Sleep -Seconds 5

if (Test-Path $zipPath) {
    Remove-Item -Force $zipPath
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($packageDir, $zipPath)
