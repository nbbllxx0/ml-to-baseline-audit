# Start the P00647 L2 runs once the L1 runs have finished (all three rows written and no MATLAB session left),
# and raise the MATLAB worker to high priority as tools/pin.py does for Python runs. Runs detached.
$dir = "E:\AI\ml-to-baseline-audit\v3\runs\P00647"
while ($true) {
    $done = (Test-Path "$dir\results_L1.txt") -and ((Get-Content "$dir\results_L1.txt" | Select-String "^row").Count -ge 3)
    $busy = @(Get-Process -Name MATLAB -ErrorAction SilentlyContinue).Count -gt 0
    if ($done -and -not $busy) { break }
    Start-Sleep -Seconds 60
}
Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$dir\launch.bat`" 0 L2" -WindowStyle Hidden
Start-Sleep -Seconds 60
Get-Process -Name MATLAB -ErrorAction SilentlyContinue | ForEach-Object { $_.PriorityClass = 'High' }
