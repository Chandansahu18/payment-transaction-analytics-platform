from __future__ import annotations
import logging
import os
import shutil
import subprocess
from pathlib import Path
from prefect import task
from orchestration.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


def _subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    if os.name == "nt":
        env.setdefault("PYTHONUTF8", "1")
        env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def _windows_git_make_paths() -> list[Path]:
    roots: list[Path] = []
    for key in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        if value := os.environ.get(key):
            roots.append(Path(value))

    candidates: list[Path] = []
    for root in roots:
        candidates.append(root / "Git" / "usr" / "bin" / "make.exe")
        candidates.append(root / "Programs" / "Git" / "usr" / "bin" / "make.exe")
    return candidates


def _resolve_make() -> list[str]:
    if override := os.environ.get("MAKE"):
        return [override]

    if make_exe := shutil.which("make"):
        return [make_exe]

    if os.name == "nt":
        for candidate in _windows_git_make_paths():
            if candidate.exists():
                logger.info("Using make from Git install: %s", candidate)
                return [str(candidate)]
        raise RuntimeError(
            "make not found on Windows. Install Git for Windows (add to PATH), "
            "or set MAKE to the full path of make.exe in your environment."
        )

    return ["make"]


@task(name="run-make", retries=1, retry_delay_seconds=30, log_prints=True)
def run_make(target: str, description: str | None = None) -> None:
    label = description or f"make {target}"
    command = [*(_resolve_make()), target]

    logger.info("Running: %s", " ".join(command))

    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=_subprocess_env(),
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.stdout:
        logger.info(completed.stdout.rstrip())
    if completed.stderr:
        logger.warning(completed.stderr.rstrip())

    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "no output"
        raise RuntimeError(f"{label} failed (exit {completed.returncode}): {detail}")