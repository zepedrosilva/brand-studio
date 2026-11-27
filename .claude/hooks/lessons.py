"""Shared helper for the lesson hooks. Python 3 standard library only.

Every hook calls run(main): any error ends silently with exit 0, so a hook never
blocks a prompt or a session start. Hooks only read files; they never write.
"""
import datetime
import json
import os
import re
import sys

# Thresholds, in one place. scripts/check-repo-docs.sh uses the same numbers.
MAX_CONTEXT_CHARS = 300  # assumption: a short nudge (the platform cap is 10,000)
MAX_LESSONS = 15  # assumption
STALE_DAYS = 90  # assumption

# English only; the `lesson:` prefix works in any language. Only phrases aimed at Claude's previous
# action; broad words (wrong, no, why did you, we always) fire on ordinary prompts and are left out.
MARKER = re.compile(r"^\s*lesson:", re.I)
_Q = "['’]?"  # straight or curly apostrophe, or none
CORRECTION = re.compile(
    r"^\s*again\s*,"
    r"|(^|\W)("
    r"no,?\s+(don" + _Q + r"t|do not|not that)\b"
    r"|that" + _Q + r"s\s+(wrong|not right|incorrect)\b"
    r"|that is\s+(wrong|not right|incorrect)\b"
    r"|not what i\s+(asked|wanted|meant)\b"
    r"|you should have\b"
    r"|i\s+(already\s+)?told you\b"
    r"|stop doing\b"
    r"|wrong\s+(file|folder|directory|branch|command|function|place|one)\b"
    r"|(don" + _Q + r"t|do not)\b.{0,60}\bagain\b"
    r"|you (forgot|missed|broke)\b"
    r")",
    re.I,
)
LESSON = re.compile(r"^- (\d{4}-\d{2}-\d{2}) · ")

MARKER_TEXT = (
    "The user marked a lesson. Paraphrase it as one rule and run the "
    "record-lesson skill. Never copy the prompt text into a file."
)
CORRECTION_TEXT = (
    "This prompt may correct you. If it does and would apply again in this "
    "repo, run the record-lesson skill with a paraphrased rule. If not, "
    "ignore this note."
)


def nudge_for(prompt):
    if MARKER.search(prompt):
        return MARKER_TEXT
    if CORRECTION.search(prompt):
        return CORRECTION_TEXT
    return ""


def project_dir(data):
    root = os.environ.get("CLAUDE_PROJECT_DIR")
    if not root and isinstance(data, dict) and isinstance(data.get("cwd"), str):
        root = data["cwd"]
    return root or os.getcwd()


def status(root):
    with open(os.path.join(root, "docs", "lessons.md"), encoding="utf-8") as f:
        text = re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)
    dates = [m.group(1) for m in map(LESSON.match, text.splitlines()) if m]
    if not dates:
        return ""
    today = datetime.date.today()
    stale = 0
    for d in dates:
        try:
            if (today - datetime.date.fromisoformat(d)).days > STALE_DAYS:
                stale += 1
        except ValueError:
            pass
    msg = "docs/lessons.md has %d lesson(s), cap %d" % (len(dates), MAX_LESSONS)
    if stale:
        msg += "; %d older than %d days" % (stale, STALE_DAYS)
    if len(dates) > MAX_LESSONS:
        msg += "; over the cap"
    if stale or len(dates) > MAX_LESSONS:
        return msg + ". Suggest running the tidy-docs skill."
    return msg + "."


def emit(event, text):
    out = {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text[:MAX_CONTEXT_CHARS]}}
    sys.stdout.write(json.dumps(out, separators=(",", ":")) + "\n")


def read_input():
    return json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))


def run(main):
    try:
        main()
    except BaseException:
        pass
    sys.exit(0)
