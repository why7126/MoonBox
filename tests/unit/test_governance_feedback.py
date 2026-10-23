"""治理闭环：权限、计量、重放、缺失事实与效果的正反例。"""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import governance_feedback as gf

GROUP = dict(command="spec-opt", task_class="rules", model="fixed-model", environment="fixture",
             validation_profile="gates-v1", workload_key="same-input")


@pytest.fixture
def setup(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/demo.py").write_text("old")
    evidence = tmp_path / "openspec/changes/demo/evidence.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("可复核证据")
    return gf.Ledger(tmp_path / "ledger"), tmp_path, gf.policy_load()


def run(ledger, root, *, seconds=10, tokens=100, purpose="task", quality="passed"):
    r = gf.start(ledger, group=GROUP, assets=["scripts/demo.py"], root=root, purpose=purpose)
    r = gf.finish(ledger, r["id"], status="passed", quality=quality,
                  tokens=None if tokens is None else {"total_tokens": tokens})
    # Controlled numeric fixtures are not presented as real measurements.
    with ledger.transaction():
        r["wall_seconds"] = seconds
        ledger.write(r)
    return r


def candidate(setup, **overrides):
    ledger, root, policy = setup
    source = run(ledger, root)
    analysis = run(ledger, root, seconds=1, tokens=1, purpose="optimization")
    params = dict(run_id=source["id"], files=["scripts/demo.py"],
                  evidence="openspec/changes/demo/evidence.md", change="demo", sprint="sprint-011",
                  seconds=10, tokens=100, risk="behavioral", root=root, cost_runs=[analysis["id"]])
    params.update(overrides)
    c = gf.plan(ledger, **params)
    return c, params


def test_lifecycle_missing_usage_idempotence_and_late_usage(setup):
    ledger, root, _ = setup
    r = run(ledger, root, tokens=None)
    again = gf.finish(ledger, r["id"], status="passed", quality="passed", tokens={"total_tokens": 0})
    assert again["usage_mode"] == "actual"
    assert again["tokens"]["total_tokens"] == 0
    assert again["ended_at"] == r["ended_at"]
    assert again["wall_seconds"] == r["wall_seconds"]
    with pytest.raises(ValueError):
        gf.finish(ledger, r["id"], status="failed", quality="failed")
    with pytest.raises(ValueError):
        gf.finish(ledger, r["id"], status="passed", quality="passed", tokens={"total_tokens": 5})


def test_import_only_numeric_projections_and_dedup(setup):
    ledger, _, _ = setup
    row = dict(source_session_hash="session", turn_hash="turn", total_tokens=15,
               input_tokens=10, cached_input_tokens=8, output_tokens=5, reasoning_output_tokens=3,
               prompt="PRIVATE", source_data_file="/private/session", retry_count=2)
    gf.import_usage(ledger, [row], "actual")
    gf.import_usage(ledger, [row], "actual")
    records = ledger.records("usage")
    assert len(records) == 1
    assert records[0]["tokens"]["total_tokens"] == 15
    assert records[0]["measurement"] == "provisional"
    assert "PRIVATE" not in json.dumps(records) and "/private" not in json.dumps(records)
    assert records[0]["tool_error_count"] == 2


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), True, "3"])
def test_invalid_counter_rejected(value):
    with pytest.raises(ValueError):
        gf.token_values({"total_tokens": value})


@pytest.mark.parametrize("path", ["../escape", "/tmp/secret", ".env.local", ".git/config"])
def test_path_rejection(setup, path):
    _, root, _ = setup
    with pytest.raises(ValueError):
        gf.relative_file(root, path)


def test_symlink_escape(setup, tmp_path):
    _, root, _ = setup
    (root / "scripts/escape").symlink_to("/tmp")
    with pytest.raises(ValueError):
        gf.relative_file(root, "scripts/escape/secret")


def test_review_is_hypothesis_and_optimization_cannot_recurse(setup):
    ledger, root, policy = setup
    r = run(ledger, root, seconds=400, tokens=None, purpose="optimization")
    report = gf.review(ledger, r["id"], policy)
    assert report["action"] == "record-cost-only"
    assert report["root_cause"] == "hypothesis"
    assert set(report["signals"]) == {"slow-run", "usage-unavailable"}
    c, _ = candidate(setup, run_id=r["id"])
    assert "recursive-optimization" in gf.decide(ledger, c["id"], policy, root=root, check=lambda *_: True)["reasons"]


def test_plan_replay_and_gate_rejection(setup):
    ledger, root, policy = setup
    c, params = candidate(setup)
    assert gf.plan(ledger, **params)["id"] == c["id"]
    blocked = gf.decide(ledger, c["id"], policy, root=root, check=lambda *_: False)
    assert blocked["reasons"] == ["change-sprint-gate-failed"]
    allowed = gf.decide(ledger, c["id"], policy, root=root, check=lambda *_: True)
    assert allowed["decision"] == "allowed"


@pytest.mark.parametrize("override,reason", [
    ({"files": ["src/business.py"]}, "outside-authorized-scope"),
    ({"files": ["rules/security.md"]}, "outside-authorized-scope"),
    ({"risk": "boundary"}, "boundary-decision-required"),
    ({"tokens": 30001}, "estimated-budget-exceeded"),
    ({"seconds": 601}, "estimated-budget-exceeded"),
    ({"cost_runs": []}, "analysis-cost-missing"),
])
def test_admission_guards(setup, override, reason):
    ledger, root, policy = setup
    c, _ = candidate(setup, **override)
    assert reason in gf.decide(ledger, c["id"], policy, root=root, check=lambda *_: True)["reasons"]


def test_revocation_drift_and_child_budget(setup):
    ledger, root, policy = setup
    c, _ = candidate(setup)
    gf.decide(ledger, c["id"], policy, root=root, check=lambda *_: True)
    disabled = dict(policy, enabled=False)
    with pytest.raises(ValueError, match="authorization-changed"):
        gf.start(ledger, group=GROUP, assets=[], root=root, optimization_id=c["id"], policy=disabled)
    child = gf.start(ledger, group=GROUP, assets=[], root=root, optimization_id=c["id"], policy=policy)
    with pytest.raises(ValueError, match="cost-incomplete"):
        gf.start(ledger, group=GROUP, assets=[], root=root, optimization_id=c["id"], policy=policy)
    gf.finish(ledger, child["id"], status="passed", quality="passed", tokens={"total_tokens": 30000})
    with pytest.raises(ValueError, match="budget-exhausted"):
        gf.start(ledger, group=GROUP, assets=[], root=root, optimization_id=c["id"], policy=policy)
    (root / "scripts/demo.py").write_text("unrelated-edit")
    assert "asset-drift" in gf.decide(ledger, c["id"], policy, root=root, check=lambda *_: True)["reasons"]


def effect_fixture(setup):
    ledger, root, policy = setup
    before = [run(ledger, root)["id"] for _ in range(3)]
    c, _ = candidate(setup)
    gf.decide(ledger, c["id"], policy, root=root, check=lambda *_: True)
    cost = gf.start(ledger, group=GROUP, assets=[], root=root, optimization_id=c["id"], policy=policy)
    gf.finish(ledger, cost["id"], status="passed", quality="passed", tokens={"total_tokens": 1})
    (root / "scripts/demo.py").write_text("new")
    gf.seal(ledger, c["id"], "openspec/changes/demo/evidence.md", root=root)
    after = [run(ledger, root, seconds=5, tokens=50)["id"] for _ in range(3)]
    return c, before, after


def test_net_benefit_deducts_all_costs(setup):
    ledger, root, policy = setup
    c, before, after = effect_fixture(setup)
    result = gf.evaluate(ledger, c["id"], before, after, policy, root=root)
    assert result["status"] == "benefit-confirmed"
    assert result["tokens"]["optimization_cost"] == 2
    assert result["tokens"]["net_saving"] == 148
    assert len(result["cost_runs"]) == 2


@pytest.mark.parametrize("field,value,expected", [
    ("quality", "failed", "regressed"),
    ("quality", "unknown", "observing"),
    ("tokens", None, "observing"),
    ("model", "other-model", "observing"),
    ("wall_seconds", 100, "regressed"),
])
def test_effect_does_not_hide_regressions_or_missing_facts(setup, field, value, expected):
    ledger, root, policy = setup
    c, before, after = effect_fixture(setup)
    with ledger.transaction():
        for key in after:
            r = ledger.read(key)
            r[field] = value
            ledger.write(r)
    assert gf.evaluate(ledger, c["id"], before, after, policy, root=root)["status"] == expected


def test_insufficient_samples_and_overlap(setup):
    ledger, root, policy = setup
    c, before, after = effect_fixture(setup)
    assert gf.evaluate(ledger, c["id"], before, after[:1], policy, root=root)["status"] == "observing"
    with pytest.raises(ValueError):
        gf.evaluate(ledger, c["id"], before, before, policy, root=root)


def test_prune_keeps_referenced_and_active_facts(setup):
    ledger, root, policy = setup
    c, _ = candidate(setup)
    obsolete = run(ledger, root)
    with ledger.transaction():
        for key in (c["source_run"], obsolete["id"]):
            r = ledger.read(key)
            r["ended_at"] = "2000-01-01T00:00:00+00:00"
            ledger.write(r)
    assert gf.prune(ledger, policy)["removed"] == 1
    assert ledger.read(c["source_run"])


def test_real_cli_round_trip(tmp_path):
    cli = [sys.executable, str(ROOT / "scripts/governance_feedback.py"), "--store", str(tmp_path / "store")]
    args = [part for k, v in GROUP.items() for part in ("--" + k.replace("_", "-"), v)]
    first = subprocess.run(cli + ["start", *args], capture_output=True, text=True, check=True)
    key = json.loads(first.stdout)["id"]
    last = subprocess.run(cli + ["finish", key, "--status", "passed", "--quality", "passed"],
                          capture_output=True, text=True, check=True)
    result = json.loads(last.stdout)
    assert result["wall_seconds"] >= 0
    assert result["usage_mode"] == "unavailable"
    assert result["review"]["signals"] == ["usage-unavailable"]


def test_missing_yaml_hook_is_compact_nonblocking():
    result = subprocess.run([sys.executable, "-S", str(ROOT / "scripts/extract-ai-usage.py"),
                             "--post-command-hook", "--workflow-event", "explore", "--dry-run", "--json"],
                            capture_output=True, text=True)
    assert result.returncode == 0
    assert json.loads(result.stdout)["usage_mode"] == "unavailable"
    assert "Traceback" not in result.stderr


def test_usage_hook_integrates_and_dry_run_never_writes(tmp_path, monkeypatch):
    import ai_usage
    session = tmp_path / "session.jsonl"
    session.write_text("\n".join(json.dumps(r) for r in [
        {"type": "user_message", "text": "/opsx-apply demo"},
        {"payload": {"type": "token_count", "last_token_usage": {"total_tokens": 15}}},
    ]))
    store = tmp_path / "feedback"
    monkeypatch.setenv("GOVERNANCE_FEEDBACK_STORE", str(store))
    kwargs = dict(session_jsonl=session, out_dir=tmp_path / "usage", workflow_event="opsx.apply", changes=["demo"])
    ai_usage.post_command_hook(**kwargs, dry_run=True)
    assert not store.exists()
    result = ai_usage.post_command_hook(**kwargs)
    assert result["status"] == "ok"
    assert len(gf.Ledger(store).records("usage")) == 1
    # A bad local sink is a warning, not failure of the parent workflow.
    monkeypatch.setenv("GOVERNANCE_FEEDBACK_STORE", str(session))
    result = ai_usage.post_command_hook(**kwargs)
    assert result["status"] == "warning"
    assert "governance-feedback-unavailable" in result["warnings"]


def test_contract_validator_rejects_removed_hook(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("budget_validator", ROOT / "scripts/validate-agent-context-budget.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ("AGENTS.md", "rules/agent-context-budget.md",
                 ".agents/skills/workflow-sync/SKILL.md", ".agents/skills/spec-opt/SKILL.md"):
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("governance-feedback-loop.md scripts/governance_feedback.py")
    p = tmp_path / "docs/standards/governance-feedback-loop.md"
    p.parent.mkdir(parents=True)
    p.write_text("治理事实源")
    (tmp_path / "rules/governance-feedback-policy.json").write_text(gf.POLICY.read_text())
    assert module.validate_governance_feedback_contract(tmp_path) == []
    (tmp_path / "AGENTS.md").write_text("missing")
    assert module.validate_governance_feedback_contract(tmp_path)


def test_analysis_alone_cannot_seal_a_repair(setup):
    ledger, root, policy = setup
    c, _ = candidate(setup)
    gf.decide(ledger, c["id"], policy, root=root, check=lambda *_: True)
    (root / "scripts/demo.py").write_text("new")
    with pytest.raises(ValueError, match="incomplete"):
        gf.seal(ledger, c["id"], "openspec/changes/demo/evidence.md", root=root)


def test_repeat_problem_reuses_candidate_and_counts_new_analysis(setup):
    ledger, root, _ = setup
    first, _ = candidate(setup)
    second, _ = candidate(setup)
    assert first["id"] == second["id"]
    assert len([r for r in ledger.records("run") if r["optimization_id"] == first["id"]]) == 2


def test_verification_drift_cannot_confirm_benefit(setup):
    ledger, root, policy = setup
    c, before, after = effect_fixture(setup)
    (root / "openspec/changes/demo/evidence.md").write_text("changed")
    result = gf.evaluate(ledger, c["id"], before, after, policy, root=root)
    assert result["status"] == "observing"
    assert "verification-evidence-drift" in result["reasons"]


def test_cost_not_recovered_stays_observing(setup):
    ledger, root, policy = setup
    c, before, after = effect_fixture(setup)
    with ledger.transaction():
        cost = next(r for r in ledger.records("run") if r["optimization_id"] == c["id"])
        cost["tokens"]["total_tokens"] = 500
        ledger.write(cost)
    result = gf.evaluate(ledger, c["id"], before, after, policy, root=root)
    assert result["status"] == "observing"
    assert result["tokens"]["net_saving"] < 0
