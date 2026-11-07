"""Read-only comparison of Codex and terminal access to Docker/WSL; never reads credentials."""

import json
import os
import platform
import shutil
import struct
import subprocess
import sys


def decode_output(value: bytes) -> str:
    # WSL writes UTF-16LE to redirected Windows handles; Docker uses UTF-8.
    encoding = "utf-16-le" if value.count(b"\0") > len(value) // 4 else "utf-8"
    return value.decode(encoding, errors="replace").strip()


def probe(command: list[str]) -> dict[str, object]:
    executable = shutil.which(command[0])
    if not executable:
        return {"command": command, "exit_code": 127, "error": "Executable not on process PATH"}
    try:
        result = subprocess.run(
            [executable, *command[1:]], capture_output=True, check=False, timeout=30
        )
        return {
            "command": command,
            "exit_code": result.returncode,
            "stdout": decode_output(result.stdout),
            "stderr": decode_output(result.stderr),
        }
    except subprocess.TimeoutExpired:
        return {"command": command, "exit_code": 124, "error": "Probe timed out after 30 seconds"}


checks = [
    probe(["docker", "version"]),
    probe(["docker", "compose", "version"]),
    probe(["docker", "context", "show"]),
    probe(["docker", "info", "--format", "{{.ServerVersion}} {{.OSType}}"]),
    probe(["wsl", "--list", "--verbose"]),
    probe(["whoami"]),
]
ready = all(checks[index]["exit_code"] == 0 for index in [0, 1, 3])
print(
    json.dumps(
        {
            "execution_environment": {
                "os": platform.system(),
                "python_bits": struct.calcsize("P") * 8,
                "wsl_process": bool(os.environ.get("WSL_DISTRO_NAME")),
                "docker_executable": shutil.which("docker"),
                "docker_host_override_present": bool(os.environ.get("DOCKER_HOST")),
                "docker_context_override_present": bool(os.environ.get("DOCKER_CONTEXT")),
            },
            "checks": checks,
            "engine_and_compose_accessible": ready,
        },
        indent=2,
    )
)
sys.exit(0 if ready else 1)
