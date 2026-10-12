@echo off
setlocal
cd /d "%~dp0"

set "JMETER_CMD="
if defined JMETER_HOME if exist "%JMETER_HOME%\bin\jmeter.bat" set "JMETER_CMD=%JMETER_HOME%\bin\jmeter.bat"
if not defined JMETER_CMD where jmeter.bat >nul 2>nul && set "JMETER_CMD=jmeter.bat"

if not defined JMETER_CMD (
  echo [ERROR] JMeter was not found.
  echo Set JMETER_HOME or add jmeter.bat to PATH.
  exit /b 2
)

if not defined PERF_THREADS set "PERF_THREADS=5"
if not defined PERF_RAMP_SECONDS set "PERF_RAMP_SECONDS=5"
if not defined PERF_DURATION_SECONDS set "PERF_DURATION_SECONDS=30"
if not defined PERF_PACING_MS set "PERF_PACING_MS=1000"

if defined THINGSBOARD_TEST_PROJECT (
  set "PROJECT_ROOT=%THINGSBOARD_TEST_PROJECT%"
) else (
  set "PROJECT_ROOT=%~dp0.."
)

if not exist "%PROJECT_ROOT%\postman\ThingsBoard_Local.postman_environment.local.json" (
  echo [ERROR] The local Postman environment file was not found.
  echo [INFO] Project path: %PROJECT_ROOT%
  echo [INFO] Set THINGSBOARD_TEST_PROJECT if the project is stored elsewhere.
  exit /b 3
)

set "REPORT_ROOT=%~dp0reports"
set "JTL_FILE=%REPORT_ROOT%\results.jtl"
set "HTML_DIR=%REPORT_ROOT%\html"
set "LOG_FILE=%REPORT_ROOT%\jmeter.log"

if exist "%REPORT_ROOT%" rmdir /s /q "%REPORT_ROOT%"
mkdir "%REPORT_ROOT%"

echo [INFO] PERF-001 device detail read performance test
echo [INFO] threads=%PERF_THREADS%, ramp=%PERF_RAMP_SECONDS%s, duration=%PERF_DURATION_SECONDS%s, pacing=%PERF_PACING_MS%ms

call "%JMETER_CMD%" -n ^
  -t "%~dp0thingsboard-device-read.jmx" ^
  "-JprojectRoot=%PROJECT_ROOT%" ^
  "-Jthreads=%PERF_THREADS%" ^
  "-JrampSeconds=%PERF_RAMP_SECONDS%" ^
  "-JdurationSeconds=%PERF_DURATION_SECONDS%" ^
  "-JpacingMs=%PERF_PACING_MS%" ^
  -l "%JTL_FILE%" ^
  -j "%LOG_FILE%" ^
  -e -o "%HTML_DIR%"

set "RUN_EXIT=%ERRORLEVEL%"
if not "%RUN_EXIT%"=="0" (
  echo [ERROR] JMeter execution failed. Check "%LOG_FILE%".
  exit /b %RUN_EXIT%
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$target = @(Import-Csv -LiteralPath '%JTL_FILE%' | Where-Object { $_.label -eq 'PERF-001 GET /api/device/{deviceId}' });" ^
  "if ($target.Count -eq 0) { Write-Error 'No PERF-001 samples found'; exit 3 };" ^
  "$elapsed = @($target | ForEach-Object { [double]$_.elapsed } | Sort-Object);" ^
  "$failed = @($target | Where-Object { $_.success -ne 'true' }).Count;" ^
  "$average = ($elapsed | Measure-Object -Average).Average;" ^
  "$position = 0.95 * ($elapsed.Count + 1); $lower = [Math]::Floor($position); $fraction = $position - $lower;" ^
  "if ($lower -le 0) { $p95 = $elapsed[0] } elseif ($lower -ge $elapsed.Count) { $p95 = $elapsed[-1] } else { $p95 = $elapsed[$lower - 1] + $fraction * ($elapsed[$lower] - $elapsed[$lower - 1]) };" ^
  "$start = ($target | ForEach-Object { [double]$_.timeStamp } | Measure-Object -Minimum).Minimum;" ^
  "$end = ($target | ForEach-Object { [double]$_.timeStamp + [double]$_.elapsed } | Measure-Object -Maximum).Maximum;" ^
  "$throughput = if ($end -gt $start) { $target.Count * 1000.0 / ($end - $start) } else { 0 };" ^
  "$summary = 'samples={0}; failed={1}; avg_ms={2:N2}; p95_ms={3:N2}; min_ms={4}; max_ms={5}; throughput_rps={6:N2}' -f $target.Count, $failed, $average, $p95, $elapsed[0], $elapsed[-1], $throughput;" ^
  "$summary | Tee-Object -FilePath '%REPORT_ROOT%\summary.txt';" ^
  "if ($failed -gt 0) { exit 4 }"

set "CHECK_EXIT=%ERRORLEVEL%"
if not "%CHECK_EXIT%"=="0" (
  echo [ERROR] Functional assertions failed. Check the HTML report.
  exit /b %CHECK_EXIT%
)

echo [PASS] Performance test completed.
echo [INFO] HTML report: %HTML_DIR%\index.html
echo [INFO] Summary: %REPORT_ROOT%\summary.txt
exit /b 0
