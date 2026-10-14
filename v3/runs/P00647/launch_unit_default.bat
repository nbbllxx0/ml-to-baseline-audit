@echo off
rem P00647 unit-cost run with MATLAB default threading (the second run of launch_unit.bat did not start; relaunched alone).
cd /d E:\AI\ml-to-baseline-audit\v3\runs\P00647
start "" /wait /affinity FFF /high "C:\Program Files\MATLAB\R2023b\bin\matlab.exe" -batch "unit_rows(0, 'unit_default')" -logfile "E:\AI\ml-to-baseline-audit\v3\runs\P00647\unit_default.log"
