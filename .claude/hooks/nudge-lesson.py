#!/usr/bin/env python3
"""UserPromptSubmit hook: nudges Claude to record a lesson after a likely correction.

Prints at most one short note. Never writes files, never blocks, exit 0 on any error.
"""
import os
import sys

sys.dont_write_bytecode = True  # no __pycache__: hooks never write files
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import lessons
except Exception:
    sys.exit(0)


def main():
    prompt = lessons.read_input().get("prompt")
    if isinstance(prompt, str):
        text = lessons.nudge_for(prompt)
        if text:
            lessons.emit("UserPromptSubmit", text)


lessons.run(main)
