param(
    [string]$ArchivePath
)

$ErrorActionPreference = 'Stop'
$tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\')
$runName = 'SnowLeopardBounce-' + [guid]::NewGuid().ToString('N')
$runDir = Join-Path $tempRoot $runName
New-Item -ItemType Directory -Path $runDir | Out-Null

try {
    $zip = Join-Path $runDir 'app.zip'
    if ($ArchivePath) {
        Copy-Item -LiteralPath $ArchivePath -Destination $zip
    } else {
        Invoke-WebRequest -UseBasicParsing `
            -Uri 'https://github.com/realdarter/snow-leopard-bounce/releases/latest/download/SnowLeopardBounce-Windows.zip' `
            -OutFile $zip
    }
    Expand-Archive -LiteralPath $zip -DestinationPath $runDir
    $exe = Join-Path $runDir 'SnowLeopardBounce\SnowLeopardBounce.exe'
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
        throw 'The release ZIP did not contain SnowLeopardBounce.exe.'
    }
    $process = Start-Process -FilePath $exe -PassThru -Wait
    if ($process.ExitCode -ne 0) {
        throw "SnowLeopardBounce exited with code $($process.ExitCode)."
    }
} finally {
    $absoluteRunDir = [IO.Path]::GetFullPath($runDir)
    $folder = Get-Item -LiteralPath $absoluteRunDir -Force -ErrorAction SilentlyContinue
    $insideTemp = $absoluteRunDir.StartsWith(
        $tempRoot + [IO.Path]::DirectorySeparatorChar,
        [StringComparison]::OrdinalIgnoreCase
    )
    if ($folder -and $insideTemp -and $folder.Name -eq $runName -and
        -not ($folder.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        Remove-Item -LiteralPath $absoluteRunDir -Recurse -Force
    }
}
