"""
Validation tests for Claude Code event hooks in the 10X Developer Unicorn plugin.

Tests ensure:
- hooks/hooks.json exists and is valid
- Hook events reference valid Claude Code lifecycle events
- Git hooks preserved as scripts for developer tooling
"""

import json
import subprocess
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parent.parent
HOOKS_DIR = PROJECT_ROOT / "hooks"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Valid Claude Code hook events
VALID_HOOK_EVENTS = {
    "SessionStart",
    "PreToolUse",
    "PostToolUse",
    "Notification",
    "Stop",
}


def test_hooks_directory_exists():
    """The hooks directory must exist."""
    assert HOOKS_DIR.exists(), (
        f"Hooks directory not found at {HOOKS_DIR}. "
        f"Create the directory structure first."
    )


def test_hooks_json_exists():
    """hooks/hooks.json must exist for Claude Code plugin."""
    hooks_json = HOOKS_DIR / "hooks.json"
    assert hooks_json.exists(), (
        f"hooks.json must exist at {hooks_json.relative_to(PROJECT_ROOT)}"
    )


def test_hooks_json_valid_json():
    """hooks/hooks.json must be valid JSON."""
    hooks_json = HOOKS_DIR / "hooks.json"

    if not hooks_json.exists():
        pytest.skip("hooks.json not created yet")

    try:
        data = json.loads(hooks_json.read_text(encoding="utf-8"))
        assert isinstance(data, dict), "hooks.json must be a JSON object"
    except json.JSONDecodeError as e:
        pytest.fail(f"hooks.json is not valid JSON: {e}")


def test_hooks_json_has_hooks_key():
    """hooks.json must have a top-level 'hooks' key."""
    hooks_json = HOOKS_DIR / "hooks.json"

    if not hooks_json.exists():
        pytest.skip("hooks.json not created yet")

    data = json.loads(hooks_json.read_text(encoding="utf-8"))
    assert "hooks" in data, "hooks.json must have a 'hooks' key"


def test_hooks_json_references_valid_events():
    """All hook events in hooks.json must be valid Claude Code lifecycle events."""
    hooks_json = HOOKS_DIR / "hooks.json"

    if not hooks_json.exists():
        pytest.skip("hooks.json not created yet")

    data = json.loads(hooks_json.read_text(encoding="utf-8"))
    hooks = data.get("hooks", {})

    for event_name in hooks:
        assert event_name in VALID_HOOK_EVENTS, (
            f"Unknown hook event '{event_name}' in hooks.json. "
            f"Valid events: {', '.join(sorted(VALID_HOOK_EVENTS))}"
        )


def test_platform_context_hook_outputs_valid_json_or_exits_cleanly():
    """platform-context.sh must output valid JSON or exit 0 with no output."""
    script = SCRIPTS_DIR / "platform-context.sh"

    if not script.exists():
        pytest.skip("platform-context.sh not created yet")

    result = subprocess.run(
        [str(script)],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(PROJECT_ROOT),
    )

    assert result.returncode == 0, (
        f"platform-context.sh exited with code {result.returncode}. "
        f"stderr: {result.stderr}"
    )

    stdout = result.stdout.strip()
    if not stdout:
        return

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as e:
        pytest.fail(
            f"platform-context.sh produced non-JSON output: {e}\n"
            f"Output was: {stdout[:500]}"
        )

    assert "continue" in data, "Hook output must have 'continue' field"
    assert data["continue"] is True, "Hook 'continue' must be true"
    assert "hookSpecificOutput" in data, "Hook output must have 'hookSpecificOutput'"

    hook_output = data["hookSpecificOutput"]
    assert hook_output.get("hookEventName") == "SessionStart", (
        "hookEventName must be 'SessionStart'"
    )
    assert "additionalContext" in hook_output, (
        "hookSpecificOutput must have 'additionalContext'"
    )
    assert isinstance(hook_output["additionalContext"], str), (
        "additionalContext must be a string"
    )


def test_git_hooks_preserved_as_scripts():
    """Git hooks should be preserved as scripts for developer tooling."""
    git_pre_commit = SCRIPTS_DIR / "git-pre-commit"
    git_pre_push = SCRIPTS_DIR / "git-pre-push"

    assert git_pre_commit.exists(), (
        "git-pre-commit should be preserved at scripts/git-pre-commit"
    )
    assert git_pre_push.exists(), (
        "git-pre-push should be preserved at scripts/git-pre-push"
    )
