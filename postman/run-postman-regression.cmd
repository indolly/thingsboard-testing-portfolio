@echo off
setlocal

rem 运行本地 Postman 接口回归，并生成不带日期的本地报告。
rem 可以在执行前设置 POSTMAN_CLI，覆盖下面的默认安装位置。

if not defined POSTMAN_CLI set "POSTMAN_CLI=D:\toolsoft\nodejs\node_global\postman.cmd"

set "SCRIPT_DIR=%~dp0"
set "COLLECTION=%SCRIPT_DIR%ThingsBoard_REST_API_Tests.postman_collection.json"
set "ENVIRONMENT=%SCRIPT_DIR%ThingsBoard_Local.postman_environment.local.json"
set "REPORT_DIR=%SCRIPT_DIR%reports"

if not exist "%POSTMAN_CLI%" (
    echo [ERROR] Postman CLI not found: %POSTMAN_CLI%
    echo Set POSTMAN_CLI to the full path of postman.cmd and try again.
    exit /b 2
)

if not exist "%COLLECTION%" (
    echo [ERROR] Collection file not found: %COLLECTION%
    exit /b 3
)

if not exist "%ENVIRONMENT%" (
    echo [ERROR] Local environment file not found: %ENVIRONMENT%
    echo Create it from the sanitized example and fill only local required values.
    exit /b 4
)

if not exist "%REPORT_DIR%" mkdir "%REPORT_DIR%"

call "%POSTMAN_CLI%" collection run "%COLLECTION%" ^
  -e "%ENVIRONMENT%" ^
  --report-events=false ^
  -r cli,junit,html ^
  --reporter-junit-export "%REPORT_DIR%\postman-results.xml" ^
  --reporter-html-export "%REPORT_DIR%\postman-report.html"

set "RUN_EXIT_CODE=%ERRORLEVEL%"

if not "%RUN_EXIT_CODE%"=="0" (
    echo [FAILED] Postman regression failed with exit code %RUN_EXIT_CODE%.
    exit /b %RUN_EXIT_CODE%
)

echo [PASSED] Postman regression completed successfully.
echo HTML report: %REPORT_DIR%\postman-report.html
echo JUnit report: %REPORT_DIR%\postman-results.xml
exit /b 0

