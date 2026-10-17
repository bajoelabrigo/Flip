# Posts a click (or wheel) to a running Flip Studio window, without moving the real mouse.
# Coordinates are those of the window picture a screenshot shows (frame included).
param(
    [int]$TargetPid = 0,
    [int]$X = 0,
    [int]$Y = 0,
    [ValidateSet('left', 'right')][string]$Button = 'left',
    [int]$Wheel = 0
)
if (-not ("FlipInput" -as [type])) {
Add-Type @"
using System; using System.Runtime.InteropServices;
public class FlipInput {
  [DllImport("user32.dll")] public static extern bool PostMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool ScreenToClient(IntPtr h, ref POINT p);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern int GetWindowTextLengthW(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  public delegate bool EnumProc(IntPtr h, IntPtr p);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr p);
  public struct POINT { public int X, Y; }
  public struct RECT { public int L, T, R, B; }
  public static IntPtr Find(uint want) {
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, p) => {
      uint pid; GetWindowThreadProcessId(h, out pid);
      if ((want == 0 || pid == want) && IsWindowVisible(h) && GetWindowTextLengthW(h) > 0) {
        if (found == IntPtr.Zero) found = h;
      }
      return true;
    }, IntPtr.Zero);
    return found;
  }
}
"@
}
$h = [FlipInput]::Find([uint32]$TargetPid)
if ($h -eq [IntPtr]::Zero) { Write-Output "no window for pid $TargetPid"; exit 1 }
$r = New-Object FlipInput+RECT
[void][FlipInput]::GetWindowRect($h, [ref]$r)
$pt = New-Object FlipInput+POINT
$pt.X = $r.L + $X; $pt.Y = $r.T + $Y
[void][FlipInput]::ScreenToClient($h, [ref]$pt)
$lp = [IntPtr](($pt.Y -shl 16) -bor ($pt.X -band 0xFFFF))
if ($Wheel -ne 0) {
    $wp = [IntPtr](([int]$Wheel -shl 16))
    [void][FlipInput]::PostMessageW($h, 0x020A, $wp, $lp)   # WM_MOUSEWHEEL
    Write-Output "wheel $Wheel at $X,$Y (client $($pt.X),$($pt.Y))"
    exit 0
}
$down = if ($Button -eq 'right') { 0x0204 } else { 0x0201 }
$up = if ($Button -eq 'right') { 0x0205 } else { 0x0202 }
$held = if ($Button -eq 'right') { 2 } else { 1 }
[void][FlipInput]::PostMessageW($h, 0x0200, [IntPtr]0, $lp)   # WM_MOUSEMOVE
Start-Sleep -Milliseconds 60
[void][FlipInput]::PostMessageW($h, $down, [IntPtr]$held, $lp)
Start-Sleep -Milliseconds 90
[void][FlipInput]::PostMessageW($h, $up, [IntPtr]0, $lp)
Write-Output "$Button-clicked $X,$Y (client $($pt.X),$($pt.Y))"
