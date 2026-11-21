[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$errors = [System.Collections.Generic.List[string]]::new()

Push-Location $repoRoot
try {
    $requiredFiles = @(
        'README.md',
        'AGENTS.md',
        'STATE.md',
        'CATALOG.yaml',
        'CONTRIBUTING.md',
        'CHANGELOG.md',
        'rules/REPOSITORY_SECURITY.md'
    )

    foreach ($path in $requiredFiles) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            $errors.Add("Missing required file: $path")
        }
    }

    $trackedFiles = @(git ls-files)
    foreach ($path in $trackedFiles) {
        $name = Split-Path -Leaf $path
        if ($name -match '^\.env($|\.)' -or $path -match '\.(pem|key|p12|pfx|sql|dump|backup)$') {
            $errors.Add("Forbidden tracked file: $path")
        }
    }

    $secretPatterns = @(
        'BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY',
        'session_id=[A-Za-z0-9_-]+',
        '(?i)(password|token|api[_-]?key|secret)\s*[=:]\s*[^\s\[<][^\s]*'
    )

    $contentFiles = Get-ChildItem -Recurse -File |
        Where-Object { $_.FullName -notmatch '[\\/]\.git[\\/]' -and $_.Extension -in '.md', '.yaml', '.yml', '.sh', '.ps1' }

    foreach ($file in $contentFiles) {
        $text = Get-Content -LiteralPath $file.FullName -Raw
        foreach ($pattern in $secretPatterns) {
            if ($text -match $pattern) {
                $relative = [System.IO.Path]::GetRelativePath($repoRoot, $file.FullName)
                $errors.Add("Possible secret pattern in: $relative")
                break
            }
        }
    }

    $metadataFolders = @('inventory', 'reports', 'knowledge', 'runbooks', 'decisions', 'references', 'rules')
    foreach ($folder in $metadataFolders) {
        if (-not (Test-Path -LiteralPath $folder)) { continue }
        Get-ChildItem -LiteralPath $folder -Recurse -File -Filter '*.md' |
            Where-Object { $_.Name -ne 'README.md' } |
            ForEach-Object {
                $firstLine = Get-Content -LiteralPath $_.FullName -TotalCount 1
                if ($firstLine -ne '---') {
                    $relative = [System.IO.Path]::GetRelativePath($repoRoot, $_.FullName)
                    $errors.Add("Missing YAML front matter: $relative")
                }
            }
    }

    Get-ChildItem -Recurse -File -Filter '*.md' | ForEach-Object {
        $file = $_
        $text = Get-Content -LiteralPath $file.FullName -Raw
        foreach ($match in [regex]::Matches($text, '\]\(([^)]+)\)')) {
            $target = $match.Groups[1].Value.Trim('<', '>')
            if ($target -match '^(https?://|mailto:|#)' -or $target -eq '') { continue }
            $pathPart = ($target -split '#')[0]
            $resolved = Join-Path $file.DirectoryName $pathPart
            if (-not (Test-Path -LiteralPath $resolved)) {
                $relative = [System.IO.Path]::GetRelativePath($repoRoot, $file.FullName)
                $errors.Add("Broken local link in $relative -> $target")
            }
        }
    }

    if (Test-Path -LiteralPath 'CATALOG.yaml') {
        $catalog = Get-Content -LiteralPath 'CATALOG.yaml' -Raw
        foreach ($match in [regex]::Matches($catalog, '(?m)^\s+path:\s+(.+)$')) {
            $path = $match.Groups[1].Value.Trim()
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
                $errors.Add("Catalog path does not exist: $path")
            }
        }
    }

    if ($errors.Count -gt 0) {
        $errors | ForEach-Object { Write-Error $_ }
        exit 1
    }

    Write-Output "Repository validation passed ($($trackedFiles.Count) tracked files)."
}
finally {
    Pop-Location
}
