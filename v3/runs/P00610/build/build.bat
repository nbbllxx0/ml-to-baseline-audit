@echo off
rem Builds the article-era Keff-CFD 2D solver (commit 720be71) from the patched copy in src\ (see REPAIRS.md).
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
set SRC=E:\AI\ml-to-baseline-audit\v3\runs\P00610\build\src
cd /d E:\AI\ml-to-baseline-audit\v3\runs\P00610\build
cl /nologo /O2 /openmp:llvm /EHsc /FIstring /FIiostream /I"%SRC%" "%SRC%\keff2D.cpp" /Fe:keff2D_gs.exe
cl /nologo /O2 /openmp:llvm /EHsc /FIstring /FIiostream /I"%SRC%_tdma" "%SRC%_tdma\keff2D.cpp" /Fe:keff2D_tdma.exe
