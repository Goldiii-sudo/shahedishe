"""
CLI Mode for Local Devin Agent.
Run the autonomous agent directly from your terminal/command line:
No browser or web dashboard needed.
"""
import asyncio
import sys
import argparse

# Ensure proper Unicode / emoji output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from core.agent import Agent, AgentState

def cli_callback(data: dict):
    mtype = data.get("type")
    if mtype == "state":
        print(f"\n[STATE] -> {data.get('state').upper()}")
        if data.get("result"):
            print(f"[RESULT] {data.get('result')}")
    elif mtype == "step":
        s = data.get("step", {})
        print(f"\n{'='*60}")
        print(f"STEP {s.get('index')}")
        print(f"[OBSERVE] {s.get('observation')}")
        print(f"[THOUGHT] {s.get('thought')}")
        print(f"[ACTION]  {s.get('action')}")
    elif mtype == "result":
        print(f"↳ OUTCOME:     {data.get('result')}")
    elif mtype == "human_needed":
        print(f"\n[HUMAN-IN-THE-LOOP REQUIRED]: {data.get('question')}")

async def main():
    parser = argparse.ArgumentParser(description="Antigravity Autonomous CLI")
    parser.add_argument("task", nargs="*", help="Task for the agent to execute")
    args = parser.parse_args()

    task_str = " ".join(args.task).strip()
    if not task_str:
        print("Antigravity Autonomous Agent (CLI Mode)")
        print("Type your goal / task below (or Ctrl+C to quit):\n")
        try:
            task_str = input("Goal > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            return

    if not task_str:
        print("Empty task. Bye.")
        return

    agent = Agent(on_update=cli_callback)
    print(f"\n[STARTING AGENT TASK]: {task_str}\n")
    try:
        final_result = await agent.run(task_str)
        print(f"\n{'='*60}")
        print(f"[FINAL OUTCOME]: {final_result}")
    except KeyboardInterrupt:
        print("\nStopping agent...")
        agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
