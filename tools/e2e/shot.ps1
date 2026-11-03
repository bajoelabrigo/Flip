# Saves a PrintWindow picture of a running Flip Studio window (no mouse moves, no desktop capture).
# -TargetPid is required: without it the picture was of whatever window was in front (see click.ps1).
[CmdletBinding()]
param([string]$OutFile = "$env:TEMP\shot.png", [Parameter(Mandatory = $true)][ValidateRange(1, [int]::MaxValue)][int]$TargetPid,
      [string]$Title = "")
Add-Type -AssemblyName System.Drawing
if (-not ("FlipShotWin2" -as [type])) {
Add-Type @"
using System; using System.Runtime.InteropServices;
public class FlipShotWin2 {
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern int GetWindowTextLengthW(IntPtr h);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, System.Text.StringBuilder s, int n);
  public delegate bool EnumProc(IntPtr h, IntPtr p);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr p);
  public struct RECT { public int L, T, R, B; }
  public static IntPtr Find(uint want, string title) {
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, p) => {
      uint pid; GetWindowThreadProcessId(h, out pid);
      if ((want == 0 || pid == want) && IsWindowVisible(h) && GetWindowTextLengthW(h) > 0) {
        var text = new System.Text.StringBuilder(512); GetWindowTextW(h, text, 512);
        // With a title, that window of the app (a tool window such as «Remove silences»); else the
        // main one, «Flip Studio», which a tool window in front would otherwise win over.
        bool match = title.Length > 0 ? text.ToString().Contains(title) : text.ToString().StartsWith("Flip Studio");
        if (found == IntPtr.Zero && match) found = h;
      }
      return true;
    }, IntPtr.Zero);
    return found;
  }
}
"@
}
$h = [FlipShotWin2]::Find([uint32]$TargetPid, $Title)
if ($h -eq [IntPtr]::Zero) { Write-Output "no window for pid $TargetPid $Title"; exit 1 }
$r = New-Object FlipShotWin2+RECT
[void][FlipShotWin2]::GetWindowRect($h, [ref]$r)
$w = $r.R - $r.L; $ht = $r.B - $r.T
$bmp = New-Object System.Drawing.Bitmap($w, $ht)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$dc = $g.GetHdc()
$ok = [FlipShotWin2]::PrintWindow($h, $dc, 0)
$g.ReleaseHdc($dc)
$g.Dispose()
if (-not $ok) { $bmp.Dispose(); Write-Output "PrintWindow failed"; exit 1 }
$bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output "saved $OutFile ($w x $ht)"
