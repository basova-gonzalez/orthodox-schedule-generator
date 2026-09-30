@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 src\gui.py
) else (
  python src\gui.py
)
if errorlevel 1 (
  echo Нужен Python 3.10 или новее с Tkinter. Проверьте установку Python.
  pause
)
