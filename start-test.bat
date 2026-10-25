
:: In the client file, we use libs that are not installed by default. We create a lib folder and we install the libs in it.
set ext=%APPDATA%\inkscape\extensions\

if not exist %ext%\libs (
    mkdir %ext%\libs
)

pip install requests --target %ext%\libs

:: inx files
copy inx-files\load.inx %ext%
copy inx-files\save.inx %ext%

:: python files
copy push.py %ext%
copy pull.py %ext%

:: config file
copy config.ini %ext%

:: restart the FastAPI server with its virtual environment
pushd "%~dp0server"
if not exist ".venv\Scripts\python.exe" (
    echo Le venv du serveur est introuvable.
    popd
    exit /b 1
)

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /PID %%P /F >nul 2>&1
start "FastAPI server" /b ".venv\Scripts\python.exe" server.py
popd

:: start inkscape
start inkscape