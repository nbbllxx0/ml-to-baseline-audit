@echo off
rem Launch run_rows(threads, tag) in MATLAB, pinned to the performance cores (mask FFF) at high priority.
rem   launch.bat 1 L1     or     launch.bat 0 L2
rem A lock folder makes each tag run at most once, even if two launchers race.
cd /d E:\AI\ml-to-baseline-audit\v3\runs\P00647
mkdir "lock_%2" 2>nul || exit /b 0
start "" /wait /affinity FFF /high "C:\Program Files\MATLAB\R2023b\bin\matlab.exe" -batch "run_rows(%1, '%2')" -logfile "E:\AI\ml-to-baseline-audit\v3\runs\P00647\run_%2.log"
