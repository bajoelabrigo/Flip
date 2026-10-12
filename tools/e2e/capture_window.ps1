# Open the portable Flip Studio on a test project, click a coordinate in the window,
# and save a screenshot so the UI can be inspected without a human at the keyboard.
param(
    [string]$Exe,
    [string]$Project,
    [string]$OutFile,
    [int]$X = 0,
    [int]$Y = 0,
    [int]$WaitSeconds = 16,
    [switch]$NoClick
)
Add-Type -AssemblyName System.Drawing
if (-not ("FlipWin" -as [type])) {
Add-Type @"
using System; using System.Runtime.InteropServices;
public class FlipWin {
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint x, uint y, int d, IntPtr e);
  public struct RECT { public int L, T, R, B; } }
"@
}
$p = Start-Process -FilePath $Exe -ArgumentList "`"$Project`"" -PassThru
Start-Sleep -Seconds $WaitSeconds
$p.Refresh()
[FlipWin]::ShowWindow($p.MainWindowHandle, 3) | Out-Null
Start-Sleep -Seconds 2
$h = $p.MainWindowHandle
$r = New-Object FlipWin+RECT
[FlipWin]::GetWindowRect($h, [ref]$r) | Out-Null
if (-not $NoClick) {
    [FlipWin]::SetForegroundWindow($h) | Out-Null
    [FlipWin]::SetCursorPos($r.L + $X, $r.T + $Y) | Out-Null
    Start-Sleep -Milliseconds 300
    [FlipWin]::mouse_event(2, 0, 0, 0, [IntPtr]::Zero)
    [FlipWin]::mouse_event(4, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 1500
}
$bmp = New-Object System.Drawing.Bitmap ($r.R - $r.L), ($r.B - $r.T)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$dc = $g.GetHdc()
[FlipWin]::PrintWindow($h, $dc, 2) | Out-Null
$g.ReleaseHdc($dc)
$bmp.Save($OutFile)
$g.Dispose(); $bmp.Dispose()
Write-Output "window $($r.R - $r.L)x$($r.B - $r.T) -> $OutFile (pid $($p.Id))"
Stop-Process -Id $p.Id -Force
