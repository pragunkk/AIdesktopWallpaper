[Setup]
AppName=AI Wallpaper App
AppVersion=1.0
DefaultDirName={autopf}\AI Wallpaper App
DefaultGroupName=AI Wallpaper App
OutputDir=.
OutputBaseFilename=AIWallpaperInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AI Wallpaper Tray"; Filename: "{app}\wallpaper_utils.exe"
Name: "{group}\AI Wallpaper GUI"; Filename: "{app}\wallpaper_gui.exe"

[Run]
Filename: "{app}\wallpaper_utils\wallpaper_utils.exe"; Description: "Start Tray Utility"; Flags: nowait postinstall skipifsilent

[Registry]
; Add tray utility to Windows startup for current user
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "AIWallpaperTray"; ValueData: """{app}\wallpaper_utils.exe"""