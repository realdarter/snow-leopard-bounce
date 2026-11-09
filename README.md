# snow leopard bounce

it puts 50 cats on your screen and they bounce around. that's pretty much it.

use the sliders to change how many cats there are or how fast they go. they speed up when they hit the edge, then slow back down. you can click right through them, and they keep going when you minimize the main window. close it or hit **stop cats** to get rid of them and stop the music.

## run it

on a Windows PC, paste this into PowerShell:

```powershell
irm https://raw.githubusercontent.com/realdarter/snow-leopard-bounce/main/run-once.ps1 | iex
```

it downloads the latest release, runs it, and removes the temporary files when you close the app. leave PowerShell open while the cats are running.

you can also grab [the ZIP from Releases](https://github.com/realdarter/snow-leopard-bounce/releases), unzip it, and open `SnowLeopardBounce.exe`. no Python needed for that.

## music

it plays [Blue Skies by Silent Partner](https://www.youtube.com/watch?v=5kDO8hLu9iI). i have permission to include the MP3. if you want your own song, put a file called `song.mp3` next to the EXE. there's a backup tune if the MP3 won't play.

## build it yourself

on Windows, with Python installed:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean SnowLeopardBounce.spec
```

the cat photo is mine. the backup tune was made for this app.
