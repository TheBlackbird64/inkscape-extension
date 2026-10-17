
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