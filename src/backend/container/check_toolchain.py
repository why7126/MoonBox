"""Offline executor tool inventory; safe output contains only fixed tool names."""
import json
import os
import shutil
import subprocess


TOOLS = {
    "python": ["--version"], "git": ["--version"], "bash": ["--version"],
    "rg": ["--version"], "node": ["--version"], "npm": ["--version"],
    "pnpm": ["--version"], "openspec": ["--version"], "uv": ["--version"],
    "curl": ["--version"], "jq": ["--version"], "patch": ["--version"],
    "unzip": ["-v"], "zip": ["-v"],
}
PINNED = {"node": "v22.22.0", "openspec": "1.3.1", "pnpm": "11.2.2", "uv": "uv 0.8.15"}


def check_tools():
    failures = []
    env = {**os.environ, "HOME": "/tmp", "XDG_CONFIG_HOME": "/tmp/config",
           "XDG_CACHE_HOME": "/tmp/cache", "OPENSPEC_TELEMETRY": "0", "DO_NOT_TRACK": "1"}
    for name, args in TOOLS.items():
        executable = shutil.which(name)
        if not executable:
            failures.append(name)
            continue
        try:
            # Node package CLIs can take longer on a cold, CPU-limited executor
            # while still returning the pinned version. Keep OS probes fail-fast.
            timeout = 120 if name in {"npm", "pnpm", "openspec"} else 10
            result = subprocess.run([executable, *args], capture_output=True,
                                    text=True, timeout=timeout, env=env)
            version = result.stdout.strip().splitlines()
            if result.returncode or (name in PINNED and (not version or version[0] != PINNED[name])):
                failures.append(name)
        except (OSError, subprocess.TimeoutExpired):
            failures.append(name)
    return {"ready": not failures, "unavailable": failures}


if __name__ == "__main__":
    report = check_tools()
    print(json.dumps(report))
    raise SystemExit(0 if report["ready"] else 1)
