"""Record actual command results; do not pass secrets on the command line."""

import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

label, *command = sys.argv[1:]
if command and command[0] == "--":
    command.pop(0)
if not re.fullmatch(r"[a-z0-9_-]+", label) or not command:
    raise SystemExit("Usage: record_check.py label -- command [args]")
root = Path(__file__).resolve().parents[1]
started = datetime.now(UTC).isoformat()
try:
    result = subprocess.run(command, cwd=root, capture_output=True, check=False)
    output = result.stdout.decode("utf-8", errors="replace") + result.stderr.decode(
        "utf-8", errors="replace"
    )
    code = result.returncode
except FileNotFoundError:
    output, code = "Required executable not found", 127
folder = root / "docs/evidence/phase-01"
folder.mkdir(parents=True, exist_ok=True)
(folder / f"{label}.txt").write_text(output, encoding="utf-8")
record = {
    "command": subprocess.list2cmdline(command),
    "exit_code": code,
    "time": started,
    "environment": (
        f"{platform.system()} {platform.release()}; runner Python {platform.python_version()}"
    ),
    "commit": None,
    "artifact": f"docs/evidence/phase-01/{label}.txt",
    "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
}
(folder / f"{label}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record, indent=2))
sys.exit(code)
