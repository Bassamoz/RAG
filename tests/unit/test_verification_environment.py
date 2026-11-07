"""A verification checkout must not follow a caller's repository-selection environment."""

import importlib.util
import os
import subprocess
from pathlib import Path


def test_checkout_commands_ignore_inherited_git_repository(monkeypatch, tmp_path):
    path = Path(__file__).resolve().parents[2] / "scripts/verify_clean_checkout.py"
    spec = importlib.util.spec_from_file_location("verify_clean_checkout", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    intended, unrelated = [tmp_path / name for name in ["intended", "unrelated"]]
    for repository in [intended, unrelated]:
        subprocess.run(["git", "init", str(repository)], env=env, check=True, capture_output=True)
    monkeypatch.setenv("GIT_DIR", str(unrelated / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(unrelated))
    monkeypatch.setenv("GIT_INDEX_FILE", str(unrelated / "foreign-index"))
    actual = module.run(["git", "rev-parse", "--absolute-git-dir"], intended)
    assert Path(actual).resolve() == (intended / ".git").resolve()
    assert not (unrelated / "foreign-index").exists()
