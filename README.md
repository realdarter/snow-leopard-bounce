# Snow Leopard Bounce

Fifty cats bounce around your screen. The sliders set the number of cats (0–100) and their speed. They speed up after hitting an edge, then slow back down. Close the main window to stop them.

## Run on a Windows PC

Download `SnowLeopardBounce-Windows.zip` from [Releases](https://github.com/realdarter/snow-leopard-bounce/releases), unzip it, and run `SnowLeopardBounce.exe`. You don't need Python.

To run it once without keeping the downloaded files, paste this into PowerShell. It cleans up when you close the app. The same code is in [run-once.ps1](run-once.ps1).

```powershell
$ErrorActionPreference='Stop'; $t=[IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\'); $n='SnowLeopardBounce-'+[guid]::NewGuid().ToString('N'); $d=Join-Path $t $n; New-Item -ItemType Directory -Path $d | Out-Null; try { $z=Join-Path $d 'app.zip'; Invoke-WebRequest -UseBasicParsing 'https://github.com/realdarter/snow-leopard-bounce/releases/latest/download/SnowLeopardBounce-Windows.zip' -OutFile $z; Expand-Archive -LiteralPath $z -DestinationPath $d; Start-Process -FilePath (Join-Path $d 'SnowLeopardBounce\SnowLeopardBounce.exe') -Wait } finally { $p=[IO.Path]::GetFullPath($d); $i=Get-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue; if($i -and $p.StartsWith($t+'\',[StringComparison]::OrdinalIgnoreCase) -and $i.Name -eq $n -and -not ($i.Attributes -band [IO.FileAttributes]::ReparsePoint)) { Remove-Item -LiteralPath $p -Recurse -Force } }
```

The app plays [Blue Skies by Silent Partner](https://www.youtube.com/watch?v=5kDO8hLu9iI). The owner confirmed permission to include it. To use a different MP3, put a file named `song.mp3` next to the EXE. There's also a backup tune if MP3 playback fails.

## Build from source

On Windows with Python and PyInstaller:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --onedir --windowed --name SnowLeopardBounce --icon cat.ico --add-data 'cat.ico;.' --add-data 'cat-small.png;.' --add-data 'cat-large.png;.' --add-data 'cat-tune.wav;.' --add-data 'Blue-Skies.mp3;.' snow_leopard_bounce.pyw
```

The cat photo came from the owner. The backup tune was made for this app.
