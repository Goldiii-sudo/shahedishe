# Antigravity Agent

Autonomous desktop and browser AI agent built with native Windows Win32 integration, Edge WebView2, Computer Vision, and Gemini LLM.

---

## [QUICKSTART]

### 1. Requirements
* Windows 10 / 11 (x64)
* Python 3.10+
* Google Chrome or Edge
* Tesseract OCR (`C:\Program Files\Tesseract-OCR\tesseract.exe`)

### 2. Launching
Double-click `run_app.bat` or run:
```powershell
python main.py
```
To run in terminal CLI mode (without desktop GUI):
```powershell
python main.py --cli
```

### 3. Local LLM Gateway
The agent connects by default to the local Gemini Web2API proxy at `http://localhost:8083/v1` using cookie-based authentication.

---

## [SYSTEM ARCHITECTURE]

```
 local-devin-agent/
 ├── main.py                 # Primary entrypoint (launches native desktop window)
 ├── desktop_app.py          # Native Edge WebView2 window controller (1440x900)
 ├── run_app.bat             # One-click Windows batch launcher
 ├── cli.py                  # CLI fallback mode
 ├── config.py               # Global configurations & thresholds
 ├── core/
 │   ├── agent.py            # Autonomous ReAct agent loop & tool dispatcher
 │   ├── prompts.py          # Dynamic prompt builder & action protocol
 │   ├── llm.py              # OpenAI-compatible LLM client with vision support
 │   └── session_store.py    # Persistent chat history & settings manager
 ├── tools/
 │   ├── os_control.py       # Win32 GDI input, Bézier curve mouse generator
 │   ├── screen.py           # Win32 desktop capture, 100px grid ruler overlay
 │   ├── captcha.py          # OpenCV & contour-based captcha checkbox locator
 │   ├── ui_finder.py        # Windows UI Automation (UIA) + OCR hybrid locator
 │   ├── browser_cdp.py      # Chrome DevTools Protocol / Playwright controller
 │   ├── bash_tool.py        # Windows PowerShell / CMD runner
 │   └── file_tools.py       # Local file reading & writing utilities
 ├── ui/
 │   ├── app.py              # FastAPI internal IPC backend & dashboard HTML
 │   └── overlay.py          # Windows transparent always-on-top HUD overlay
 ├── prompts/
 │   └── custom_prompt.md    # Custom persona & jailbreak injections (auto-loaded)
 └── data/
     ├── sessions/           # JSON files with saved chats & execution histories
     └── settings.json       # Persisted user preferences
```

---

## [KEY CAPABILITIES]

1. **Native Desktop UI (Antigravity IDE Theme)**
   - Minimalist deep-space dark theme (`#090d16`).
   - Zero emojis across the entire UI and codebase; clean vector SVG icons.
   - 3-column layout: Projects & Sessions sidebar | Chat, Thoughts & Actions | Live 1920x1080 Screen Stream with remote AnyDesk-style cursor.

2. **Sub-Pixel Click Accuracy & Anti-Bot Mouse Physics**
   - **Cubic Bézier Trajectories**: Cursor moves via smooth Bézier curves with cosine ease-in/ease-out and micro-jitter, completely bypassing heuristic bot detectors.
   - **100px Grid Overlay**: Screenshots sent to vision models include subtle guide rulers and intersection coordinates (e.g. `800,400`, `1000,500`).
   - **Live User Mouse Tracking**: Detects when the human user physically points at an element and enables instant clicking via `click_user_cursor`.

3. **Hybrid Captcha Solver (`click_captcha`)**
   - **Level 1 (DOM / CDP)**: Scans browser frames (`page.frames()`), locates `#checkbox` inside iframes, and clicks directly.
   - **Level 2 (Computer Vision)**: Detects hCaptcha, Google reCAPTCHA, and Cloudflare Turnstile on any desktop window via HSV color masking and contour geometry.

4. **Persistence & Jailbreak Support**
   - Sessions grouped by project directory with relative timestamps (`30m`, `2h`, `5d`, `5mo`).
   - Custom prompts from `prompts/*.md` automatically injected on the fly.
   - Enforced `LANGUAGE_RULE` guarantees model speaks the exact language of the user.
