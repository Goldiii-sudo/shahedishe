# ARCHITECTURE & SUBSYSTEM SPECIFICATION

Detailed engineering reference for the Antigravity Agent codebase.

---

## 1. AGENT ORCHESTRATION & STATE MACHINE (`core/agent.py`)

### Execution Loop:
1. **Screen Capture (`tools/screen.py`)**:
   - `capture_screen()` grabs desktop via Win32 GDI `BitBlt` using `SetThreadDesktop(OpenInputDesktop)`.
   - Dynamic 100px guide grid drawn with intersection tags every 200px.
   - User mouse position evaluated via `tools.os_control.get_real_user_mouse_pos()`.
2. **Context Compilation**:
   - Dynamic persona loaded from `prompts/*.md`.
   - History of previous steps (observation, thought, action, result) formatted into `TASK_TEMPLATE`.
   - Mandatory user language directive injected (`LANGUAGE_RULE`).
3. **Vision LLM Inference**:
   - Request dispatched to `http://localhost:8083/v1/chat/completions` (OpenAI format).
   - High-resolution JPEG base64 payload.
4. **Action Execution**:
   - Matches structured JSON action (`click_captcha`, `ui_click`, `click_user_cursor`, `click`, `type_text`, `bash`, `browser_*`, etc.).
   - Updates always-on-top HUD overlay (`ui/overlay.py`).
   - Dispatches result to live WebSocket listeners.
5. **Persistence**:
   - Every message and step recorded to `data/sessions/{session_id}.json`.

---

## 2. LOW-LEVEL INPUT & ANTI-DETECTION PHYSICS (`tools/os_control.py`)

### Desktop Attachment:
Windows services or secondary threads must call `_attach_desktop()` before invoking `user32` cursor APIs:
```python
hdesk = u32.OpenInputDesktop(0, False, 0x01FF)
u32.SetThreadDesktop(hdesk)
```

### Cubic Bézier Trajectory Generation:
Instantaneous `SetCursorPos` triggers bot detection in hCaptcha and anti-cheats. Mouse paths are generated using:
$$B(t) = (1-t)^3 P_0 + 3(1-t)^2 t P_1 + 3(1-t) t^2 P_2 + t^3 P_3$$
* $P_0$: Current mouse coordinates.
* $P_1$: Point at 30% distance deflected perpendicularly by random offset.
* $P_2$: Point at 75% distance with damped deflection.
* $P_3$: Target coordinates.
* Easing parameter: $t = 0.5 \cdot (1 - \cos(\pi \cdot t_{\text{raw}}))$ (smooth cosine ease-in and ease-out).
* Micro-jitter: Sub-pixel Gaussian jitter injected into $x, y$ coordinates fading to 0 near the arrival target.

### Real Human vs. Agent Cursor Disambiguation:
To prevent feedback loops where the agent mistakes its own previous click for human input:
* `record_agent_mouse_pos(x, y)` stores the agent's target position.
* `get_real_user_mouse_pos()` returns coordinates only if $\Delta > 15\text{px}$. If $\Delta \le 15\text{px}$, it returns `None`.

---

## 3. TARGETING & ELEMENT RECOGNITION (`tools/ui_finder.py` & `tools/captcha.py`)

### Hybrid Locator Cascade:
1. **Captcha Interceptor**:
   If target string contains `"captcha"`, `"капч"`, `"hcaptcha"`, `"recaptcha"`, `"turnstile"`, or `"чекбокс"`, execution delegates directly to `tools.captcha.find_captcha_checkbox()`.
2. **Windows UI Automation (UIA)**:
   - Scans active window controls (`root.GetChildren()`).
   - Filters out browser tabs and window chrome (`TabItemControl`, `TitleBarControl`, `HeaderItemControl`, `WindowControl`) unless explicitly requested.
   - Computes element bounding box center.
3. **Tesseract OCR**:
   - Fallback for custom rendered UI.
   - Extracts bounding boxes via `image_to_data` with confidence threshold $> 30$.

### Captcha Detection Algorithm (`tools/captcha.py`):
* **hCaptcha**:
  1. Computes HSV color mask for teal logo ($H \in [75, 105]$, $S > 90$, $V > 90$).
  2. Bounding rectangle search window placed $175\text{px} \dots 265\text{px}$ to the left of the logo.
  3. Strict contour thresholding finds rounded rectangle with aspect ratio $0.75 \dots 1.3$ and dimensions $18\text{px} \dots 42\text{px}$.
  4. Returns exact center $(x, y)$.
* **Google reCAPTCHA / Cloudflare Turnstile**:
  - Scans OCR text for anchor words (`"человек"`, `"human"`, `"робот"`, `"robot"`).
  - Searches for checkbox rectangle immediately adjacent to the anchor.

---

## 4. BROWSER CDP & DOM AUTOMATION (`tools/browser_cdp.py`)

Based on verified techniques from `autoreger.js`:
1. **Frame Traversal (`solve_captcha`)**:
   Iterates through `page.frames`:
   ```python
   for frame in page.frames:
       if ("hcaptcha" in frame.url or "recaptcha" in frame.url) and "checkbox" in frame.url:
           await frame.locator("#checkbox").click(timeout=3000)
   ```
2. **DOM Rect Calculator (`get_element_rect`)**:
   Calls `getBoundingClientRect()` inside page evaluate context:
   ```javascript
   const rect = el.getBoundingClientRect();
   return { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
   ```

---

## 5. UI & PERSISTENCE ARCHITECTURE

* **Edge WebView2 Window**: Managed via `webview.create_window` in `desktop_app.py`.
* **Dark Theme**: Deep space dark (`#090d16`), panels (`#0e1526`), borders (`#1e293b`), accents (`#6366f1` / `#38bdf8`).
* **Icons**: Inline SVG icons (Spark, Folder, Chat, Sliders, Trash, Check, User). Zero emoji characters.
* **Storage**:
  - `data/sessions/{id}.json`: Complete history, timestamps, step telemetry, and message logs.
  - `data/settings.json`: User configurations (model selection, mouse smoothing, grid overlay).
