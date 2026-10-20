"""
Native Windows Desktop Application for Local Devin Agent.
Launches the FastAPI backend in a background daemon thread,
then pops up a sleek native desktop window (WebKit/Edge WebView2).
No browser tabs needed.
"""
import sys
import threading
import time
import uvicorn
import webview

import config
from ui.app import app

import socket
import urllib.request

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def find_free_port(start_port: int = 7860) -> int:
    port = start_port
    while is_port_in_use(port):
        # test if it's already our agent backend running
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/status", timeout=0.5) as r:
                if r.status == 200:
                    return port # already running!
        except Exception:
            pass
        port += 1
    return port

def main():
    # 0. Start Always-On-Top HUD Overlay
    from ui.overlay import start_overlay_thread
    start_overlay_thread()

    target_port = find_free_port(config.WEB_PORT)
    config.WEB_PORT = target_port

    # If backend is not already running on target_port, start it
    if not is_port_in_use(target_port):
        def start_backend():
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=target_port,
                log_level="warning",
                ws_ping_interval=None,
                ws_ping_timeout=None,
            )
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        time.sleep(1.2)

    url = f"http://127.0.0.1:{target_port}"
    
    window = webview.create_window(
        title="Antigravity Agent",
        url=url,
        width=1440,
        height=900,
        resizable=True,
        min_size=(960, 600),
        background_color="#090d16",
    )

    # 4. Start native event loop (blocks until window is closed)
    webview.start(debug=False)
    sys.exit(0)

if __name__ == "__main__":
    main()
