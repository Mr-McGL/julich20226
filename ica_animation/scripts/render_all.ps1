$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
python run.py render --scene all --preset full --output output/ica_animation.mp4 @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
