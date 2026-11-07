"""Validate installation from a temporary local Git checkout without changing the user's repo.

Only explicitly inventoried source files are copied. Local .env files, dependencies, build
outputs, and user data are excluded. The temporary checkout is retained under ignored tmp/.
"""

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def isolated_environment() -> dict[str, str]:
    # VS Code/Git hooks may export a different worktree or index; cwd does not override it.
    return {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}


def root_git_state() -> dict[str, object] | None:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--absolute-git-dir"],
        env=isolated_environment(),
        capture_output=True,
        check=False,
    )
    if result.returncode:
        return None
    directory = Path(result.stdout.decode().strip())
    head = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--verify", "HEAD"],
        env=isolated_environment(),
        capture_output=True,
        check=False,
    )
    index = directory / "index"
    return {
        "directory": str(directory),
        "head": head.stdout.decode().strip(),
        "index_sha256": hashlib.sha256(index.read_bytes()).hexdigest() if index.exists() else None,
    }


def run(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        env=isolated_environment(),
        check=False,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )
    print(result.stdout, end="", flush=True)
    result.check_returncode()
    return result.stdout.strip()


def main() -> None:
    original_repository = root_git_state()
    manifest = json.loads(
        (ROOT / "docs/evidence/phase-01/artifact-manifest.json").read_text(encoding="utf-8")
    )
    paths = set(manifest["code_files"])
    paths.update(
        {
            "README.md",
            "AGENTS.md",
            "scripts/diagnose_runtime.py",
            "scripts/verify_development.py",
            "scripts/verify_clean_checkout.py",
            "tests/unit/test_verification_environment.py",
        }
    )
    destination = ROOT / "tmp" / f"foundation-checkout-{uuid4().hex[:10]}"
    if not destination.resolve().is_relative_to(ROOT.resolve()):
        raise RuntimeError("Temporary checkout must stay inside the workspace")
    source, checkout, hooks = [destination / name for name in ["source", "checkout", "hooks"]]
    hooks.mkdir(parents=True)
    digests = {}
    for name in sorted(paths):
        path = ROOT / name
        if not path.resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError("Source path escapes workspace")
        if path.name.startswith(".env") and path.name != ".env.example":
            raise RuntimeError("Local secrets cannot enter a checkout fixture")
        target = source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        digests[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    # Do not let a user's global Windows autocrlf rewrite the test snapshot's bytes.
    git = [
        "git",
        "-c",
        f"core.hooksPath={hooks.as_posix()}",
        "-c",
        "commit.gpgsign=false",
        "-c",
        "core.autocrlf=false",
    ]
    run(
        [*git, "-c", f"init.templateDir={hooks.as_posix()}", "init", "-b", "foundation-test"],
        source,
    )
    run([*git, "add", "--force", "."], source)
    run(
        [
            *git,
            "-c",
            "user.name=Foundation validation",
            "-c",
            "user.email=validation@example.invalid",
            "commit",
            "-m",
            "Snapshot foundation source for clean-checkout verification",
        ],
        source,
    )
    commit = run([*git, "rev-parse", "HEAD"], source)
    run([*git, "clone", "--no-local", str(source), str(checkout)], destination)
    mismatches = [
        name
        for name, value in digests.items()
        if hashlib.sha256((checkout / name).read_bytes()).hexdigest() != value
    ]
    assert not mismatches, f"Checkout changed source bytes: {mismatches}"
    uv = ROOT / ".venv/Scripts/uv.exe"
    pnpm = ROOT / ".tools/node_modules/pnpm/pnpm.exe"
    os.environ["API_ORIGIN"] = "http://127.0.0.1:8000"
    run([str(uv), "sync", "--project", "apps/api", "--frozen", "--offline"], checkout)
    run([str(pnpm), "install", "--frozen-lockfile", "--offline"], checkout)
    python = checkout / "apps/api/.venv/Scripts/python.exe"
    # The sandbox and host use different Windows accounts. Never reuse a temp root
    # previously created by the other identity, or change its ACL to hide a failure.
    pytest_temp = destination / "pytest-tmp"
    assert not pytest_temp.exists(), "Checkout fixture must use a fresh pytest directory"
    run(
        [
            str(python),
            "-m",
            "pytest",
            "-c",
            "apps/api/pyproject.toml",
            "tests/unit",
            "tests/smoke",
            "-q",
            f"--basetemp={pytest_temp}",
        ],
        checkout,
    )
    run([str(pnpm), "typecheck"], checkout)
    run([str(pnpm), "test"], checkout)
    assert root_git_state() == original_repository, "Original repository HEAD/index changed"
    print(
        json.dumps(
            {
                "event": "clean_checkout_verified",
                "temporary_test_commit": commit,
                "source_sha256": hashlib.sha256(
                    json.dumps(digests, sort_keys=True).encode()
                ).hexdigest(),
                "checkout": checkout.relative_to(ROOT).as_posix(),
                "root_repository_modified": False,
                "files_verified": len(digests),
            }
        )
    )


if __name__ == "__main__":
    main()
