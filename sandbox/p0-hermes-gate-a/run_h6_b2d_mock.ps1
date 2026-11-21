# Run the standalone mock candidate using only the local Linux daemon.
$ErrorActionPreference = 'Stop'
$project = 'h6b2d-' + [Guid]::NewGuid().ToString('N').Substring(0, 12)
$tempRoot = [IO.Path]::TrimEndingDirectorySeparator([IO.Path]::GetFullPath([IO.Path]::GetTempPath()))
$scratch = Join-Path $tempRoot $project
$dockerArgs = @('--context', 'desktop-linux')
$composeArgs = $dockerArgs + @('compose', '-p', $project, '-f', (Join-Path $PSScriptRoot 'compose.h6-b2-d-mock.yaml'))
$prior = [Environment]::GetEnvironmentVariable('TTD_H6_B2_D_FAKE_LEDGER', 'Process')

function Invoke-Docker([string[]]$Arguments) {
    & docker @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Docker failed (exit $LASTEXITCODE)" }
}

function Invoke-Fixture([string[]]$Arguments) {
    Invoke-Docker ($composeArgs + $Arguments)
}

function Require($Condition, [string]$Reason) {
    if (-not $Condition) { throw $Reason }
}

$storage = @{
    init = @('ledger:rw', 'ipc:rw', 'auth:rw', 'guard-auth:rw', 'test-auth:rw')
    writer = @('ledger:rw', 'ipc:rw', 'auth:ro')
    guard = @('ipc:ro', 'auth:ro', 'guard-auth:ro')
    tests = @('test-auth:ro')
}
$sources = @('h6_b2d_mock_test.py', 'h6_ipc_auth.py', 'h6_writer.py', 'guard.py', 'one_shot.py', 'mock_contract.py')
$targets = @{
    ipc = '/opt/ttd/h6-b2d-ipc'
    auth = '/run/h6-b2d-auth'
    'guard-auth' = '/run/secrets'
    'test-auth' = '/run/h6-b2d-test-auth'
}
$ledgerTarget = '/opt/ttd/mock-ledger'
$image = 'python@sha256:c5ba3deef00c7758561a0f03c26f44f10589263d40e732b8748e0d1f38f6dd89'

New-Item -ItemType Directory -Path $scratch | Out-Null
[Environment]::SetEnvironmentVariable('TTD_H6_B2_D_FAKE_LEDGER', $scratch, 'Process')
$validated = $false
try {
    $render = Invoke-Fixture @('config', '--format', 'json') | Out-String | ConvertFrom-Json -AsHashtable
    Require ($render.name -eq $project -and $render.services.Count -eq 4 -and $render.volumes.Count -eq 4) 'Unexpected project'
    foreach ($volume in $render.volumes.Keys) {
        $definition = $render.volumes[$volume]
        Require ($targets.ContainsKey($volume) -and $definition.name -eq ($project + '_' + $volume) -and
            -not $definition.external -and -not $definition.driver_opts) 'Unexpected volume definition'
    }
    foreach ($name in $render.services.Keys) {
        $service = $render.services[$name]
        Require ($storage.ContainsKey($name) -and $service.image -eq $image -and $service.pull_policy -eq 'never' -and
            $service.user -eq '0:0' -and $service.network_mode -eq 'none' -and $service.read_only -and
            ($service.cap_drop -join ',') -eq 'ALL' -and $service.security_opt -contains 'no-new-privileges:true' -and
            -not ($service.ports -or $service.secrets -or $service.privileged -or $service.cap_add -or $service.devices -or
                $service.pid -or $service.ipc -or $service.env_file -or $service.container_name)) "Unexpected service settings in $name"
        $environmentCount = if ($name -eq 'guard') { 1 } else { 0 }
        Require ($service.environment.Count -eq $environmentCount -and
            ($name -ne 'guard' -or $service.environment.TTD_H6_B2_D_SOCKET -eq '/opt/ttd/h6-b2d-ipc/writer.sock')) "Unexpected environment in $name"
        $actual = @(foreach ($mount in $service.volumes) {
            if ($mount.type -eq 'volume') {
                $target = if ($mount.source -eq 'test-auth' -and $name -eq 'tests') { $targets.auth } else { $targets[$mount.source] }
                Require ($target -eq $mount.target) "Wrong volume target in $name"
                $mode = if ($mount.read_only) { 'ro' } else { 'rw' }
                "$($mount.source):$mode"
            } elseif ($mount.target -eq $ledgerTarget) {
                Require ($mount.type -eq 'bind' -and -not $mount.read_only -and
                    [IO.Path]::GetFullPath($mount.source) -eq $scratch -and $mount.bind.propagation -eq 'rprivate' -and
                    $mount.bind.create_host_path -eq $false) "Wrong fake ledger bind in $name"
                'ledger:rw'
            } else {
                $leaf = [IO.Path]::GetFileName($mount.source)
                $source = Join-Path $PSScriptRoot $leaf
                $target = "/opt/ttd/$leaf"
                if ($name -eq 'tests' -and $leaf -eq 'adapter.py') {
                    $source = Join-Path $PSScriptRoot '../p0-level2/adapter.py'
                    $target = '/opt/ttd/level2-adapter.py'
                } else {
                    Require ($leaf -in $sources) "Unexpected bind source in $name"
                }
                Require ($mount.type -eq 'bind' -and $mount.read_only -and $mount.target -eq $target -and
                    [IO.Path]::GetFullPath($mount.source) -eq [IO.Path]::GetFullPath($source) -and
                    (Test-Path -LiteralPath $source -PathType Leaf)) "Wrong file bind in $name"
            }
        })
        Require ((($actual | Sort-Object) -join ',') -ceq (($storage[$name] | Sort-Object) -join ',')) "Wrong mount set in $name"
    }
    $validated = $true
    Write-Output 'PASS rendered standalone mock Compose scope'

    Invoke-Fixture @('run', '--rm', '--no-deps', '-T', 'init')
    Invoke-Fixture @('up', '-d', '--wait', '--no-deps', 'writer')
    Invoke-Fixture @('up', '-d', '--wait', '--no-deps', 'guard')
    foreach ($service in @('writer', 'guard')) {
        $id = Invoke-Fixture @('ps', '-q', $service)
        $inspect = @(Invoke-Docker ($dockerArgs + @('inspect', $id)) | Out-String | ConvertFrom-Json -AsHashtable)[0]
        $hostConfig = $inspect.HostConfig
        Require ($inspect.Config.User -eq '0:0' -and $hostConfig.NetworkMode -eq 'none' -and
            $hostConfig.ReadonlyRootfs -and $hostConfig.CapDrop -contains 'ALL' -and $hostConfig.PortBindings.Count -eq 0 -and
            $hostConfig.SecurityOpt -contains 'no-new-privileges:true') "Runtime settings drift in $service"
        Require (@($inspect.Mounts | Where-Object { $_.Destination -eq $targets.auth -and -not $_.RW }).Count -eq 1) 'IPC key mount is not read-only'
        $writable = @($inspect.Mounts | Where-Object RW)
        if ($service -eq 'writer') {
            Require ($writable.Count -eq 2 -and
                @($writable | Where-Object { $_.Destination -eq $ledgerTarget -and $_.Type -eq 'bind' -and
                    $_.Propagation -eq 'rprivate' }).Count -eq 1 -and
                @($writable | Where-Object { $_.Destination -eq $targets.ipc }).Count -eq 1 -and
                @($inspect.Mounts | Where-Object { $_.Destination -eq '/run/secrets' }).Count -eq 0) 'Writer mount drift'
        } else {
            Require ($writable.Count -eq 0 -and @($inspect.Mounts | Where-Object { $_.Destination -eq $ledgerTarget }).Count -eq 0) 'Guard mount drift'
        }
    }
    $check = "import json,urllib.request; h=json.load(urllib.request.urlopen('http://127.0.0.1:8081/healthz')); assert h['mode']=='h6_b2_d_mock' and h['ledger']['kill_switch'] and h['ledger']['attempts']==1"
    Invoke-Fixture @('exec', '-T', 'guard', 'python', '-B', '-c', $check)
    Write-Output 'PASS actual Guard/writer entrypoints and signed snapshot'
    $probe = @'
import os, socket
from h6_ipc_auth import KEY_PATH, SOCKET_PATH, send
import time
assert (os.getuid(), os.getgid()) == (0, 23060)
assert len(KEY_PATH.read_bytes()) == 32
with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as conn:
    conn.connect(str(SOCKET_PATH))
    try:
        send(conn, time.monotonic() + 2, client=os.urandom(32).hex())
        assert conn.recv(4097) == b''
    except (BrokenPipeError, ConnectionResetError):
        pass
'@
    Invoke-Fixture @('exec', '-T', '--user', '0:23060', '-w', '/opt/ttd', 'guard', 'python', '-B', '-c', $probe)
    Write-Output 'PASS actual writer rejects UID 0 peer with wrong GID and correct key'
    Invoke-Fixture @('run', '--rm', '--no-deps', '-T', 'tests')
    Invoke-Fixture @('stop', 'writer')
    $unavailable = @'
import urllib.error, urllib.request
try:
    urllib.request.urlopen('http://127.0.0.1:8081/healthz', timeout=2)
    raise AssertionError('Guard stayed healthy without its writer')
except urllib.error.HTTPError as exc:
    assert exc.code == 503
'@
    Invoke-Fixture @('exec', '-T', 'guard', 'python', '-B', '-c', $unavailable)
    Write-Output 'PASS Guard fails closed after writer stop'
} finally {
    try {
        if ($validated) {
            Invoke-Fixture @('down', '--volumes', '--remove-orphans')
            foreach ($group in @('ps', 'volume', 'network')) {
                $query = if ($group -eq 'ps') { @('ps', '-aq') } else { @($group, 'ls', '-q') }
                Require (-not (Invoke-Docker ($dockerArgs + $query + @('--filter', "label=com.docker.compose.project=$project")))) "Fixture $group resources remain"
            }
        }
        $resolved = (Resolve-Path -LiteralPath $scratch).Path
        Require ($resolved -eq $scratch -and (Split-Path -Parent $resolved) -eq $tempRoot -and
            (Split-Path -Leaf $resolved) -eq $project) 'Refusing to delete unexpected path'
        Remove-Item -LiteralPath $resolved -Recurse -Force
        Require (-not (Test-Path -LiteralPath $resolved)) 'Fixture ledger directory remains'
        Write-Output 'PASS fixture resources removed'
    } finally {
        [Environment]::SetEnvironmentVariable('TTD_H6_B2_D_FAKE_LEDGER', $prior, 'Process')
    }
}
