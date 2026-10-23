"""Strict content-bound proposals. Deployment-reviewed profiles are not repo input.

This layer never grants authority or writes archive facts. A proposal is only a
candidate until the independent authorization and archive checks have passed.
"""
from __future__ import annotations

import hashlib
import json
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Hash = Annotated[str, Field(pattern=r'^[a-f0-9]{64}$')]
Name = Annotated[str, Field(min_length=1, max_length=128, pattern=r'^[A-Za-z0-9_-]+$')]
PROTECTED = frozenset(('identity', 'complete_unique_chain', 'evidence', 'compatibility_conditions',
                       'concurrency', 'permissions', 'independent_signoff', 'scope_complete',
                       'history', 'recovery_idempotence'))
MAX_BYTES = 256 * 1024


class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, frozen=True)

    @model_validator(mode='before')
    @classmethod
    def version_is_integer(cls, value):
        if isinstance(value, dict) and 'schema_version' in value and type(value['schema_version']) is not int:
            raise ValueError('schema_version must be an integer')
        return value


class Evidence(Strict):
    path: str = Field(min_length=1, max_length=512)
    sha256: Hash


class Obligation(Strict):
    id: str
    source: Evidence
    before: str = Field(min_length=1, max_length=32768)
    after: str = Field(min_length=1, max_length=32768)


class RuleEdit(Strict):
    profile_id: Name
    before: str = Field(min_length=1, max_length=32768)
    after: str = Field(min_length=1, max_length=32768)
    exception: Literal['compatible_append_verified']


class Proposal(Strict):
    schema_version: Literal[1]
    classification: Literal['guarded_exception_extension']
    project_id: Hash
    binding_revision: Hash
    successor: Name
    predecessors: list[Name] = Field(min_length=1, max_length=256)
    capability: Name
    requirement: str = Field(min_length=1, max_length=256)
    before: str = Field(min_length=1, max_length=65536)
    after: str = Field(min_length=1, max_length=65536)
    delta_sha256: Hash
    acceptance_sha256: Hash
    delivery_sha256: Hash
    policy_version: Name
    verifier_version: Literal['replacement-v1']
    obligations: list[Obligation] = Field(min_length=10, max_length=10)
    edits: list[RuleEdit] = Field(min_length=1, max_length=32)
    review: Evidence
    regression: Evidence


def canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def digest(value: dict) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def strict_json(raw: bytes) -> dict:
    if len(raw) > MAX_BYTES:
        raise ValueError('oversized_proposal')
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError('duplicate_key')
            out[key] = value
        return out
    value = json.loads(raw, object_pairs_hook=pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(ValueError('non_finite_number')))
    if not isinstance(value, dict): raise ValueError('object_required')
    return value


def parse(raw: bytes) -> Proposal:
    return Proposal.model_validate(strict_json(raw))


def classify(proposal: Proposal, profiles: dict) -> None:
    """Only exact independently reviewed transformations, never arbitrary predicates.

    Profiles come from the verified deployment release, not the proposal. They
    bind complete before/after texts as well as individual mapped edits. This
    intentionally rejects semantically similar but unreviewed prose.
    """
    from .compatible_successor import scenarios
    scenarios(proposal.before)
    scenarios(proposal.after)
    if len(set(proposal.predecessors)) != len(proposal.predecessors) or proposal.successor in proposal.predecessors:
        raise ValueError('ambiguous_chain')
    if {o.id for o in proposal.obligations} != PROTECTED:
        raise ValueError('protected_obligations_missing')
    for obligation in proposal.obligations:
        if obligation.before != obligation.after:
            raise ValueError('protected_obligation_changed')
    transformed = proposal.before
    seen = set()
    for edit in proposal.edits:
        profile = profiles.get(edit.profile_id)
        expected = {'classification': 'guarded_exception_extension',
                    'exception': 'compatible_append_verified', 'before': edit.before, 'after': edit.after,
                    'before_sha256': hashlib.sha256(proposal.before.encode()).hexdigest(),
                    'after_sha256': hashlib.sha256(proposal.after.encode()).hexdigest(),
                    'obligations_sha256': digest({'obligations': [o.model_dump() for o in proposal.obligations]})}
        if not profile or profile != expected or edit.profile_id in seen:
            raise ValueError('unsupported_replacement')
        seen.add(edit.profile_id)
        if edit.before == edit.after or transformed.count(edit.before) != 1:
            raise ValueError('ambiguous_rule_mapping')
        if any(edit.before in o.before or o.before in edit.before for o in proposal.obligations):
            raise ValueError('protected_obligation_changed')
        transformed = transformed.replace(edit.before, edit.after, 1)
    if transformed != proposal.after:
        raise ValueError('unmapped_difference')
