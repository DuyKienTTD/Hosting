#Requires -Version 5.1
[CmdletBinding(DefaultParameterSetName='Install')]
param(
    [Parameter(Mandatory, ParameterSetName='Install')][string]$SelectorFile,
    [Parameter(ParameterSetName='Install')][string[]]$SmokePeer = @(),
    [Parameter(Mandatory, ParameterSetName='Uninstall')][switch]$Uninstall
)

$ErrorActionPreference = 'Stop'
$root = Join-Path $env:LOCALAPPDATA 'TTD-Zalo-Nick'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$task = 'TTD-Zalo-Nick-' + $identity.User.Value
if ($Uninstall) {
    if (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue) {
        Stop-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $task -Confirm:$false
    }
    Remove-Item -LiteralPath (Join-Path $root 'credential.dpapi') -Force -ErrorAction SilentlyContinue
    Write-Host 'Da go lich chay va credential cuc bo. Da giu profile Chrome va nhat ky gui.'
    return
}
if (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue) {
    throw 'Hay thu hoi tren UI va chay -Uninstall truoc khi ghep cap lai.'
}

$selectorPath = (Resolve-Path -LiteralPath $SelectorFile).Path
$selector = Get-Content -LiteralPath $selectorPath -Raw | ConvertFrom-Json
if (-not $selector.version -or $selector.version.StartsWith('fixture-')) {
    throw 'Can bo selector Zalo Web da duoc duyet, co phien ban.'
}
foreach ($peer in $SmokePeer) {
    if ($peer -notmatch '^[A-Za-z0-9_-]{1,100}$') { throw 'ID test khong hop le.' }
}

function Install-Prerequisite([string]$Package) {
    if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) {
        throw 'Can App Installer (winget) hoac cai Node.js LTS va Chrome truoc.'
    }
    & winget.exe install --id $Package --exact --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw "Cai dat $Package that bai." }
    $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' +
        [Environment]::GetEnvironmentVariable('Path','User')
}
function Find-Chrome {
    foreach ($folder in @($env:ProgramFiles, ${env:ProgramFiles(x86)}, $env:LOCALAPPDATA)) {
        if ($folder -and (Test-Path (Join-Path $folder 'Google\Chrome\Application\chrome.exe'))) { return $true }
    }
    return $false
}
$node = Get-Command node.exe -ErrorAction SilentlyContinue
if (-not $node -or (& $node.Source -p 'Number(process.versions.node.split(".")[0])') -lt 22) {
    Install-Prerequisite 'OpenJS.NodeJS.LTS'
    $node = Get-Command node.exe
}
if ((& $node.Source -p 'Number(process.versions.node.split(".")[0])') -lt 22) { throw 'Can Node.js 22 LTS hoac moi hon.' }
if (-not (Find-Chrome)) { Install-Prerequisite 'Google.Chrome' }
if (-not (Find-Chrome)) { throw 'Khong tim thay Google Chrome.' }

New-Item -ItemType Directory -Force -Path $root | Out-Null
$acl = Get-Acl -LiteralPath $root
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object Security.AccessControl.FileSystemAccessRule($identity.User, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow')
$acl.SetAccessRule($rule)
Set-Acl -LiteralPath $root -AclObject $acl
$app = Join-Path $root 'app'
New-Item -ItemType Directory -Force -Path $app | Out-Null
foreach ($entry in @('package.json','package-lock.json','src','start-nick-worker.ps1')) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot $entry) -Destination $app -Recurse -Force
}
Copy-Item -LiteralPath $selectorPath -Destination (Join-Path $root 'selectors.json') -Force
New-Item -ItemType Directory -Force -Path (Join-Path $root 'profile') | Out-Null
Push-Location $app
try {
    & (Join-Path (Split-Path $node.Source) 'npm.cmd') ci --omit=dev
    if ($LASTEXITCODE -ne 0) { throw 'npm ci that bai.' }
} finally { Pop-Location }

$code = Read-Host 'Nhap ma ghep cap mot lan tu Kenh Zalo > Nick phu' -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($code)
try {
    $body = @{ code = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) } | ConvertTo-Json -Compress
    $reply = Invoke-RestMethod -Method Post -Uri 'https://cskh.thuanthanhdat.com.vn/nick-worker/pair' `
        -ContentType 'application/json' -Body $body -MaximumRedirection 0 -TimeoutSec 20
    if ($reply.credential -notmatch '^[a-f0-9]{64}$') { throw 'Phan hoi ghep cap khong hop le.' }
    ConvertTo-SecureString $reply.credential -AsPlainText -Force | ConvertFrom-SecureString |
        Set-Content -LiteralPath (Join-Path $root 'credential.dpapi')
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    Remove-Variable body,reply -ErrorAction SilentlyContinue
}
@{ node = $node.Source; smokePeers = $SmokePeer } | ConvertTo-Json |
    Set-Content -LiteralPath (Join-Path $root 'config.json') -Encoding UTF8

$runner = Join-Path $app 'start-nick-worker.ps1'
$action = New-ScheduledTaskAction -Execute (Join-Path $PSHOME 'powershell.exe') `
    -Argument ('-NoProfile -ExecutionPolicy RemoteSigned -File "' + $runner + '"') -WorkingDirectory $app
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $identity.Name
$principal = New-ScheduledTaskPrincipal -UserId $identity.Name -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $task -Action $action -Trigger $trigger -Principal $principal -Settings $settings | Out-Null
Start-ScheduledTask -TaskName $task
Write-Host 'Da ghep cap va tao lich chay. Kenh dang STOP.'
