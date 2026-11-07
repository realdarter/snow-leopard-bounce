# Snow Leopard Bounce

Fifty cat pictures bounce around the screen. Use the two sliders to change how many cats there are (0–100) and how fast they go. They speed up after a bounce, then slow back down. Close the main window to stop everything.

## Run on a Windows PC

Download the latest `SnowLeopardBounce-Windows.zip` from [Releases](https://github.com/realdarter/snow-leopard-bounce/releases), extract it, and run `SnowLeopardBounce.exe` inside the extracted folder. No Python installation is needed.

To run it once and remove the temporary app files after closing it, paste this command into PowerShell. It does not remove files you manually downloaded or extracted. The readable version is in [run-once.ps1](run-once.ps1).

```powershell
$ErrorActionPreference='Stop'; $t=[IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\'); $n='SnowLeopardBounce-'+[guid]::NewGuid().ToString('N'); $d=Join-Path $t $n; New-Item -ItemType Directory -Path $d | Out-Null; try { $z=Join-Path $d 'app.zip'; Invoke-WebRequest -UseBasicParsing 'https://github.com/realdarter/snow-leopard-bounce/releases/latest/download/SnowLeopardBounce-Windows.zip' -OutFile $z; Expand-Archive -LiteralPath $z -DestinationPath $d; Start-Process -FilePath (Join-Path $d 'SnowLeopardBounce\SnowLeopardBounce.exe') -Wait } finally { $p=[IO.Path]::GetFullPath($d); $i=Get-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue; if($i -and $p.StartsWith($t+'\',[StringComparison]::OrdinalIgnoreCase) -and $i.Name -eq $n -and -not ($i.Attributes -band [IO.FileAttributes]::ReparsePoint)) { Remove-Item -LiteralPath $p -Recurse -Force } }
```

The release plays [Blue Skies by Silent Partner](https://www.youtube.com/watch?v=5kDO8hLu9iI). The project owner confirmed redistribution permission for this recording. If you have the rights to use a different track, place an MP3 named `song.mp3` next to `SnowLeopardBounce.exe`. The app will play it instead. An original tune is included as a playback fallback.

## Build from source

On Windows with Python and PyInstaller:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --onedir --windowed --name SnowLeopardBounce --icon cat.ico --add-data 'cat.ico;.' --add-data 'cat-small.png;.' --add-data 'cat-large.png;.' --add-data 'cat-tune.wav;.' --add-data 'Blue-Skies.mp3;.' snow_leopard_bounce.pyw
```

The cat photo was supplied by the project owner. The fallback tune was created for this app.
