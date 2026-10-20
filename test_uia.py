import ctypes
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

u32 = ctypes.windll.user32
hdesk = u32.OpenInputDesktop(0, False, 0x01FF)
if hdesk:
    u32.SetThreadDesktop(hdesk)

import uiautomation as auto

root = auto.GetRootControl()
print("Top-level Windows on InputDesktop:")
for w in root.GetChildren():
    r = w.BoundingRectangle
    if w.Name and r.width() > 50:
        print(f"[{w.ControlTypeName}] '{w.Name[:50]}' -> rect: ({r.left}, {r.top}, {r.right}, {r.bottom})")
