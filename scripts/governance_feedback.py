#!/usr/bin/env python3
"""治理量化闭环 CLI；仅保存派生事实，不执行优化补丁或原始会话代码。"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "rules/governance-feedback-policy.json"
GROUP = ("command", "task_class", "model", "environment", "validation_profile", "workload_key")
TOKEN_FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def number(value, *, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError("invalid-nonnegative-number")
    if integer and int(value) != value:
        raise ValueError("invalid-counter")
    return int(value) if integer else float(value)


def identifier(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,127}", value):
        raise ValueError("invalid-identifier")
    return value


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def relative_file(root: Path, name: str) -> Path:
    p = Path(name)
    if p.is_absolute() or ".." in p.parts or "\\" in name or not re.fullmatch(r"[A-Za-z0-9_./-]+", name):
        raise ValueError("unsafe-relative-path")
    resolved = (root / p).resolve()
    if not resolved.is_relative_to(root.resolve()) or any(part.startswith(".env") or part == ".git" for part in p.parts):
        raise ValueError("unsafe-relative-path")
    return resolved


def file_hash(root: Path, name: str) -> str:
    p = relative_file(root, name)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "absent"


def policy_load(path: Path = POLICY) -> dict:
    p = json.loads(path.read_text())
    if p.get("schema_version") != 1 or not isinstance(p.get("enabled"), bool):
        raise ValueError("invalid-policy")
    for field in ("max_optimization_seconds", "max_optimization_tokens", "min_samples",
                  "regression_ratio", "slow_run_seconds", "retention_days", "cooldown_hours"):
        if number(p[field]) <= 0:
            raise ValueError("invalid-policy-budget")
    if p["min_samples"] < 3:
        raise ValueError("insufficient-policy-samples")
    return p


class Ledger:
    def __init__(self, directory: Path):
        self.directory = directory

    @contextmanager
    def transaction(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        with (self.directory / ".lock").open("a") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def read(self, key: str) -> dict:
        return json.loads((self.directory / f"{identifier(key)}.json").read_text())

    def write(self, record: dict):
        target = self.directory / f"{identifier(record['id'])}.json"
        fd, path = tempfile.mkstemp(dir=self.directory, prefix=".pending-")
        try:
            with os.fdopen(fd, "w") as output:
                json.dump(record, output, ensure_ascii=False, indent=2, allow_nan=False)
                output.write("\n")
            os.replace(path, target)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def records(self, kind: str) -> list[dict]:
        records = [json.loads(p.read_text()) for p in sorted(self.directory.glob("*.json"))]
        return [r for r in records if r.get("kind") == kind]


def start(ledger: Ledger, *, group: dict, assets: list[str], root: Path = ROOT,
          optimization_id: str | None = None, purpose: str = "task", policy: dict | None = None) -> dict:
    if purpose not in {"task", "optimization"}:
        raise ValueError("invalid-purpose")
    record = {
        "schema_version": 1, "kind": "run", "id": "run-" + uuid.uuid4().hex,
        **{key: identifier(group[key]) for key in GROUP},
        "assets": {name: file_hash(root, name) for name in assets},
        "started_at": now(), "ended_at": None, "wall_seconds": None,
        "status": "running", "quality": "unknown", "usage_mode": "unavailable",
        "tokens": None, "tool_error_count": 0, "depth": 1 if optimization_id or purpose == "optimization" else 0,
        "optimization_id": identifier(optimization_id) if optimization_id else None,
        "measurement": "explicit-lifecycle",
    }
    with ledger.transaction():
        if optimization_id:
            candidate = ledger.read(optimization_id)
            if candidate.get("decision") != "allowed" or candidate.get("state") != "implementing":
                raise ValueError("optimization-not-admitted")
            current_policy = policy or policy_load()
            if not current_policy["enabled"] or candidate.get("policy_hash") != digest(current_policy):
                raise ValueError("authorization-changed")
            costs = [r for r in ledger.records("run") if r.get("optimization_id") == optimization_id]
            if any(r["status"] == "running" or r["tokens"] is None for r in costs):
                raise ValueError("cost-incomplete")
            if (sum(r["wall_seconds"] or 0 for r in costs) >= current_policy["max_optimization_seconds"]
                    or sum(r["tokens"]["total_tokens"] for r in costs) >= current_policy["max_optimization_tokens"]):
                raise ValueError("optimization-budget-exhausted")
        ledger.write(record)
    return record


def token_values(values: dict | None) -> dict | None:
    if values is None:
        return None
    # A source total is required. Subset counters are never added to the total.
    if "total_tokens" not in values:
        raise ValueError("missing-total-tokens")
    return {key: number(values[key], integer=True) if key in values else None for key in TOKEN_FIELDS}


def finish(ledger: Ledger, run_id: str, *, status: str, quality: str,
           tokens: dict | None = None, tool_errors: int = 0) -> dict:
    if status not in {"passed", "failed", "interrupted"} or quality not in {"passed", "failed", "unknown"}:
        raise ValueError("invalid-outcome")
    with ledger.transaction():
        record = ledger.read(run_id)
        if record.get("kind") != "run" or record.get("measurement") != "explicit-lifecycle":
            raise ValueError("not-explicit-run")
        values = token_values(tokens)
        if record["status"] != "running":
            if record["status"] != status or record["quality"] != quality:
                raise ValueError("conflicting-finish")
            # Late host usage can seal missing data without moving the end boundary.
            if values is not None:
                if record["tokens"] is not None and record["tokens"] != values:
                    raise ValueError("conflicting-usage")
                record.update(tokens=values, usage_mode="actual")
                ledger.write(record)
            return record
        ended = now()
        elapsed = (datetime.fromisoformat(ended) - datetime.fromisoformat(record["started_at"])).total_seconds()
        if elapsed < 0:
            raise ValueError("clock-moved-backwards")
        record.update(ended_at=ended, wall_seconds=elapsed, status=status, quality=quality,
                      tokens=values, usage_mode="actual" if values is not None else "unavailable",
                      tool_error_count=number(tool_errors, integer=True))
        ledger.write(record)
    return record


def import_usage(ledger: Ledger, records: list[dict], usage_mode: str) -> int:
    """Import only allowlisted numeric facts; session rows are provisional, not full runs."""
    with ledger.transaction():
        for row in records:
            identity = [row.get("source_session_hash"), row.get("turn_hash")]
            if not all(isinstance(item, str) and item for item in identity):
                raise ValueError("missing-usage-identity")
            key = "usage-" + digest(identity)[:32]
            record = {
                "schema_version": 1, "id": key, "kind": "usage", "measurement": "provisional",
                "usage_mode": usage_mode if usage_mode in {"actual", "estimated_fallback"} else "unavailable",
                "tokens": token_values(row) if usage_mode == "actual" else None,
                "tool_call_count": number(row.get("tool_call_count", 0), integer=True),
                "tool_error_count": number(row.get("retry_count", 0), integer=True),
                "updated_at": now(),
            }
            ledger.write(record)
    return len(records)


def prune(ledger: Ledger, policy: dict) -> dict:
    """Keep active and referenced facts; remove expired unreferenced local projections."""
    cutoff = datetime.now(timezone.utc).timestamp() - policy["retention_days"] * 86400
    removed = 0
    with ledger.transaction():
        protected = set()
        for candidate in ledger.records("optimization"):
            protected.add(candidate["source_run"])
            protected.update(r["id"] for r in ledger.records("run") if r.get("optimization_id") == candidate["id"])
        for effect in ledger.records("effect"):
            protected.update(effect["before"] + effect["after"] + effect["cost_runs"])
        for record in ledger.records("usage") + ledger.records("run"):
            stamp = record.get("ended_at") or record.get("updated_at")
            if record["id"] in protected or not stamp or record.get("status") == "running":
                continue
            if datetime.fromisoformat(stamp).timestamp() < cutoff:
                (ledger.directory / f"{record['id']}.json").unlink()
                (ledger.directory / f"review-{record['id']}.json").unlink(missing_ok=True)
                removed += 1
    return {"status": "ok", "removed": removed, "retention_days": policy["retention_days"]}


def review(ledger: Ledger, run_id: str, policy: dict) -> dict:
    """Signals are hypotheses. An evidence-bearing plan is required before admission."""
    with ledger.transaction():
        run = ledger.read(run_id)
        if run.get("kind") != "run" or run["status"] == "running":
            raise ValueError("unfinished-run")
        signals = []
        if run["status"] != "passed" or run["quality"] == "failed":
            signals.append("execution-failure")
        if run["tool_error_count"]:
            signals.append("tool-errors")
        if run["wall_seconds"] > policy["slow_run_seconds"]:
            signals.append("slow-run")
        if run["tokens"] is None:
            signals.append("usage-unavailable")
        result = {"schema_version": 1, "id": "review-" + run_id, "kind": "review",
                  "source_run": run_id, "signals": signals, "root_cause": "hypothesis" if signals else "none",
                  "action": "record-cost-only" if run["depth"] else ("investigate" if signals else "none")}
        ledger.write(result)
    return result


def plan(ledger: Ledger, *, run_id: str, files: list[str], evidence: str, change: str,
         sprint: str, seconds: float, tokens: int, risk: str, root: Path = ROOT,
         cost_runs: list[str] | None = None, problem: str = "execution-efficiency", policy: dict | None = None) -> dict:
    if not files or risk not in {"nonbehavioral", "behavioral", "boundary"}:
        raise ValueError("invalid-plan")
    change, sprint = identifier(change), identifier(sprint)
    if not evidence.startswith(f"openspec/changes/{change}/"):
        raise ValueError("evidence-outside-change")
    evidence_path = relative_file(root, evidence)
    if not evidence_path.is_file():
        raise ValueError("missing-evidence")
    with ledger.transaction():
        run = ledger.read(run_id)
        if run.get("kind") != "run" or run["status"] == "running":
            raise ValueError("unfinished-source")
        hashes = {name: file_hash(root, name) for name in sorted(set(files))}
        analysis_runs = [ledger.read(k) for k in set(cost_runs or [])]
        def bind_costs(candidate_id):
            if any(r.get("kind") != "run" or r["depth"] != 1
                   or r.get("optimization_id") not in {None, candidate_id}
                   or r["status"] == "running" for r in analysis_runs):
                raise ValueError("invalid-analysis-cost")
            for cost in analysis_runs:
                cost["optimization_id"] = candidate_id
                ledger.write(cost)
        current_policy = policy or policy_load()
        fingerprint = digest([tuple(run[k] for k in GROUP), sorted(hashes), identifier(problem)])
        for previous in ledger.records("optimization"):
            if previous.get("problem_fingerprint") != fingerprint:
                continue
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(previous["created_at"])).total_seconds()
            if previous["state"] in {"proposed", "implementing", "observing"} or age < current_policy["cooldown_hours"] * 3600:
                bind_costs(previous["id"])
                return previous
        # One candidate per source and file set: repeated reviews cannot restart a budget.
        key = "opt-" + digest([run_id, sorted(hashes)])[:24]
        if (ledger.directory / f"{key}.json").exists():
            return ledger.read(key)
        record = {
            "schema_version": 1, "kind": "optimization", "id": key, "source_run": run_id,
            "depth": run["depth"], "files": hashes, "evidence": evidence,
            "evidence_hash": file_hash(root, evidence), "change": change, "sprint": sprint,
            "estimated_seconds": number(seconds), "estimated_tokens": number(tokens, integer=True),
            "risk": risk, "state": "proposed", "decision": "pending", "created_at": now(),
            "problem_fingerprint": fingerprint,
        }
        bind_costs(key)
        ledger.write(record)
    return record


def gate_check(root: Path, candidate: dict) -> bool:
    # Known governance tools only; argv never comes from session text.
    commands = [
        [sys.executable, "scripts/validate-change-identity.py"],
        ["openspec", "validate", candidate["change"]],
        [sys.executable, "scripts/validate-sprint-scope.py", candidate["sprint"], "--item", candidate["change"]],
        [sys.executable, "scripts/sync-workflow-status.py", "--event", "opsx.start",
         "--change", candidate["change"], "--sprint", candidate["sprint"], "--dry-run"],
    ]
    for argv in commands:
        try:
            result = subprocess.run(argv, cwd=root, capture_output=True, timeout=60, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return False
        if result.returncode:
            return False
    return True


def decide(ledger: Ledger, candidate_id: str, policy: dict, *, root: Path = ROOT,
           check=gate_check) -> dict:
    with ledger.transaction():
        candidate = ledger.read(candidate_id)
        if candidate.get("kind") != "optimization":
            raise ValueError("not-optimization")
        reasons = []
        if not policy["enabled"] or not policy.get("authorization"):
            reasons.append("authorization-disabled")
        if candidate["depth"]:
            reasons.append("recursive-optimization")
        if candidate["risk"] == "boundary":
            reasons.append("boundary-decision-required")
        for name, old_hash in candidate["files"].items():
            allowed = name in policy["allowed_files"] or any(name.startswith(p) for p in policy["allowed_prefixes"])
            if not allowed or name in policy["protected_files"]:
                reasons.append("outside-authorized-scope")
            if file_hash(root, name) != old_hash:
                reasons.append("asset-drift")
        if file_hash(root, candidate["evidence"]) != candidate["evidence_hash"]:
            reasons.append("evidence-drift")
        if candidate["estimated_seconds"] > policy["max_optimization_seconds"] or candidate["estimated_tokens"] > policy["max_optimization_tokens"]:
            reasons.append("estimated-budget-exceeded")
        costs = [r for r in ledger.records("run") if r.get("optimization_id") == candidate_id]
        if not costs:
            reasons.append("analysis-cost-missing")
        if any(r["status"] == "running" or r["tokens"] is None for r in costs):
            reasons.append("cost-incomplete")
        if sum(r["wall_seconds"] or 0 for r in costs) >= policy["max_optimization_seconds"]:
            reasons.append("time-budget-exhausted")
        if sum((r["tokens"] or {}).get("total_tokens", 0) for r in costs) >= policy["max_optimization_tokens"]:
            reasons.append("token-budget-exhausted")
        for other in ledger.records("optimization"):
            if other["id"] != candidate_id and other["source_run"] == candidate["source_run"] and other["decision"] == "allowed":
                reasons.append("source-budget-already-reserved")
        if candidate["state"] not in {"proposed", "implementing"}:
            reasons.append("candidate-already-closed")
        if not reasons and not check(root, candidate):
            reasons.append("change-sprint-gate-failed")
        candidate.update(decision="blocked" if reasons else "allowed", reasons=sorted(set(reasons)),
                         policy_hash=digest(policy))
        if not reasons:
            candidate["state"] = "implementing"
        ledger.write(candidate)
    return candidate


def seal(ledger: Ledger, candidate_id: str, evidence: str, *, root: Path = ROOT) -> dict:
    """Bind independently checked repair evidence and resulting versions before observation."""
    with ledger.transaction():
        candidate = ledger.read(candidate_id)
        if candidate.get("decision") != "allowed" or candidate.get("state") != "implementing":
            raise ValueError("repair-not-implementing")
        if not evidence.startswith(f"openspec/changes/{candidate['change']}/"):
            raise ValueError("verification-outside-change")
        evidence_hash = file_hash(root, evidence)
        if evidence_hash == "absent":
            raise ValueError("verification-missing")
        costs = [r for r in ledger.records("run") if r.get("optimization_id") == candidate_id]
        if len(costs) < 2 or any(r["status"] != "passed" or r["quality"] != "passed" for r in costs):
            raise ValueError("repair-cost-or-validation-incomplete")
        delivered = {name: file_hash(root, name) for name in candidate["files"]}
        if delivered == candidate["files"]:
            raise ValueError("no-repair-delta")
        candidate.update(state="observing", repair_verified=True, verified_at=now(),
                         verification_evidence=evidence, verification_hash=evidence_hash,
                         delivered_assets=delivered)
        ledger.write(candidate)
    return candidate


def evaluate(ledger: Ledger, candidate_id: str, before: list[str], after: list[str], policy: dict,
             *, root: Path = ROOT) -> dict:
    with ledger.transaction():
        candidate = ledger.read(candidate_id)
        if candidate.get("kind") != "optimization" or candidate["decision"] != "allowed":
            raise ValueError("candidate-not-admitted")
        if set(before) & set(after) or len(set(before)) != len(before) or len(set(after)) != len(after):
            raise ValueError("duplicate-comparison-samples")
        baseline, followup = [ledger.read(k) for k in before], [ledger.read(k) for k in after]
        samples = baseline + followup
        costs = [r for r in ledger.records("run") if r.get("optimization_id") == candidate_id]
        reasons = []
        if len(baseline) < policy["min_samples"] or len(followup) < policy["min_samples"]:
            reasons.append("insufficient-samples")
        if any(r.get("kind") != "run" or r.get("measurement") != "explicit-lifecycle"
               or r.get("status") == "running" or r.get("depth") for r in samples):
            reasons.append("incomplete-or-optimization-samples")
        groups = {tuple(r.get(k) for k in GROUP) for r in samples}
        if len(groups) != 1 or any("unknown" in group for group in groups):
            reasons.append("incomparable-samples")
        if any(r.get("quality") == "unknown" for r in samples):
            reasons.append("quality-unknown")
        if any(r.get("status") != "passed" or r.get("quality") != "passed" for r in baseline):
            reasons.append("invalid-baseline-quality")
        paths = set(candidate["files"])
        if any(not paths.issubset(r.get("assets", {})) for r in samples):
            reasons.append("missing-asset-version")
        if baseline and followup:
            old_versions = {digest({p: r.get("assets", {}).get(p) for p in paths}) for r in baseline}
            new_versions = {digest({p: r.get("assets", {}).get(p) for p in paths}) for r in followup}
            if len(old_versions) != 1 or len(new_versions) != 1 or old_versions == new_versions:
                reasons.append("mixed-or-unchanged-versions")
            if any(r.get("ended_at") is None for r in samples) or (
                max(r["ended_at"] or "" for r in baseline) > min(r.get("started_at", "") for r in followup)
            ):
                reasons.append("invalid-sample-order")
        if not costs or any(r["status"] == "running" or r["quality"] != "passed" for r in costs):
            reasons.append("repair-not-verified")
        if not candidate.get("repair_verified"):
            reasons.append("repair-not-sealed")
        elif file_hash(root, candidate["verification_evidence"]) != candidate["verification_hash"]:
            reasons.append("verification-evidence-drift")
        if any({p: r.get("assets", {}).get(p) for p in paths} != candidate["files"] for r in baseline):
            reasons.append("baseline-version-mismatch")
        if any({p: r.get("assets", {}).get(p) for p in paths} != candidate.get("delivered_assets") for r in followup):
            reasons.append("delivered-version-mismatch")
        result = {"schema_version": 1, "id": "effect-" + candidate_id, "kind": "effect",
                  "optimization_id": candidate_id, "before": before, "after": after,
                  "cost_runs": [r["id"] for r in costs], "sample_count": [len(baseline), len(followup)],
                  "status": "observing", "reasons": reasons, "time": None, "tokens": None}
        if any(r.get("status") in {"failed", "interrupted"} or r.get("quality") == "failed" for r in followup + costs):
            result.update(status="regressed", reasons=reasons + ["quality-regression"])
        elif not reasons:
            for field, source in (("time", "wall_seconds"), ("tokens", "tokens")):
                def value(r):
                    return r[source] if field == "time" else (r[source] or {}).get("total_tokens")
                old, new, expense = [value(r) for r in baseline], [value(r) for r in followup], [value(r) for r in costs]
                if any(v is None for v in old + new + expense):
                    continue
                median = statistics.median(old)
                current = statistics.median(new)
                result[field] = {"baseline_median": median, "after_median": current,
                                 "optimization_cost": sum(expense),
                                 "net_saving": median * len(new) - sum(new) - sum(expense),
                                 "regressed": current > median * (1 + policy["regression_ratio"])}
            metrics = [result[k] for k in ("time", "tokens") if result[k] is not None]
            if any(m["regressed"] for m in metrics):
                result["status"] = "regressed"
            elif len(metrics) == 2 and all(m["net_saving"] >= 0 for m in metrics) and any(m["net_saving"] > 0 for m in metrics):
                result["status"] = "benefit-confirmed"
            else:
                result["reasons"].append("cost-not-recovered-or-metrics-missing")
        candidate["state"] = result["status"]
        ledger.write(candidate)
        ledger.write(result)
    return result


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--store", type=Path, default=ROOT / "logs/governance-feedback")
    sub = p.add_subparsers(dest="action", required=True)
    s = sub.add_parser("start", help="调用前开始计时，版本按文件哈希记录")
    for key in GROUP:
        s.add_argument("--" + key.replace("_", "-"), required=True)
    s.add_argument("--asset", action="append", default=[])
    s.add_argument("--optimization-id")
    s.add_argument("--purpose", choices=["task", "optimization"], default="task")
    s = sub.add_parser("finish", help="结束运行；无真实用量时省略 --tokens")
    s.add_argument("run_id")
    s.add_argument("--status", choices=["passed", "failed", "interrupted"], required=True)
    s.add_argument("--quality", choices=["passed", "failed", "unknown"], required=True)
    s.add_argument("--tokens", type=int)
    s.add_argument("--tool-errors", type=int, default=0)
    s = sub.add_parser("review", help="生成幂等信号；信号不等于根因")
    s.add_argument("run_id")
    s = sub.add_parser("plan", help="登记有证据的优化方案，随后 decide")
    s.add_argument("--run-id", required=True)
    s.add_argument("--file", action="append", required=True)
    for name in ("evidence", "change", "sprint"):
        s.add_argument("--" + name, required=True)
    s.add_argument("--seconds", type=float, required=True)
    s.add_argument("--tokens", type=int, required=True)
    s.add_argument("--risk", choices=["nonbehavioral", "behavioral", "boundary"], required=True)
    s.add_argument("--problem", required=True, help="稳定问题分类，同类任务去重及冷却")
    s.add_argument("--cost-run", action="append", default=[], help="绑定此前优化分析运行，避免遗漏优化自身成本")
    s = sub.add_parser("decide", help="验证授权、范围、预算及真实 Change/Sprint 门禁")
    s.add_argument("candidate_id")
    s = sub.add_parser("evaluate", help="比较同组完整样本并扣除优化成本")
    s.add_argument("candidate_id")
    s.add_argument("--before", action="append", required=True)
    s.add_argument("--after", action="append", required=True)
    s = sub.add_parser("seal", help="绑定修复验证证据和交付版本，进入收益观察")
    s.add_argument("candidate_id")
    s.add_argument("--evidence", required=True)
    s = sub.add_parser("show", help="读取脱敏运行或候选记录")
    s.add_argument("record_id")
    sub.add_parser("prune", help="清理过期且未被优化证据引用的本地派生事实")
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        ledger, policy = Ledger(args.store), policy_load()
        if args.action == "start":
            result = start(ledger, group={key: getattr(args, key) for key in GROUP}, assets=args.asset,
                           optimization_id=args.optimization_id, purpose=args.purpose)
        elif args.action == "finish":
            result = finish(ledger, args.run_id, status=args.status, quality=args.quality,
                            tokens={"total_tokens": args.tokens} if args.tokens is not None else None,
                            tool_errors=args.tool_errors)
            result = {"run_id": result["id"], "wall_seconds": result["wall_seconds"],
                      "usage_mode": result["usage_mode"], "review": review(ledger, args.run_id, policy)}
        elif args.action == "review":
            result = review(ledger, args.run_id, policy)
        elif args.action == "plan":
            result = plan(ledger, run_id=args.run_id, files=args.file, evidence=args.evidence,
                          change=args.change, sprint=args.sprint, seconds=args.seconds, tokens=args.tokens,
                          risk=args.risk, cost_runs=args.cost_run, problem=args.problem, policy=policy)
        elif args.action == "decide":
            result = decide(ledger, args.candidate_id, policy)
        elif args.action == "evaluate":
            result = evaluate(ledger, args.candidate_id, args.before, args.after, policy)
        elif args.action == "seal":
            result = seal(ledger, args.candidate_id, args.evidence)
        elif args.action == "prune":
            result = prune(ledger, policy)
        else:
            result = ledger.read(args.record_id)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 2 if result.get("decision") == "blocked" else 0
    except (ValueError, KeyError, OSError, TypeError):
        # Exception bodies may contain caller paths or private data.
        print(json.dumps({"status": "error", "reason": "invalid-input-or-ledger",
                          "recommended_action": "检查CLI参数、策略及本地台账；不改变主工作流状态。"}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
