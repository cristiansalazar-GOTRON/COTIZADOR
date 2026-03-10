$ErrorActionPreference = "Stop"

# Configuración
$AppName = "Cotizador Automatico"
$InstallDir = "C:\Program Files\Cotizador Automatico"
$SourceDir = "c:\PROGRAMAS CRISTIAN\COTIZADOR AUTOMATICO\dist"
$IconPath = "c:\PROGRAMAS CRISTIAN\COTIZADOR AUTOMATICO\cotizador.ico"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Instalador - $AppName" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar permisos de administrador
$isAdmin = [Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains `
    [Security.Principal.SecurityIdentifier]"S-1-5-32-544"

if (-not $isAdmin) {
    Write-Host "Error: Este instalador requiere permisos de administrador." -ForegroundColor Red
    Write-Host "Por favor, ejecute como administrador." -ForegroundColor Red
    exit 1
}

# Crear carpeta de instalación
Write-Host "Creando carpeta de instalación..." -ForegroundColor Yellow
if (Test-Path $InstallDir) {
    Write-Host "La carpeta ya existe. Realizando actualización..." -ForegroundColor Yellow
    Remove-Item "$InstallDir\cotizador.exe" -ErrorAction SilentlyContinue
} else {
    New-Item -ItemType Directory -Path $InstallDir | Out-Null
}

# Copiar archivos
Write-Host "Copiando archivos..." -ForegroundColor Yellow
Copy-Item "$SourceDir\cotizador.exe" "$InstallDir\" -Force
Copy-Item $IconPath "$InstallDir\" -Force

# Crear acceso directo en Inicio
Write-Host "Creando acceso directo en el menú Inicio..." -ForegroundColor Yellow
$StartMenuDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Cotizador Automatico"
if (-not (Test-Path $StartMenuDir)) {
    New-Item -ItemType Directory -Path $StartMenuDir | Out-Null
}

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$StartMenuDir\Cotizador de Equipos.lnk")
$Shortcut.TargetPath = "$InstallDir\cotizador.exe"
$Shortcut.IconLocation = "$InstallDir\cotizador.ico,0"
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Save()

# Crear acceso directo en Escritorio
Write-Host "Creando acceso directo en el Escritorio..." -ForegroundColor Yellow
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$DesktopShortcut = $WshShell.CreateShortcut("$DesktopPath\Cotizador de Equipos.lnk")
$DesktopShortcut.TargetPath = "$InstallDir\cotizador.exe"
$DesktopShortcut.IconLocation = "$InstallDir\cotizador.ico,0"
$DesktopShortcut.WorkingDirectory = $InstallDir
$DesktopShortcut.Save()

# Crear entrada en Desinstalar programas
Write-Host "Registrando en Desinstalar programas..." -ForegroundColor Yellow
$RegPath = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\CotizadorAutomatico"
if (-not (Test-Path $RegPath)) {
    New-Item -Path $RegPath -Force | Out-Null
}

$UninstallScript = "$InstallDir\uninstall.ps1"
New-Item -ItemType File -Path $UninstallScript -Force | Out-Null
Add-Content $UninstallScript @"
`$ErrorActionPreference = "SilentlyContinue"
`$InstallDir = "$InstallDir"
`$StartMenuDir = "$StartMenuDir"
`$DesktopPath = [Environment]::GetFolderPath("Desktop")

Remove-Item "`$InstallDir" -Recurse -Force
Remove-Item "`$StartMenuDir" -Recurse -Force
Remove-Item "`$DesktopPath\Cotizador de Equipos.lnk" -Force
Remove-Item "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\CotizadorAutomatico" -Force

Write-Host "Desinstalación completada." -ForegroundColor Green
"@

Set-ItemProperty -Path $RegPath -Name "DisplayName" -Value "Cotizador de Equipos de Importacion"
Set-ItemProperty -Path $RegPath -Name "DisplayVersion" -Value "0.1.0"
Set-ItemProperty -Path $RegPath -Name "UninstallString" -Value "powershell.exe -ExecutionPolicy Bypass -File `"$UninstallScript`""
Set-ItemProperty -Path $RegPath -Name "DisplayIcon" -Value "$InstallDir\cotizador.ico"
Set-ItemProperty -Path $RegPath -Name "InstallLocation" -Value $InstallDir

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "✓ Instalación completada exitosamente" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Ubicación: $InstallDir"
Write-Host "Acceso directo creado en el Menú Inicio"
Write-Host "Acceso directo creado en el Escritorio"
Write-Host ""
Write-Host "El archivo de tasas se guardará en:"
Write-Host "c:\PROGRAMAS CRISTIAN\COTIZADOR AUTOMATICO\tasas_guardadas.json"
Write-Host ""

Start-Sleep -Seconds 2
