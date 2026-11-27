# Run the exact local synthetic topology after validating the rendered config.
$ErrorActionPreference = 'Stop'
$project = 'h6b2c-' + [Guid]::NewGuid().ToString('N').Substring(0, 12)
$composeFile = Join-Path $PSScriptRoot 'compose.h6-b2-c-fixture.yaml'
$dockerArgs = @('--context', 'desktop-linux')
$composeArgs = $dockerArgs + @('compose', '-p', $project, '-f', $composeFile)

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

$expected = @{
    init = @('ledger:rw', 'acl:rw', 'ipc:rw', 'auth:rw')
    writer = @('ledger:rw', 'ipc:rw', 'auth:ro')
    level2 = @('ledger:rw')
    guard = @('ipc:ro', 'auth:ro')
    'same-uid' = @('ipc:ro')
    'wrong-gid' = @('ipc:ro', 'auth:ro')
    unmounted = @()
    'acl-nonroot' = @('acl:rw')
    'acl-level2' = @('acl:rw')
    faults = @('ledger:rw')
}
$sourceFiles = @('h6_b2c_identity_test', 'h6_writer', 'h6_b2a_ledger_test', 'h6_stage_a_test',
    'one_shot', 'mock_contract', 'bridge', 'guard', 'one_shot_linux_test')
$targets = @{
    ledger = '/case/mock-ledger'
    acl = '/case/acl'
    ipc = '/case/ipc'
    auth = '/case/auth'
}
$pin = 'python@sha256:c5ba3deef00c7758561a0f03c26f44f10589263d40e732b8748e0d1f38f6dd89'
$scratch = [IO.Path]::GetFullPath((Join-Path ([IO.Path]::GetTempPath()) $project))
$priorLedger = [Environment]::GetEnvironmentVariable('TTD_H6_B2_C_FAKE_LEDGER', 'Process')
New-Item -ItemType Directory -Path $scratch | Out-Null
[Environment]::SetEnvironmentVariable('TTD_H6_B2_C_FAKE_LEDGER', $scratch, 'Process')
$validated = $false
try {
    $render = Invoke-Fixture @('config', '--format', 'json') | Out-String | ConvertFrom-Json -AsHashtable
    Require ($render.name -eq $project -and $render.services.Count -eq $expected.Count) 'Wrong project or services'
    Require ($render.volumes.Count -eq ($targets.Count - 1)) 'Wrong volume set'
    foreach ($volume in $render.volumes.Keys) {
        Require ($targets.ContainsKey($volume) -and $render.volumes[$volume].name -eq "${project}_$volume" -and
            -not $render.volumes[$volume].external -and -not $render.volumes[$volume].driver_opts) 'Unexpected volume'
    }
    foreach ($name in $render.services.Keys) {
        $service = $render.services[$name]
        Require ($expected.ContainsKey($name) -and $service.image -eq $pin -and $service.pull_policy -eq 'never' -and
            $service.network_mode -eq 'none' -and $service.read_only -and $service.cap_drop.Count -eq 1 -and
            $service.cap_drop[0] -eq 'ALL' -and $service.security_opt -contains 'no-new-privileges:true' -and
            -not ($service.ports -or $service.secrets -or $service.cap_add -or $service.privileged -or
                $service.devices -or $service.pid -or $service.ipc -or $service.env_file -or $service.container_name) -and
            $service.environment.Count -eq 2 -and $service.environment.PYTHONPATH -eq '/fixture' -and
            $service.environment.PYTHONUNBUFFERED -eq '1') "Unexpected rendered sandbox settings in $name"
        $actual = @(foreach ($mount in $service.volumes) {
            if ($mount.type -eq 'volume') {
                Require ($targets[$mount.source] -eq $mount.target) "Wrong volume target in $name"
                $mode = if ($mount.read_only) { 'ro' } else { 'rw' }
                "$($mount.source):$mode"
            } elseif ($mount.target -eq $targets.ledger) {
                Require ($mount.type -eq 'bind' -and -not $mount.read_only -and
                    [IO.Path]::GetFullPath($mount.source) -eq $scratch -and
                    $mount.bind.propagation -eq 'rprivate' -and $mount.bind.create_host_path -eq $false) "Wrong fixture ledger bind in $name"
                'ledger:rw'
            } else {
                $leaf = [IO.Path]::GetFileNameWithoutExtension($mount.source)
                $source = Join-Path $PSScriptRoot "$leaf.py"
                $target = "/fixture/$leaf.py"
                if ($leaf -eq 'adapter' -and $name -in @('init', 'level2', 'acl-level2')) {
                    $source = Join-Path $PSScriptRoot '../p0-level2/adapter.py'
                    $target = '/level2/adapter.py'
                } else {
                    Require ($leaf -in $sourceFiles) "Unexpected bind source in $name"
                }
                Require ($mount.type -eq 'bind' -and $mount.read_only -and $mount.target -eq $target -and
                    [IO.Path]::GetFullPath($mount.source) -eq [IO.Path]::GetFullPath($source) -and
                    (Test-Path -LiteralPath $source -PathType Leaf)) "Wrong bind mount in $name"
            }
        })
        Require ((($actual | Sort-Object) -join ',') -ceq (($expected[$name] | Sort-Object) -join ',')) "Wrong mount set in $name"
    }
    Write-Output 'PASS rendered local fixture, allowlisted files and isolated volumes'
    $validated = $true

    Invoke-Fixture @('run', '--rm', '--no-deps', '-T', 'init')
    Invoke-Fixture @('up', '-d', '--wait', '--no-deps', 'writer')
    $writer = Invoke-Fixture @('ps', '-q', 'writer')
    $inspect = @(Invoke-Docker ($dockerArgs + @('inspect', $writer)) | Out-String | ConvertFrom-Json -AsHashtable)[0]
    Require ($inspect.Config.User -eq '0:0') "Unexpected writer user: $($inspect.Config.User)"
    Require ($inspect.HostConfig.NetworkMode -eq 'none') "Unexpected writer network: $($inspect.HostConfig.NetworkMode)"
    Require $inspect.HostConfig.ReadonlyRootfs 'Writer rootfs is writable'
    Require ($inspect.HostConfig.CapDrop -contains 'ALL') "Unexpected writer cap_drop: $($inspect.HostConfig.CapDrop)"
    Require ($inspect.HostConfig.SecurityOpt -contains 'no-new-privileges:true') "Unexpected writer security options: $($inspect.HostConfig.SecurityOpt)"
    Require ($inspect.HostConfig.PortBindings.Count -eq 0) 'Writer has port bindings'
    $writable = @($inspect.Mounts | Where-Object RW)
    $bound = @($writable | Where-Object { $_.Type -eq 'bind' -and $_.Destination -eq '/case/mock-ledger' -and
        $_.Propagation -eq 'rprivate' })
    Require ($writable.Count -eq 2 -and
        $bound.Count -eq 1 -and
        @($writable | Where-Object { $_.Type -eq 'volume' -and $_.Destination -eq '/case/ipc' }).Count -eq 1 -and
        @($inspect.Mounts | Where-Object { $_.Propagation -and $_.Propagation -ne 'rprivate' }).Count -eq 0) 'Unexpected writer mount'
    Write-Output 'PASS inspected writer isolation and private propagation'
    foreach ($role in @('guard', 'same-uid', 'wrong-gid', 'unmounted', 'acl-nonroot', 'acl-level2')) {
        Invoke-Fixture @('run', '--rm', '--no-deps', '-T', $role)
    }
    Invoke-Fixture @('run', '--rm', '--no-deps', '-T', 'acl-nonroot', 'acl-nonroot', 'after')
    Invoke-Fixture @('up', '-d', '--no-deps', 'level2')
    $level2 = Invoke-Fixture @('ps', '-aq', 'level2')
    $deadline = [DateTime]::UtcNow.AddSeconds(10)
    do {
        $ready = (Invoke-Docker ($dockerArgs + @('logs', $level2))) -contains 'LEVEL2_LOCK_HELD'
        if (-not $ready) { Start-Sleep -Milliseconds 100 }
    } until ($ready -or [DateTime]::UtcNow -ge $deadline)
    Require $ready 'Level 2 never acquired fixture lock'
    Invoke-Fixture @('run', '--rm', '--no-deps', '-T', 'guard', 'guard', 'race')
    Require ((Invoke-Docker ($dockerArgs + @('wait', $level2))) -eq '0') 'Level 2 fixture failed'
    Invoke-Docker ($dockerArgs + @('logs', $level2))
    Invoke-Fixture @('run', '--rm', '--no-deps', '-T', 'faults')
    Invoke-Fixture @('restart', 'writer')
    Invoke-Fixture @('up', '-d', '--wait', '--no-deps', 'writer')
    Invoke-Fixture @('run', '--rm', '--no-deps', '-T', 'guard', 'guard', 'restart')
    Invoke-Fixture @('stop', 'writer')
    Invoke-Fixture @('run', '--rm', '--no-deps', '-T', 'level2', 'level2', 'verify')
} finally {
    try {
        if ($validated) {
            Invoke-Fixture @('down', '--volumes', '--remove-orphans')
            Require (-not (Invoke-Docker ($dockerArgs + @('ps', '-aq', '--filter', "label=com.docker.compose.project=$project")))) 'Fixture containers remain'
            Require (-not (Invoke-Docker ($dockerArgs + @('volume', 'ls', '-q', '--filter', "label=com.docker.compose.project=$project")))) 'Fixture volumes remain'
            Require (-not (Invoke-Docker ($dockerArgs + @('network', 'ls', '-q', '--filter', "label=com.docker.compose.project=$project")))) 'Fixture networks remain'
        }
        $resolvedScratch = (Resolve-Path -LiteralPath $scratch).Path
        Require ($resolvedScratch -eq $scratch -and (Split-Path -Leaf $resolvedScratch) -eq $project -and
            (Split-Path -Parent $resolvedScratch) -eq [IO.Path]::TrimEndingDirectorySeparator(
                [IO.Path]::GetFullPath([IO.Path]::GetTempPath()))) 'Refusing to delete unexpected fixture path'
        Remove-Item -LiteralPath $resolvedScratch -Recurse -Force
        Require (-not (Test-Path -LiteralPath $resolvedScratch)) 'Fixture ledger directory remains'
        Write-Output 'PASS fixture resources removed'
    } finally {
        [Environment]::SetEnvironmentVariable('TTD_H6_B2_C_FAKE_LEDGER', $priorLedger, 'Process')
    }
}
