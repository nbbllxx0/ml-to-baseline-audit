<#
Blind cross-provider coding with the Codex CLI: set up the sessions, log in, check the tools, run, and report status.

    powershell -ExecutionPolicy Bypass -File run_codex.ps1 -Action Setup
    powershell -ExecutionPolicy Bypass -File run_codex.ps1 -Action Login
    powershell -ExecutionPolicy Bypass -File run_codex.ps1 -Action Smoke
    powershell -ExecutionPolicy Bypass -File run_codex.ps1 -Action Run -Parallel 4
    powershell -ExecutionPolicy Bypass -File run_codex.ps1 -Action Status

Setup copies the session folders and the Codex settings to -RunRoot, which must lie outside the project folder. Every
Codex process runs with CODEX_HOME = <RunRoot>\codex_home, a separate Codex home with no memories, history, global
AGENTS.md, plugins or skills. Event logs go to <RunRoot>\logs, outside the agents' working folders. Run skips finished
sessions, so repeating the command resumes an interrupted run.
#>
param(
    [ValidateSet('Setup', 'Login', 'Status', 'Smoke', 'Run', 'Repair', 'DryRun')]
    [string]$Action = 'Status',
    [string]$RunRoot = 'C:\xprov_runs',
    [string[]]$Models = @('gpt-6-sol', 'gpt-6-luna'),
    [string[]]$Sessions = @(),
    [int]$Parallel = 4,
    [int]$TimeoutMinutes = 180,
    [switch]$Force,
    # Use your usual Codex login instead of the separate home: the user config is ignored, every setting of
    # codex_home\config.toml is passed on the command line, and no session files are written (--ephemeral).
    [switch]$DefaultHome,
    # Codex CLI to run. Default: the newest codex.exe bundled with the Codex desktop app, else codex.cmd from npm.
    # The npm CLI 0.147.0 cannot run gpt-6-sol with a ChatGPT login; the app's 0.158 CLI can.
    [string]$CodexExe = ''
)
$Overrides = @('-c', 'model_reasoning_effort=high', '-c', 'approval_policy=never', '-c', 'sandbox_mode=workspace-write',
    '-c', 'web_search=live', '-c', 'sandbox_workspace_write.network_access=true', '-c', 'windows.sandbox=unelevated',
    '-c', 'shell_environment_policy.inherit=all', '-c', 'shell_environment_policy.ignore_default_excludes=false')
foreach ($feat in 'memories', 'apps', 'plugins', 'remote_plugin', 'browser_use', 'browser_use_external',
    'browser_use_full_cdp_access', 'computer_use', 'in_app_browser', 'multi_agent', 'hooks', 'skill_search',
    'image_generation', 'goals', 'tool_suggest', 'chronicle') { $Overrides += @('--disable', $feat) }
$ErrorActionPreference = 'Stop'
$Package = $PSScriptRoot
$ProjectRoot = (Resolve-Path (Join-Path $Package '..\..\..')).Path.TrimEnd('\')
$RunRoot = [IO.Path]::GetFullPath($RunRoot).TrimEnd('\')
$CodexHome = Join-Path $RunRoot 'codex_home'
$SessRoot = Join-Path $RunRoot 'sessions'
$LogRoot = Join-Path $RunRoot 'logs'
$Prompt = 'Read AGENTS.md in this folder and complete the task it describes.'

foreach ($bad in @($ProjectRoot, (Join-Path $env:USERPROFILE '.codex'), (Join-Path $env:USERPROFILE '.claude'))) {
    if ($RunRoot.StartsWith($bad, [StringComparison]::OrdinalIgnoreCase) -or $bad.StartsWith($RunRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "RunRoot $RunRoot overlaps $bad. Choose a folder outside the project and outside your Codex and Claude homes."
    }
}
if ($CodexExe) { $Codex = $CodexExe } else {
    $app = Get-ChildItem (Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin') -Recurse -Filter codex.exe -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $Codex = if ($app) { $app.FullName } else { (Get-Command codex.cmd -ErrorAction Stop).Source }
}
Write-Host "Codex CLI: $Codex ($(& $Codex --version 2>$null))"

function Get-SessionNames([string]$model) {
    $dir = Join-Path $SessRoot $model
    if (-not (Test-Path $dir)) { throw "No sessions for $model under $SessRoot. Run -Action Setup first." }
    $all = Get-ChildItem $dir -Directory | ForEach-Object { $_.Name } | Where-Object { $_ -ne 'smoke' }
    if ($Sessions.Count -gt 0) { return @($all | Where-Object { $Sessions -contains $_ }) }
    return @($all)
}

function Get-Progress([string]$model, [string]$name) {
    # returns @(done, expected)
    $dir = Join-Path $SessRoot "$model\$name"
    $out = Join-Path $dir 'out'
    if ($name -eq 'smoke') { return @([int](Test-Path (Join-Path $out 'smoke.json')), 1) }
    if ($name -eq 'referrals') {
        $f = Join-Path $out 'referrals.json'
        $n = 0
        if (Test-Path $f) {
            # assign first: in Windows PowerShell 5.1, @(... | ConvertFrom-Json) wraps a JSON array into one element
            try { $data = Get-Content $f -Raw -Encoding UTF8 | ConvertFrom-Json; $n = @($data).Count } catch { $n = 0 }
        }
        return @($n, 17)
    }
    $pids = @(Get-Content (Join-Path $dir 'queue.txt') -Encoding UTF8 | ForEach-Object { if ($_ -match '^- (P\d{5}) ') { $Matches[1] } })
    $done = @($pids | Where-Object { Test-Path (Join-Path $out "$_.json") }).Count
    return @($done, $pids.Count)
}

function Start-Session([string]$model, [string]$name, [string]$task = $Prompt) {
    $dir = Join-Path $SessRoot "$model\$name"
    $log = Join-Path $LogRoot "$model\$name"
    New-Item -ItemType Directory -Force -Path $log, (Join-Path $dir 'out'), (Join-Path $dir 'tmp') | Out-Null
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $events = Join-Path $log "events-$stamp.jsonl"
    $stderr = Join-Path $log "stderr-$stamp.txt"
    $last = Join-Path $log "last-$stamp.md"
    $argLine = "exec --cd `"$dir`" --skip-git-repo-check -m $model --json -o `"$last`""
    if ($DefaultHome) {
        $argLine += ' --ignore-user-config --ephemeral ' + ($Overrides -join ' ')
        Remove-Item Env:\CODEX_HOME -ErrorAction SilentlyContinue
    } else { $env:CODEX_HOME = $CodexHome }
    $argLine += " `"$task`""
    $p = Start-Process -FilePath $Codex -ArgumentList $argLine -WorkingDirectory $dir -WindowStyle Hidden `
        -RedirectStandardOutput $events -RedirectStandardError $stderr -PassThru
    $null = $p.Handle   # keeps the exit code readable after the process ends
    return [pscustomobject]@{ Model = $model; Name = $name; Proc = $p; Start = Get-Date; Log = $log; Stamp = $stamp }
}

function Invoke-Sessions($jobs, [int]$limit, [int]$timeout) {
    $queue = New-Object System.Collections.Queue
    foreach ($j in $jobs) { $queue.Enqueue($j) }
    $running = New-Object System.Collections.ArrayList
    while ($queue.Count -gt 0 -or $running.Count -gt 0) {
        while ($running.Count -lt $limit -and $queue.Count -gt 0) {
            $j = $queue.Dequeue()
            $r = if ($j.PSObject.Properties['Task']) { Start-Session $j.Model $j.Name $j.Task } else { Start-Session $j.Model $j.Name }
            [void]$running.Add($r)
            Write-Host ("{0:HH:mm:ss} started  {1}/{2}" -f (Get-Date), $j.Model, $j.Name)
        }
        Start-Sleep -Seconds 20
        foreach ($r in @($running)) {
            $state = $null
            if ($r.Proc.HasExited) { $state = "exit $($r.Proc.ExitCode)" }
            elseif (((Get-Date) - $r.Start).TotalMinutes -gt $timeout) {
                & taskkill.exe /PID $r.Proc.Id /T /F | Out-Null
                $state = "stopped after $timeout min"
            }
            if ($state) {
                $prog = Get-Progress $r.Model $r.Name
                Set-Content -Path (Join-Path $r.Log "result-$($r.Stamp).txt") -Value "$state; $($prog[0]) of $($prog[1]) done" -Encoding UTF8
                Write-Host ("{0:HH:mm:ss} finished {1}/{2}: {3}; {4} of {5} done" -f (Get-Date), $r.Model, $r.Name, $state, $prog[0], $prog[1])
                $running.Remove($r)
            }
        }
    }
}

switch ($Action) {
    'Setup' {
        New-Item -ItemType Directory -Force -Path $CodexHome, $SessRoot, $LogRoot | Out-Null
        Copy-Item (Join-Path $Package 'codex_home\config.toml') (Join-Path $CodexHome 'config.toml') -Force
        foreach ($model in $Models) {
            $src = Join-Path $Package "sessions\$model"
            if (-not (Test-Path $src)) { throw "The package has no sessions for $model." }
            foreach ($s in Get-ChildItem $src -Directory) {
                $dest = Join-Path $SessRoot "$model\$($s.Name)"
                $hasOutput = (Test-Path (Join-Path $dest 'out')) -and @(Get-ChildItem (Join-Path $dest 'out') -File -ErrorAction SilentlyContinue).Count -gt 0
                if ($hasOutput -and -not $Force) { Write-Host "kept (has output): $model/$($s.Name)"; continue }
                New-Item -ItemType Directory -Force -Path $dest | Out-Null
                Copy-Item (Join-Path $s.FullName '*') $dest -Recurse -Force
                New-Item -ItemType Directory -Force -Path (Join-Path $dest 'out'), (Join-Path $dest 'tmp') | Out-Null
            }
            Write-Host "set up: $model ($(@(Get-ChildItem (Join-Path $SessRoot $model) -Directory).Count) sessions)"
        }
        Write-Host "Next: -Action Login (once), then -Action Smoke."
    }
    'Login' {
        $env:CODEX_HOME = $CodexHome
        & $Codex login
        & $Codex login status
    }
    'Status' {
        if (-not $DefaultHome) { $env:CODEX_HOME = $CodexHome }
        & $Codex login status
        foreach ($model in $Models) {
            $names = @(Get-SessionNames $model) + @('smoke')
            $done = 0; $exp = 0; $open = @()
            foreach ($n in $names) {
                $p = Get-Progress $model $n
                if ($n -ne 'smoke') { $done += $p[0]; $exp += $p[1] }
                if ($p[0] -lt $p[1]) { $open += "$n ($($p[0])/$($p[1]))" }
            }
            Write-Host "$model : $done of $exp records; incomplete: $(if ($open.Count) { $open -join ', ' } else { 'none' })"
        }
    }
    'DryRun' {
        foreach ($model in $Models) {
            $name = @(Get-SessionNames $model)[0]
            $dir = Join-Path $SessRoot "$model\$name"
            Write-Host "CODEX_HOME=$CodexHome"
            Write-Host "$Codex exec --cd `"$dir`" --skip-git-repo-check -m $model --json -o `"<log>\last-<stamp>.md`" `"$Prompt`""
        }
    }
    'Smoke' {
        $jobs = foreach ($model in $Models) { [pscustomobject]@{ Model = $model; Name = 'smoke' } }
        Invoke-Sessions $jobs $Models.Count 20
        foreach ($model in $Models) {
            $f = Join-Path $SessRoot "$model\smoke\out\smoke.json"
            if (-not (Test-Path $f)) { Write-Host "SMOKE FAILED ($model): no out\smoke.json; see $LogRoot\$model\smoke"; continue }
            $s = Get-Content $f -Raw -Encoding UTF8 | ConvertFrom-Json
            $ok = ($s.abs_status -eq 200) -and ($s.title -match 'Attention Is All You Need') -and ($s.pdf_line -match 'Attention')
            Write-Host ("SMOKE {0} ({1}): status {2}; title '{3}'; pdf line '{4}'; web search {5}; arXiv id '{6}'" -f `
                $(if ($ok) { 'OK' } else { 'FAILED' }), $model, $s.abs_status, $s.title, $s.pdf_line, $s.web_search_ok, $s.arxiv_id_found)
        }
    }
    'Repair' {
        # format-only repair: sessions holding a REPAIR.md written by repair_codex.py prepare
        $jobs = New-Object System.Collections.ArrayList
        foreach ($model in $Models) {
            foreach ($n in Get-SessionNames $model) {
                if (Test-Path (Join-Path $SessRoot "$model\$n\REPAIR.md")) {
                    [void]$jobs.Add([pscustomobject]@{ Model = $model; Name = $n; Task = 'Read REPAIR.md in this folder and do exactly what it says.' })
                }
            }
        }
        Write-Host "$($jobs.Count) repair sessions, $Parallel at a time"
        Invoke-Sessions $jobs $Parallel 30
        Write-Host "Next: python guide_manuscript/cross_provider_coding/repair_codex.py verify $RunRoot <model>"
    }
    'Run' {
        $jobs = New-Object System.Collections.ArrayList
        foreach ($model in $Models) {
            foreach ($n in Get-SessionNames $model) {
                $p = Get-Progress $model $n
                if ($p[0] -ge $p[1]) { Write-Host "done already: $model/$n"; continue }
                [void]$jobs.Add([pscustomobject]@{ Model = $model; Name = $n })
            }
        }
        Write-Host "$($jobs.Count) sessions to run, $Parallel at a time, timeout $TimeoutMinutes min"
        Invoke-Sessions $jobs $Parallel $TimeoutMinutes
        Write-Host "Next: python guide_manuscript/cross_provider_coding/collect_codex.py $RunRoot"
    }
}
