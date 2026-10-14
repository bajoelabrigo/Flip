# Upload the six new model packages to the `packages` release of flipstudio-extras.
# Each one is retried: large gh asset uploads fail often on the first try, and a partial
# release would leave the index pointing at 404s.
$ErrorActionPreference = 'Continue'
$dist = 'C:\Users\bajoe\Downloads\FlipStudio\codigo\flip-addons\dist'
$repo = 'bajoelabrigo/flipstudio-extras'
$tag = 'packages'
$names = @(
    'rostro.puntos-1.0.0.driftpkg',
    'ruido.voz-1.0.0.driftpkg',
    'recorte.personas-1.0.0.driftpkg',
    'mejorar.video-1.0.0.driftpkg',
    'profundidad-1.0.0.driftpkg',
    'recorte.sujeto-1.0.0.driftpkg'
)

foreach ($n in $names) {
    $path = Join-Path $dist $n
    if (-not (Test-Path $path)) { Write-Output "MISSING $n"; continue }
    $mb = [math]::Round((Get-Item $path).Length / 1MB, 1)
    $ok = $false
    for ($try = 1; $try -le 4 -and -not $ok; $try++) {
        Write-Output "== $n ($mb MB) try $try"
        $out = gh release upload $tag $path -R $repo --clobber 2>&1
        if ($LASTEXITCODE -eq 0) { $ok = $true; Write-Output "   OK" }
        else { Write-Output "   FAIL: $($out | Select-Object -Last 2)"; Start-Sleep -Seconds 5 }
    }
    if (-not $ok) { Write-Output "!! GAVE UP ON $n" }
}
Write-Output "=== DONE ==="
