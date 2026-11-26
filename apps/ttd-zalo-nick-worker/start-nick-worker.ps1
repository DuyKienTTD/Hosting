#Requires -Version 5.1
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot
$config = Get-Content -LiteralPath (Join-Path $root 'config.json') -Raw | ConvertFrom-Json
$secure = Get-Content -LiteralPath (Join-Path $root 'credential.dpapi') -Raw | ConvertTo-SecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $env:NICK_WORKER_AUTH = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    $env:NICK_SERVER_URL = 'wss://cskh.thuanthanhdat.com.vn/nick-worker/socket'
    $env:NICK_WEB_URL = 'https://chat.zalo.me'
    $env:NICK_PROFILE_ROOT = Join-Path $root 'profile'
    $env:NICK_SELECTOR_FILE = Join-Path $root 'selectors.json'
    $env:NICK_SMOKE_ONLY = '1'
    $env:NICK_SMOKE_PEERS = @($config.smokePeers) -join ','
    & $config.node (Join-Path $PSScriptRoot 'src\main.js')
    exit $LASTEXITCODE
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    Remove-Item Env:NICK_WORKER_AUTH -ErrorAction SilentlyContinue
}
