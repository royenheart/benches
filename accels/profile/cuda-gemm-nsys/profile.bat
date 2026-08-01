@echo off
setlocal
REM Profile with Nsight Systems. Requires nsys on PATH.
if not exist gemm.exe (
  echo gemm.exe not found. Run build.bat first.
  exit /b 1
)

set N=%1
set ITERS=%2
if "%N%"=="" set N=1024
if "%ITERS%"=="" set ITERS=10

nsys profile -o gemm_report -f true --stats=true ^
  --trace=cuda,nvtx,osrt ^
  gemm.exe %N% %ITERS%

echo.
echo Report: gemm_report.nsys-rep
echo Open with: nsys-ui gemm_report.nsys-rep
endlocal
