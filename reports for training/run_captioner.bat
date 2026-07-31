@echo off
set PY= C:\Users\HP\AppData\Local\Programs\Python\Python311\python.exe
cd /d "d:\Dhaniyal\reports for training"
if "%~1"=="" (
  echo Please provide an image path.
  echo Example: run_captioner.bat "D:\somefolder\photo.jpg"
  exit /b 1
)
%PY% caption_from_image.py "%~1"
