"""Independent two-party installation verification; ordinary proposals cannot call it."""
from typing import Literal
from .replacement_proof import Strict, Hash, Name, PROTECTED, digest
from pydantic import Field


class PolicyTransition(Strict):
    capability: Name
    requirement: str = Field(min_length=1, max_length=256)
    before_sha256: Hash
    after_sha256: Hash


class Installation(Strict):
    schema_version: Literal[1]
    kind: Literal['policy_installation']
    project_id: Hash
    binding_revision: Hash
    mechanism_change: Name
    from_policy: Name
    to_policy: Name
    release_digest: Hash
    verifier_digest: Hash
    delta_digest: Hash
    acceptance_digest: Hash
    delivery_digest: Hash
    baseline_digest: Hash
    expected_digest: Hash
    protected_obligations: list[str] = Field(min_length=10, max_length=10)
    operation_id: Name
    transitions: list[PolicyTransition] = Field(min_length=1, max_length=1)


def verify_installation(manifest: Installation, trust, *, ops_receipt, owner_receipt,
                        project, current_policy, release_digest, verifier_digest, now=None, historical=False):
    if (manifest.project_id != project.key or manifest.binding_revision != project.binding_revision
            or manifest.from_policy != current_policy or manifest.to_policy == current_policy
            or manifest.to_policy != trust.policy_version or manifest.release_digest != release_digest
            or release_digest != trust.release_digest or manifest.verifier_digest != verifier_digest
            or set(manifest.protected_obligations) != PROTECTED):
        raise ValueError('bootstrap_manifest_mismatch')
    if not trust.independent_bootstrap():
        raise ValueError('bootstrap_roles_not_independent')
    bindings = {'project_id': project.key, 'binding_revision': project.binding_revision,
                'installation_digest': digest(manifest.model_dump()), 'operation_id': manifest.operation_id,
                'release_digest': release_digest}
    trust.verify(ops_receipt, purpose='bootstrap.ops', bindings=bindings, now=now, historical=historical)
    trust.verify(owner_receipt, purpose='bootstrap.owner', bindings=bindings, now=now, historical=historical)
    return bindings
