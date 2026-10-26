# Types text into a running Flip Studio window (WM_CHAR per character), without touching the real
# keyboard: for a field that already has focus, e.g. after click.ps1 on it.
# Coordinates are those of the window picture a screenshot shows (frame included).
# -TargetPid is required: without it the click went to whatever window was in front (2026-10-23 it
# landed in another app of Jorge's because the pid came as -ProcessId, which was silently ignored).
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidateRange(1, [int]::MaxValue)][int]$TargetPid,
    [Parameter(Mandatory = $true)][string]$Text
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
foreach ($ch in $Text.ToCharArray()) {
    [void][FlipInput]::PostMessageW($h, 0x0102, [IntPtr][int]$ch, [IntPtr]1)   # WM_CHAR
    Start-Sleep -Milliseconds 40
}
Write-Output "typed $($Text.Length) characters"
