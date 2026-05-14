"""Detect missing pieces for Juno AI and suggest exact terminal commands (stdlib only)."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

JUNO_ROOT = Path(__file__).resolve().parent
REQUIREMENTS_FILE = JUNO_ROOT / "requirements.txt"


@dataclass(frozen=True)
class SetupIssue:
    """One problem (or informational note) the user can fix in the terminal."""

    severity: str  # "error" | "warning" | "info"
    title: str
    detail: str
    copy_commands: tuple[str, ...] = ()


def venv_python_executable() -> Path | None:
    """Return the venv interpreter path if a project .venv exists."""
    candidates = (
        JUNO_ROOT / ".venv" / "bin" / "python",
        JUNO_ROOT / ".venv" / "Scripts" / "python.exe",
    )
    for p in candidates:
        if p.is_file():
            return p
    return None


def running_inside_venv() -> bool:
    return getattr(sys, "base_prefix", sys.prefix) != sys.prefix


def _apt_python_bootstrap() -> tuple[str, ...]:
    return (
        "sudo apt update",
        "sudo apt install -y python3 python3-venv python3-pip",
    )


def _install_project_commands() -> tuple[str, ...]:
    """Commands that work on Linux Mint / Debian-style systems from the Juno folder."""
    root = str(JUNO_ROOT)
    return (
        f"cd {root}",
        "chmod +x install-linux.sh juno-ai.sh build-deb.sh",
        "./install-linux.sh",
    )


def analyze_installation() -> list[SetupIssue]:
    """
    Return actionable issues (may be empty). Safe to call after Juno already starts:
    it also verifies the optional .venv can import dependencies.
    """
    issues: list[SetupIssue] = []

    if sys.version_info < (3, 10):
        issues.append(
            SetupIssue(
                "error",
                "Python is older than 3.10",
                f"This process is Python {sys.version_info.major}.{sys.version_info.minor}. "
                "Juno targets 3.10+ (what Linux Mint currently ships).",
                _apt_python_bootstrap(),
            )
        )

    if not REQUIREMENTS_FILE.is_file():
        issues.append(
            SetupIssue(
                "warning",
                "requirements.txt not beside Juno",
                f"Expected file missing: {REQUIREMENTS_FILE}. "
                "Re-copy the whole juno-ai folder from your archive or git checkout.",
                (),
            )
        )

    cfg_home = Path.home() / ".config" / "juno-ai"
    try:
        cfg_home.mkdir(parents=True, exist_ok=True)
        probe = cfg_home / ".juno_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError as exc:
        issues.append(
            SetupIssue(
                "error",
                "Cannot write the config folder",
                f"Juno needs to create `{cfg_home}`.\nReason: {exc}",
                (
                    f"mkdir -p {cfg_home}",
                    f"chmod u+rwx {cfg_home}",
                ),
            )
        )

    venv_py = venv_python_executable()
    if venv_py is not None:
        try:
            proc = subprocess.run(
                [str(venv_py), "-c", "import PyQt6.QtCore; import openai"],
                cwd=str(JUNO_ROOT),
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            issues.append(
                SetupIssue(
                    "error",
                    "Could not run the virtual environment Python",
                    str(exc),
                    _install_project_commands(),
                )
            )
        else:
            if proc.returncode != 0:
                err = (proc.stderr or proc.stdout or "").strip() or "Unknown import error"
                issues.append(
                    SetupIssue(
                        "error",
                        "Virtual environment is incomplete",
                        "The `.venv` folder exists but PyQt6 or openai failed to import.\n" + err[:800],
                        _install_project_commands(),
                    )
                )
    elif not running_inside_venv():
        issues.append(
            SetupIssue(
                "warning",
                "Recommended: create the project virtual environment",
                "You are not using `.venv` next to Juno. That is fine if you installed "
                "PyQt6 and openai yourself, but the supported install path uses `./install-linux.sh`.",
                _install_project_commands(),
            )
        )

    if not issues:
        issues.append(
            SetupIssue(
                "info",
                "Core checks passed",
                "Python version, config folder, and dependencies look usable from Juno's point of view.",
                (),
            )
        )

    return issues
