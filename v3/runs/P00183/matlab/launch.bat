@echo off
rem Launch run_classical(threads, tag) in MATLAB, pinned to the performance cores (mask FFF) at high priority.
rem   launch.bat 1 L1     or     launch.bat 0 L2
cd /d E:\AI\ml-to-baseline-audit\v3\runs\P00183\matlab
start "" /wait /affinity FFF /high "C:\Program Files\MATLAB\R2023b\bin\matlab.exe" -batch "run_classical(%1, '%2')" -logfile "E:\AI\ml-to-baseline-audit\v3\runs\P00183\matlab\run_%2.log"
