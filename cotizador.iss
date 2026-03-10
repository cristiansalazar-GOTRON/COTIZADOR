[Setup]
AppName=Cotizador de Equipos de Importacion
AppVersion=0.1.0
AppPublisher=Tu Empresa
AppPublisherURL=
AppSupportURL=
AppUpdatesURL=
DefaultDirName={autopf}\Cotizador Automatico
DefaultGroupName=Cotizador Automatico
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\cotizador.exe
OutputDir=instaladores
OutputBaseFilename=Cotizador_Automatico_Setup
SetupIconFile=cotizador.ico

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\cotizador.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "cotizador.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Cotizador de Equipos"; Filename: "{app}\cotizador.exe"; IconFilename: "{app}\cotizador.ico"
Name: "{group}\{cm:UninstallProgram,Cotizador de Equipos}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Cotizador de Equipos"; Filename: "{app}\cotizador.exe"; IconFilename: "{app}\cotizador.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\cotizador.exe"; Description: "{cm:LaunchProgram,Cotizador de Equipos}"; Flags: nowait postinstall skipifsilent
