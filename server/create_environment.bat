@echo off
setlocal

:: Create the python environment of the server, and generate the config file (url + api key)
pushd "%~dp0"

if exist .venv rmdir /S /Q .venv
python -m venv .venv || goto :error
.venv\Scripts\python.exe -m pip install -r requirements.txt || goto :error

:: openssl is not available by default on windows: python generates the api key
for /f %%K in ('.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"') do set API_KEY=%%K
if "%API_KEY%"=="" goto :error

(
    echo [server]
    echo url = http://localhost:8000/
    echo api_key = %API_KEY%
) > config.ini

:: equivalent of chmod 600: only the current user can read the api key
icacls config.ini /inheritance:r /grant:r "%USERDOMAIN%\%USERNAME%:F" >nul || goto :error

echo API_KEY generated (copy the config.ini file and paste it next to the extensions files)
popd
exit /b 0

:error
echo Erreur lors de la creation de l'environnement
popd
exit /b 1
