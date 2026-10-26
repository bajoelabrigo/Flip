# Posts a left-button drag (press, moves, release) to a running Flip Studio window, without moving
# the real mouse: what click.ps1 cannot do, such as selecting letters in a text field.
# Coordinates are those of the window picture a screenshot shows (frame included).
# -TargetPid is required: without it the click went to whatever window was in front (2026-10-23 it
# landed in another app of Jorge's because the pid came as -ProcessId, which was silently ignored).
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateRange(1, [int]::MaxValue)][int]$TargetPid,
    [int]$X = 0,
    [int]$Y = 0,
    [int]$ToX = 0,
    [int]$ToY = 0,
    [int]$Steps = 8
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
function ClientLp([int]$px, [int]$py) {
    $pt = New-Object FlipInput+POINT
    $pt.X = $r.L + $px; $pt.Y = $r.T + $py
    [void][FlipInput]::ScreenToClient($h, [ref]$pt)
    return [IntPtr](($pt.Y -shl 16) -bor ($pt.X -band 0xFFFF))
}
$from = ClientLp $X $Y
[void][FlipInput]::PostMessageW($h, 0x0200, [IntPtr]0, $from)   # WM_MOUSEMOVE
Start-Sleep -Milliseconds 60
[void][FlipInput]::PostMessageW($h, 0x0201, [IntPtr]1, $from)   # WM_LBUTTONDOWN
for ($i = 1; $i -le $Steps; $i++) {
    Start-Sleep -Milliseconds 40
    $lp = ClientLp ([int]($X + ($ToX - $X) * $i / $Steps)) ([int]($Y + ($ToY - $Y) * $i / $Steps))
    [void][FlipInput]::PostMessageW($h, 0x0200, [IntPtr]1, $lp)  # WM_MOUSEMOVE, button held
}
Start-Sleep -Milliseconds 60
[void][FlipInput]::PostMessageW($h, 0x0202, [IntPtr]0, (ClientLp $ToX $ToY))   # WM_LBUTTONUP
Write-Output "dragged $X,$Y -> $ToX,$ToY"
