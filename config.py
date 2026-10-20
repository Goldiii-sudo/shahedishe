"""
Centralized configuration — loads from .env, provides typed defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Tesseract OCR path ───────────────────────────────────────────────────
TESSERACT_CMD: str = os.getenv(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# ── LLM ──────────────────────────────────────────────────────────────────
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "nvidia")
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://integrate.api.nvidia.com/v1")
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "z-ai/glm-5.3")
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))

# Vision model — used for screenshot analysis when main model is text-only
VISION_MODEL: str = os.getenv("VISION_MODEL", "meta/llama-3.2-90b-vision-instruct")
VISION_BASE_URL: str = os.getenv("VISION_BASE_URL", "")    # empty = same as LLM_BASE_URL
VISION_API_KEY: str = os.getenv("VISION_API_KEY", "")      # empty = same as LLM_API_KEY

# ── Screen capture ───────────────────────────────────────────────────────
SCREEN_WIDTH: int = int(os.getenv("SCREEN_WIDTH", "1920"))
SCREEN_HEIGHT: int = int(os.getenv("SCREEN_HEIGHT", "1080"))
SCREENSHOT_MAX_WIDTH: int = int(os.getenv("SCREENSHOT_MAX_WIDTH", "1344"))
SCREENSHOT_MAX_HEIGHT: int = int(os.getenv("SCREENSHOT_MAX_HEIGHT", "756"))
GRID_ENABLED: bool = os.getenv("GRID_ENABLED", "true").lower() == "true"
GRID_STEP: int = int(os.getenv("GRID_STEP", "100"))

# ── Browser CDP ──────────────────────────────────────────────────────────
BROWSER_CDP_URL: str = os.getenv("BROWSER_CDP_URL", "http://127.0.0.1:9222")

# ── Agent behaviour ─────────────────────────────────────────────────────
AGENT_MAX_STEPS: int = int(os.getenv("AGENT_MAX_STEPS", "50"))
AGENT_STEP_DELAY: float = float(os.getenv("AGENT_STEP_DELAY", "0.2"))

# ── Web UI ───────────────────────────────────────────────────────────────
WEB_HOST: str = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT: int = int(os.getenv("WEB_PORT", "7860"))

# ── Paths ────────────────────────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).resolve().parent
SCREENSHOTS_DIR: Path = BASE_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Scale factors for mapping model coordinates → real screen
SCALE_X: float = SCREEN_WIDTH / SCREENSHOT_MAX_WIDTH
SCALE_Y: float = SCREEN_HEIGHT / SCREENSHOT_MAX_HEIGHT
