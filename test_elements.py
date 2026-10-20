import ctypes
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

u32 = ctypes.windll.user32
hdesk = u32.OpenInputDesktop(0, False, 0x01FF)
if hdesk:
    u32.SetThreadDesktop(hdesk)

import uiautomation as auto

def inspect_elements():
    print("Finding interactive controls across windows...")
    count = 0
    for w in auto.GetRootControl().GetChildren():
        if not w.Name or not w.BoundingRectangle.width():
            continue
        # search buttons and edits
        for control, depth in auto.WalkControl(w, maxDepth=3):
            if control.ControlTypeName in ("ButtonControl", "EditControl", "HyperlinkControl", "MenuItemControl"):
                r = control.BoundingRectangle
                if r.width() > 10 and r.height() > 10:
                    cx = r.left + r.width() // 2
                    cy = r.top + r.height() // 2
                    print(f"[{control.ControlTypeName}] '{control.Name}' -> center: ({cx}, {cy})")
                    count += 1
                    if count >= 25:
                        return

inspect_elements()
