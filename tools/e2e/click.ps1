# Posts a click (or wheel) to a running Flip Studio window, without moving the real mouse.
# Coordinates are those of the window picture a screenshot shows (frame included).
# -TargetPid is required: without it the click went to whatever window was in front (2026-10-23 it
# landed in another app of Jorge's because the pid came as -ProcessId, which was silently ignored).
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateRange(1, [int]::MaxValue)][int]$TargetPid,
    [int]$X = 0,
    [int]$Y = 0,
    [ValidateSet('left', 'right')][string]$Button = 'left',
    [int]$Wheel = 0,
    [string]$Title = ""
)
if (-not ("FlipInput2" -as [type])) {
Add-Type @"
using System; using System.Runtime.InteropServices;
public class FlipInput2 {
  [DllImport("user32.dll")] public static extern bool PostMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool ScreenToClient(IntPtr h, ref POINT p);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern int GetWindowTextLengthW(IntPtr h);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, System.Text.StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  public delegate bool EnumProc(IntPtr h, IntPtr p);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr p);
  public struct POINT { public int X, Y; }
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
$h = [FlipInput2]::Find([uint32]$TargetPid, $Title)
if ($h -eq [IntPtr]::Zero) { Write-Output "no window for pid $TargetPid $Title"; exit 1 }
$r = New-Object FlipInput2+RECT
[void][FlipInput2]::GetWindowRect($h, [ref]$r)
$pt = New-Object FlipInput2+POINT
$pt.X = $r.L + $X; $pt.Y = $r.T + $Y
$screenLp = [IntPtr](($pt.Y -shl 16) -bor ($pt.X -band 0xFFFF))
[void][FlipInput2]::ScreenToClient($h, [ref]$pt)
$lp = [IntPtr](($pt.Y -shl 16) -bor ($pt.X -band 0xFFFF))
if ($Wheel -ne 0) {
    # WM_MOUSEWHEEL carries screen coordinates (unlike the button messages); the pointer goes
    # there first so the window knows what is under it.
    [void][FlipInput2]::PostMessageW($h, 0x0200, [IntPtr]0, $lp)   # WM_MOUSEMOVE
    Start-Sleep -Milliseconds 60
    $wp = [IntPtr](([int]$Wheel -shl 16))
    [void][FlipInput2]::PostMessageW($h, 0x020A, $wp, $screenLp)   # WM_MOUSEWHEEL
    Write-Output "wheel $Wheel at $X,$Y (client $($pt.X),$($pt.Y))"
    exit 0
}
$down = if ($Button -eq 'right') { 0x0204 } else { 0x0201 }
$up = if ($Button -eq 'right') { 0x0205 } else { 0x0202 }
$held = if ($Button -eq 'right') { 2 } else { 1 }
[void][FlipInput2]::PostMessageW($h, 0x0200, [IntPtr]0, $lp)   # WM_MOUSEMOVE
Start-Sleep -Milliseconds 60
[void][FlipInput2]::PostMessageW($h, $down, [IntPtr]$held, $lp)
Start-Sleep -Milliseconds 90
[void][FlipInput2]::PostMessageW($h, $up, [IntPtr]0, $lp)
Write-Output "$Button-clicked $X,$Y (client $($pt.X),$($pt.Y))"
