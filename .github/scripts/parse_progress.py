import json
import re
from pathlib import Path

SOURCE = Path("progress/latest-release.md")
OUTPUT = Path(".github/release-progress.json")

def extract_mod_list_table(md: str) -> list[list[str]]:
    lines = md.splitlines()

    # Find "### Mod List"
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "### Mod List")
    except StopIteration:
        raise RuntimeError("Could not find '### Mod List' header")

    # Find table start (first pipe row after header)
    table = []
    for line in lines[start + 1:]:
        if not line.strip():
            if table:
                break
            continue
        if line.strip().startswith("|"):
            table.append(line)
        elif table:
            break

    if len(table) < 3:
        raise RuntimeError("Mod List table not found or incomplete")

    # Skip header + separator
    data_rows = table[2:]

    parsed = []
    for row in data_rows:
        cols = [c.strip() for c in row.strip("|").split("|")]
        if len(cols) < 3:
            continue
        parsed.append(cols)

    return parsed

md = SOURCE.read_text(encoding="utf-8")
rows = extract_mod_list_table(md)

STAR = "⭐"
CHECK = "✅"

total_starred = 0
completed_starred = 0

for mod, status, priority, *_ in rows:
    if STAR in priority:
        total_starred += 1
        if CHECK in status:
            completed_starred += 1

percent = 0
if total_starred:
    percent = round((completed_starred / total_starred) * 100)
    
#Color selection    
if percent < 25:
    color = "#e05d44"        # red
elif percent < 41:
    color = "#fe7d37"        # dark orange
elif percent < 70:
    color = "#dfb317"        # orange
elif percent < 90:
    color = "#b4c63b"        # yellow-green
else:
    color = "#4cbb17"        # bright green

#Debug timestamp
from datetime import datetime
ts = datetime.utcnow().strftime("%H:%M UTC")

badge = {
    "schemaVersion": 1,
    "label": "1.21.11 Release Progress",
    "message": f"{completed_starred}/{total_starred} ({percent}%)",
    "color": color  # Selection from above
}

OUTPUT.write_text(json.dumps(badge, indent=2), encoding="utf-8")
print(f"Computed {completed_starred}/{total_starred} = {percent}%")
