# Snow Leopard Bounce

A playful Windows app with 50 bouncing snow leopards. The square main window has sliders for the number of cats (0–100) and their average speed. Each cat briefly speeds up after a wall bounce and then returns to its average speed. Closing the main window closes every cat and stops the music.

## Run on a Windows PC

Download the latest `SnowLeopardBounce-Windows.zip` from [Releases](https://github.com/realdarter/snow-leopard-bounce/releases), extract it, and run `SnowLeopardBounce.exe` inside the extracted folder. No Python installation is needed.

Or paste this one command into PowerShell on a Windows PC to download, extract, and launch it:

```powershell
$ErrorActionPreference='Stop'; $z=Join-Path $env:TEMP 'SnowLeopardBounce-Windows.zip'; $d=Join-Path $env:LOCALAPPDATA 'SnowLeopardBounce'; Invoke-WebRequest 'https://github.com/realdarter/snow-leopard-bounce/releases/latest/download/SnowLeopardBounce-Windows.zip' -OutFile $z; Expand-Archive -LiteralPath $z -DestinationPath $d -Force; & (Join-Path $d 'SnowLeopardBounce\SnowLeopardBounce.exe')
```

The release includes an original looping tune. If you have the rights to use a different track, place an MP3 named `song.mp3` next to `SnowLeopardBounce.exe`. The app will play it instead. The music file is not included in this repository or release.

## Build from source

On Windows with Python and PyInstaller:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --onedir --windowed --name SnowLeopardBounce --icon cat.ico --add-data 'cat.ico;.' --add-data 'cat-small.png;.' --add-data 'cat-large.png;.' --add-data 'cat-tune.wav;.' snow_leopard_bounce.pyw
```

The cat photo was supplied by the project owner. The bundled tune was created for this app.
