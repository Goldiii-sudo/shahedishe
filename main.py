"""
Antigravity Agent - Native Desktop Application.
Runs the autonomous agent in a high-performance native desktop window (WebView2).
"""
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Antigravity Agent - Native Desktop Application")
    parser.add_argument("--cli", action="store_true", help="Run in command line interface mode instead of desktop window")
    parser.add_argument("task", nargs="*", help="Optional task to execute immediately (CLI mode)")
    args, unknown = parser.parse_known_args()

    if args.cli:
        import asyncio
        from cli import main as cli_main
        asyncio.run(cli_main())
    else:
        from desktop_app import main as desktop_main
        desktop_main()

if __name__ == "__main__":
    main()
