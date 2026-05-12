#!/usr/bin/env pwsh
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Command,

    [string]$Workspace,
    [string]$Cwd = (Get-Location).Path,
    [string]$TargetPath
)

$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot 'common.ps1')

function Resolve-NormalizedPath {
    param([Parameter(Mandatory = $true)][string]$PathValue)

    $resolved = Resolve-Path -LiteralPath $PathValue -ErrorAction SilentlyContinue
    if ($resolved) {
        return $resolved.Path
    }

    $parent = Split-Path -Path $PathValue -Parent
    if ([string]::IsNullOrWhiteSpace($parent)) {
        $parent = '.'
    }
    $base = Split-Path -Path $PathValue -Leaf
    $resolvedParent = Resolve-Path -LiteralPath $parent -ErrorAction Stop
    return [System.IO.Path]::GetFullPath((Join-Path $resolvedParent.Path $base))
}

function Test-ApprovedDevEnvironment {
    return $env:KITE_DEV_ENV -eq '1'
}

function Test-ContainerEvidence {
    return (Test-Path -LiteralPath '/.dockerenv') -or (Test-Path -LiteralPath '/run/.containerenv')
}

function Test-DangerousCommand {
    param([Parameter(Mandatory = $true)][string]$Text)

    $value = $Text.ToLowerInvariant()
    $patterns = @(
        'npm install -g',
        'npm i -g',
        'pnpm add -g',
        'yarn global add',
        'bun add -g',
        'pip install ',
        'pip3 install ',
        'uv tool install ',
        'cargo install ',
        'apt install ',
        'apt-get install ',
        'yum install ',
        'dnf install ',
        'brew install ',
        'docker build',
        'docker run',
        'docker pull',
        'systemctl ',
        'service '
    )

    foreach ($pattern in $patterns) {
        if ($value.Contains($pattern)) {
            return $true
        }
    }

    return $false
}

function Test-PathOutsideWorkspace {
    param(
        [Parameter(Mandatory = $true)][string]$Target,
        [Parameter(Mandatory = $true)][string]$Workspace
    )

    $separators = [char[]]@(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $workspaceRoot = $Workspace.TrimEnd($separators)
    $targetRoot = $Target.TrimEnd($separators)

    $comparison = [System.StringComparison]::Ordinal
    if ([System.IO.Path]::DirectorySeparatorChar -eq '\') {
        $comparison = [System.StringComparison]::OrdinalIgnoreCase
    }

    if ([string]::Equals($targetRoot, $workspaceRoot, $comparison)) {
        return $false
    }

    $primaryPrefix = $workspaceRoot + [System.IO.Path]::DirectorySeparatorChar
    $alternatePrefix = $workspaceRoot + [System.IO.Path]::AltDirectorySeparatorChar
    if ($targetRoot.StartsWith($primaryPrefix, $comparison)) {
        return $false
    }
    if ($alternatePrefix -ne $primaryPrefix -and $targetRoot.StartsWith($alternatePrefix, $comparison)) {
        return $false
    }

    return $true
}

if (-not $Workspace) {
    try {
        $Workspace = Get-RepoRoot
    } catch {
        $Workspace = (Get-Location).Path
    }
}

$workspacePath = Resolve-NormalizedPath -PathValue $Workspace
$cwdPath = Resolve-NormalizedPath -PathValue $Cwd
$normalizedTarget = $null
if ($TargetPath) {
    $normalizedTarget = Resolve-NormalizedPath -PathValue $TargetPath
}

$dangerousReason = $null
if (Test-DangerousCommand -Text $Command) {
    $dangerousReason = 'host-affecting command pattern detected'
} elseif ($normalizedTarget -and (Test-PathOutsideWorkspace -Target $normalizedTarget -Workspace $workspacePath)) {
    $dangerousReason = 'target path is outside the approved workspace'
}

if (-not $dangerousReason) {
    Write-Output 'ALLOW: command is read-only or workspace-safe.'
    exit 0
}

if (Test-ApprovedDevEnvironment) {
    $container = if (Test-ContainerEvidence) { 'yes' } else { 'no' }
    Write-Output "ALLOW: approved dev environment detected (KITE_DEV_ENV=1, container=$container)."
    exit 0
}

[Console]::Error.Write("`a")
[Console]::Error.WriteLine("BLOCK: $dangerousReason.")
[Console]::Error.WriteLine("Command: $Command")
[Console]::Error.WriteLine("Workspace: $workspacePath")
[Console]::Error.WriteLine("Current directory: $cwdPath")
[Console]::Error.WriteLine("KITE_DEV_ENV=$($env:KITE_DEV_ENV)")
[Console]::Error.WriteLine('Next step: run inside an approved dev environment or export KITE_DEV_ENV=1 in an approved sandbox before retrying.')
exit 1