# DEVELOPER JOURNAL & INCIDENT CHANGELOG

Log of architectural decisions, root cause analyses, and completed refactorings.

---

### [2026-10-16] Incident 01: Captcha Checkbox Misclick & Browser Tab Hijack
* **Symptoms**:
  In session `sess_1792173560_ca2611`, agent repeatedly missed the hCaptcha checkbox on `https://lessons.zennolab.com/captchas/hcaptcha/?level=easy`, clicking the browser tab bar and random background space instead.
* **Root Causes**:
  1. `ui_finder.find_element_by_uia("hCaptcha")` matched the browser window tab `hCaptcha: Easy` (`TabItemControl`) at coordinates `(1012, 22)`.
  2. Agent's mouse move to `(570, 450)` left the system cursor there. On next step, `screen.py` queried `get_mouse_pos()`, mistook the agent's own cursor for the human user's cursor, stamped `USER MOUSE: (570, 450)` on the screenshot, and fed this hallucinated coordinate back to the model.
  3. `gemini-3.5-flash-lite` lacked direct sub-pixel bounding box anchoring for small web iframes.
* **Resolution**:
  - Created [`tools/captcha.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/tools/captcha.py) with dedicated HSV teal color mask and contour geometry. Validated on screenshot — hits exact center `(864, 489)`.
  - Added action `click_captcha` in [`core/agent.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/core/agent.py).
  - Intercepted captcha-related search targets in [`tools/ui_finder.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/tools/ui_finder.py).
  - Filtered out `TabItemControl` and `TitleBarControl` from UIA element matching.
  - Added `get_real_user_mouse_pos()` in [`tools/os_control.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/tools/os_control.py) to ignore cursor positions within 15px of previous agent clicks.

---

### [2026-10-16] Feature 02: Integration of Techniques from `autoreger.js`
* **Context**:
  Analyzed reference script `c:\Users\MSI\Downloads\autoreger.js`.
* **Integrated Patterns**:
  1. Frame traversal for iframe-embedded captchas:
     `page.frames()` iterated for URLs matching `hcaptcha` / `recaptcha`, followed by direct `#checkbox` triggering.
  2. Physical block center computation via DOM `getBoundingClientRect()`:
     `{ x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 }`.
* **Implementation**:
  Added `solve_captcha()` and `get_element_rect()` to [`tools/browser_cdp.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/tools/browser_cdp.py).

---

### [2026-10-16] Refactor 03: Complete Removal of Web Version & Emoji Purge
* **Context**:
  User requested eliminating separate web browser dashboard workflows and stripping all emojis.
* **Changes**:
  - Unified entry point in [`main.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/main.py): launches native Edge WebView2 desktop app directly.
  - Rewrote [`run_app.bat`](file:///c:/Users/MSI/Downloads/local-devin-agent/run_app.bat) to launch `main.py`.
  - Audited all `.py` files to guarantee 100% emoji-free codebase.
  - Replaced all UI icons with minimalist inline SVG vector graphics matching the Google Antigravity IDE theme.

---

### [2026-10-16] Feature 04: Anti-Bot Mouse Trajectories & Persistence
* **Implementation**:
  - Cubic Bézier mouse paths with cosine easing and Gaussian micro-jitter in [`tools/os_control.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/tools/os_control.py).
  - Session history persistence in `data/sessions/*.json`.
  - Settings persistence in `data/settings.json`.
  - Dynamic prompt loader in `prompts/custom_prompt.md` with strict user language enforcement.

---

### [2026-10-16] Feature 05: 1:1 Antigravity Bar, Media Attachments & Sub-5s Performance
* **Context**:
  User requested 1:1 visual match to Antigravity IDE input bar (`media_1792174866286_0fbd9d12.png`), photo/video attachment support, selectable read-only text, removal of pause/stop buttons, thinking mode selector (Turbo / Fast / Deep Think), and sub-5-second step speed.
* **Key Improvements**:
  1. **Latency & Speed (< 5s / step)**:
     - Profiled PIL JPEG serialization: removed CPU-heavy `optimize=True`, reducing frame encoding from ~250ms to 5.7ms.
     - Switched screenshot disk writes to background daemon threads (`threading.Thread`).
     - Shortened Bézier mouse duration from 120–360ms to 60–180ms.
     - Defaulted model to `gemini-3.8-flash` (~2.9s text, ~5.5s 1080p vision).
     - Reduced `AGENT_STEP_DELAY` to 0.1s.
  2. **1:1 Antigravity Input Bar**:
     - Embedded `.ag-input-box` container with auto-expanding textarea.
     - Left controls: `+` attachment button (photos/videos with thumbnail preview tray) and styled `Gemini 3.8 Flash High ^` model dropdown.
     - Right controls: `🛡️ Turbo ^` thinking mode selector, microphone voice input icon, and circular solid blue `#0084ff` send button with white arrow `→`.
     - Added global clipboard image paste (`Ctrl+V`) and drag-and-drop file upload.
  3. **Text Selection & Immutability**:
     - Applied `user-select: text !important; cursor: text;` to all chat messages, thoughts, and logs for easy selection and copying.
     - Ensured content is 100% read-only (`contenteditable="false"`).
  4. **Clutter Removal**:
     - Permanently removed the `.controls` bar (Pause, Resume, Stop buttons).

---

### [2026-10-16] Feature 06: Handy Local Whisper 3 Turbo Integration & Voice-Driven Dispatch
* **Context**:
  User has Handy installed at `C:\Users\MSI\AppData\Local\Handy` containing local Whisper 3 Turbo (`ggml-large-v3-turbo.bin`, 1.62 GB) at `C:\Users\MSI\AppData\Roaming\com.pais.handy\models\ggml-large-v3-turbo.bin`.
  Requirement: dictate speech anywhere, text automatically populates the agent input box ("смари пишет"), and automatically sends the task when the user gives a voice trigger command (e.g. "... отправь", "погнали", "старт") without touching the keyboard.
* **Architecture**:
  1. **Dual-Pipeline Execution**:
     - **Native Handy Hotkey Path (`Alt+X`)**: Runs via Handy's optimized native AVX2 Rust binary (~4.8s). Handy records and appends to `history.db`.
     - **Background SQLite Monitor (`core/handy_listener.py`)**: `HandyWatcher` polls `history.db` in non-blocking read-only mode (`?mode=ro`) with 300ms intervals, detects new dictations, parses triggers, and broadcasts over WebSocket.
     - **Browser In-App Mic Path (`core/voice.py` + `/api/transcribe`)**: Clicking `#mic-btn` captures 16kHz mono audio via `MediaRecorder`, sends to `/api/transcribe`, resamples via `ffmpeg`, and transcribes directly using `pywhispercpp` loaded with Handy's `ggml-large-v3-turbo.bin`.
  2. **Voice Send Trigger Parsing (`SEND_TRIGGER_RE` / `VOICE_SEND_REGEX`)**:
     - Detects trigger words at end of speech: `отправь`, `отправить`, `отправляй`, `погнали`, `поехали`, `выполняй`, `выполни`, `сделай`, `делай`, `старт`, `пуск`, `давай`, `send`, `go`.
     - Strips trailing trigger word and preceding punctuation cleanly.
     - Sets `auto_send = True` when trigger is present, `False` for normal dictation.
  3. **UI Integration (`ui/app.py`)**:
     - Input listener intercepts Handy's direct `Ctrl+V` pastes and strips triggers.
     - WebSocket handler `voice_dictation` populates `#task-input` with glowing border pulse.
     - If `auto_send == True`, waits 350ms for visual confirmation then fires `startTask()`.

---

### [2026-10-16] Feature 07: ZennoLab hCaptcha Verification & Isolated Docker Sandbox / Tunnel
* **Context**:
  Tested captcha clicking on `https://lessons.zennolab.com/captchas/hcaptcha/?level=easy` and built an isolated Docker container sandbox with remote debugging tunnel and instant 1-click reset.
* **Verification on ZennoLab**:
  1. Ran [`test_zennolab.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/test_zennolab.py).
  2. Computer Vision locator ([`tools/captcha.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/tools/captcha.py)) found checkbox at `(864, 405)`.
  3. CDP DOM locator ([`tools/browser_cdp.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/tools/browser_cdp.py)) located `#checkbox` in `newassets.hcaptcha.com` iframe and clicked.
  4. Challenge popup successfully triggered (verified in [`screenshots/zennolab_after.png`](file:///c:/Users/MSI/Downloads/local-devin-agent/screenshots/zennolab_after.png)).
* **Docker Sandbox & Tunnel (`docker/`)**:
  - [`docker/Dockerfile`](file:///c:/Users/MSI/Downloads/local-devin-agent/docker/Dockerfile): Debian-based Chromium + Xvfb (1920x1080) + fluxbox + x11vnc + noVNC + socat.
  - [`docker/docker-compose.yml`](file:///c:/Users/MSI/Downloads/local-devin-agent/docker/docker-compose.yml): Exposes `127.0.0.1:9222` (CDP tunnel for agent) and `127.0.0.1:6080` (live noVNC web view).
  - [`docker/reset.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/docker/reset.py) & [`docker/reset.bat`](file:///c:/Users/MSI/Downloads/local-devin-agent/docker/reset.bat): Standalone 1-click reset that tears down containers, wipes ephemeral storage/cookies/fingerprints, recreates the container, and verifies CDP readiness. If Docker is not running, resets local sandbox profile.
  - [`docker/tunnel.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/docker/tunnel.py): Standalone tunnel utility for CDP health monitoring and remote SSH port-forwarding.

---

### [2026-10-16] Feature 08: Full Multi-Captcha Benchmark & Antigravity Design Overhaul
* **Captcha Benchmark Suite ([`test_suite_captchas.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/test_suite_captchas.py))**:
  Discovered and ran tests against real ZennoLab challenge pages:
  1. `hCaptcha Easy`: Clicked & challenge window opened.
  2. `hCaptcha Moderate`: Clicked & challenge window opened.
  3. `hCaptcha Difficult`: Clicked & challenge window opened.
  4. `reCAPTCHA v2 Low` (`recaptcha/v2_simple.php?level=low`): **100% green checkmark solved** (`screenshots/suite/recaptcha_v2_low_after.png`).
  5. `reCAPTCHA v2 Middle` (`recaptcha/v2_simple.php?level=middle`): Clicked & 3x3 challenge grid opened (`screenshots/suite/recaptcha_v2_middle_after.png`).
* **Design Overhaul in [`ui/app.py`](file:///c:/Users/MSI/Downloads/local-devin-agent/ui/app.py)**:
  1. **Top Header Quick Actions**:
     - `Solve Captcha` button with purple glow (manual one-click trigger).
     - `Reset Sandbox` button with cyan glow (instant container/profile wipe).
  2. **Sidebar Chat Search**:
     - Added instant search input filtering sessions in real-time.
  3. **Live Screen Feed Inspector & Fullscreen**:
     - Added real-time hover pixel coordinate badge (`X: 864, Y: 405`).
     - Click on screen preview automatically transfers coordinates to input.
     - Fullscreen pop-out toggle button for detailed agent monitoring.
  4. **Markdown & Trace Polish**:
     - One-click "Copy" button on all code blocks.
     - Action tags in Execution Trace color-coded: `CAPTCHA` (neon purple), `CLICK` (cyan), `TYPE` (emerald), `NAVIGATE` (blue), `BASH` (orange).
