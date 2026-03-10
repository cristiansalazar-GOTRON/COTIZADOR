@echo off
REM Instalador para Cotizador Automatico
REM Este script solicita permisos de administrador e instala la aplicacion

setlocal enabledelayedexpansion

REM Verificar si se ejecuta como administrador
net session >nul 2>&1
if errorlevel 1 (
    echo.
    echo ================================================
    echo Solicitud de Permisos de Administrador
    echo ================================================
    echo Este instalador requiere permisos de administrador.
    echo.
    echo Se abrira una nueva ventana solicitando permisos...
    echo.
    timeout /t 2 /nobreak
    
    REM Ejecutar de nuevo con permisos elevados
    powershell -Command "Start-Process cmd.exe -ArgumentList '/c cd /d %~dp0 && instalar.bat' -Verb RunAs" -WindowStyle Hidden
    exit /b
)

REM Ejecutar el script PowerShell
echo.
echo ================================================
echo Iniciando instalacion...
echo ================================================
echo.

powershell.exe -ExecutionPolicy Bypass -File "%~dp0instalar.ps1"

if errorlevel 1 (
    echo.
    echo Error durante la instalacion.
    echo Por favor, intente de nuevo.
    pause
    exit /b 1
)

echo.
echo Instalacion completada.
echo Presione cualquier tecla para cerrar esta ventana...
pause >nul
