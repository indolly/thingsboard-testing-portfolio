pipeline {
    agent { label 'built-in' }

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '10'))
    }

    triggers {
        cron('H 9 * * 1-5')
    }

    environment {
        TB_BASE_URL = 'http://127.0.0.1:9091'
        TB_ALARM_TRIGGER_TEMPERATURE = '80'
        TB_ALARM_RECOVERY_TEMPERATURE = '0'
        TB_ALARM_WAIT_SECONDS = '30'
        PYTHONUTF8 = '1'
        PYTHON_BOOTSTRAP = 'C:\\Users\\dolphin\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'
        PIP_CACHE_DIR = 'D:\\toolsoft\\python-cache'
        PATH = "D:\\toolsoft\\nodejs\\node_global;D:\\toolsoft\\nodejs;${env.PATH}"
    }

    stages {
        stage('准备 Python 环境') {
            steps {
                dir('api-automation-python') {
                    bat '''
@echo off
if not exist "%PYTHON_BOOTSTRAP%" (
  echo [ERROR] Bootstrap Python does not exist: %PYTHON_BOOTSTRAP%
  exit /b 2
)

if not exist ".venv\\Scripts\\python.exe" (
  "%PYTHON_BOOTSTRAP%" -m venv .venv
  if errorlevel 1 exit /b 3
)

.venv\\Scripts\\python.exe -m pip install --disable-pip-version-check --cache-dir "%PIP_CACHE_DIR%" -r requirements.txt
if errorlevel 1 exit /b 4
                    '''
                }
            }
        }

        stage('环境预检') {
            steps {
                dir('api-automation-python') {
                    bat '''
@echo off
if not exist ".venv\\Scripts\\python.exe" (
  echo [ERROR] Python virtual environment does not exist.
  exit /b 2
)

.venv\\Scripts\\python.exe --version
.venv\\Scripts\\python.exe -m pip check

where allure
if errorlevel 1 (
  echo [ERROR] Allure CLI is not available in PATH.
  exit /b 3
)
allure --version

powershell.exe -NoProfile -Command ^
  "$response = Invoke-WebRequest -Uri '%TB_BASE_URL%/login' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -ne 200) { exit 4 }"
                    '''
                }
            }
        }

        stage('接口回归') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'thingsboard-tenant-admin',
                        usernameVariable: 'TB_TENANT_USERNAME',
                        passwordVariable: 'TB_TENANT_PASSWORD'
                    ),
                    usernamePassword(
                        credentialsId: 'thingsboard-customer-user',
                        usernameVariable: 'TB_CUSTOMER_USERNAME',
                        passwordVariable: 'TB_CUSTOMER_PASSWORD'
                    )
                ]) {
                    dir('api-automation-python') {
                        bat 'call run-regression.cmd'
                    }
                }
            }
        }
    }

    post {
        always {
            junit(
                allowEmptyResults: true,
                testResults: 'api-automation-python/reports/pytest-results.xml'
            )

            archiveArtifacts(
                allowEmptyArchive: true,
                artifacts: 'api-automation-python/allure-results/**, api-automation-python/allure-report/**, api-automation-python/reports/*.xml'
            )

            allure(
                includeProperties: false,
                results: [[path: 'api-automation-python/allure-results']]
            )
        }

        success {
            echo 'ThingsBoard API 回归通过。'
        }

        unsuccessful {
            echo 'ThingsBoard API 回归未通过，请查看 JUnit、Allure 和控制台日志。'
        }
    }
}
