@echo off
rem P00647 unit-cost runs, sequential, pinned to the performance cores (mask FFF) at high priority.
cd /d E:\AI\ml-to-baseline-audit\v3\runs\P00647
start "" /wait /affinity FFF /high "C:\Program Files\MATLAB\R2023b\bin\matlab.exe" -batch "unit_rows(1, 'unit_1thread')" -logfile "E:\AI\ml-to-baseline-audit\v3\runs\P00647\unit_1thread.log"
start "" /wait /affinity FFF /high "C:\Program Files\MATLAB\R2023b\bin\matlab.exe" -batch "unit_rows(0, 'unit_default')" -logfile "E:\AI\ml-to-baseline-audit\v3\runs\P00647\unit_default.log"
