#!/usr/bin/env python3
"""SessionStart hook: one line on the lessons file (count, stale, over the cap).

Silent when there are no lessons. Never writes files, exit 0 on any error.
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
    try:
        data = lessons.read_input()
    except Exception:
        data = {}
    text = lessons.status(lessons.project_dir(data))
    if text:
        lessons.emit("SessionStart", text)


lessons.run(main)
