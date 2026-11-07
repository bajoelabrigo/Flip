# Before every CI build (0.30.2, Jorge: four builds lost in a day to a test that a local check finds in seconds).
#
#   pwsh tools/precheck.ps1          # from the repo root
#
# 1. Translations: runs lupdate exactly as the CI's Translations test does, on copies of i18n/*.ts, and fails
#    if the catalogs would change (a new or renamed qsTr/tr text that is not in them yet). With -Fix it
#    writes lupdate's output back to i18n/ so the new texts can be translated before pushing.
# 2. QML syntax: qmlformat parses every QML file changed against main; a file that does not parse fails here
#    instead of after an hour of CI.
param([switch]$Fix)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$bin = Join-Path $root '.qtmingw\6.10.3\mingw_64\bin'
if (-not (Test-Path "$bin\lupdate.exe")) {
    Write-Host "No local lupdate. Install it once (see CLAUDE.md, «Comprobar los catálogos sin depender de CI»)."
    exit 2
}
$failed = $false

# 1. Translations
# Inside the repo (.qmcheck is git-ignored scratch): the system temp folder is not always writable.
$tmp = Join-Path $root ('.qmcheck\precheck-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force $tmp | Out-Null
$copies = @()
foreach ($ts in Get-ChildItem i18n\drift*.ts) {
    $copy = Join-Path $tmp $ts.Name
    Copy-Item $ts.FullName $copy
    $copies += $copy
}
$out = & "$bin\lupdate.exe" src i18n -no-obsolete -locations none -disable-heuristic sametext -disable-heuristic similartext -ts @copies 2>&1
if ($LASTEXITCODE -ne 0 -or ($out | Select-String 'Cannot create')) {
    Write-Host "lupdate could not run:"; $out | Select-String 'Cannot|rror' | Select-Object -First 5 | ForEach-Object { Write-Host "   $_" }
    exit 2
}
$changed = @()
foreach ($copy in $copies) {
    $orig = Join-Path 'i18n' (Split-Path -Leaf $copy)
    $a = (Get-Content -Raw $orig) -replace "`r", ''
    $b = (Get-Content -Raw $copy) -replace "`r", ''
    if ($a -ne $b) { $changed += (Split-Path -Leaf $copy) }
}
if ($changed.Count -gt 0) {
    $failed = $true
    Write-Host "TRANSLATIONS: lupdate would change $($changed.Count) catalogs ($($changed -join ', '))."
    $first = Join-Path $tmp $changed[0]
    $diff = Compare-Object ((Get-Content (Join-Path 'i18n' $changed[0])) -replace "`r", '') ((Get-Content $first) -replace "`r", '')
    $diff | Select-Object -First 12 | ForEach-Object { Write-Host "   $($_.SideIndicator) $($_.InputObject)" }
    if ($Fix) {
        foreach ($c in $changed) { Copy-Item (Join-Path $tmp $c) (Join-Path 'i18n' $c) -Force }
        Write-Host "   Written back to i18n/: translate the new texts, then run this again."
    }
} else {
    Write-Host "Translations: OK"
}
Remove-Item -Recurse -Force $tmp

# 2. QML syntax of the files changed against main
$qml = git diff --name-only origin/main -- '*.qml' 2>$null
$bad = @()
foreach ($f in $qml) {
    if (-not (Test-Path $f)) { continue }
    & "$bin\qmlformat.exe" $f *> $null
    if ($LASTEXITCODE -ne 0) { $bad += $f }
}
if ($bad.Count -gt 0) {
    $failed = $true
    Write-Host "QML: these files do not parse:"
    $bad | ForEach-Object { Write-Host "   $_" }
} else {
    Write-Host "QML syntax: OK ($(@($qml).Count) changed files)"
}

if ($failed) { exit 1 }
Write-Host "Precheck passed."
