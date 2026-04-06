@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo No se encontro ".venv\Scripts\python.exe"
  echo Crea o repara el entorno virtual antes de continuar.
  exit /b 1
)

".venv\Scripts\python.exe" main.py
