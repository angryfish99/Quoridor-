@echo off
echo Preparing web build directory...
if not exist "web_source" mkdir "web_source"
copy main.py web_source\main.py > nul
copy requirements.txt web_source\requirements.txt > nul
xcopy src web_source\src /E /I /Y > nul
xcopy assets web_source\assets /E /I /Y > nul

echo Building Quoridor for Web...
python -m pygbag --build web_source

echo.
echo Build complete!
echo To play locally, run: python -m pygbag web_source
