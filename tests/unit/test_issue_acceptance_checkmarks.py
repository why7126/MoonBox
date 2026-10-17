from scripts.workflow_sync.issue_subdocuments import acceptance_checkmark


def test_partial_sample_never_inherits_passing_command_probe():
    assert acceptance_checkmark(' ', 'partial', True) == ' '
    assert acceptance_checkmark('x', 'partial', True) == ' '


def test_signed_sample_requires_probe_for_new_checkmark_but_preserves_existing_signoff():
    assert acceptance_checkmark(' ', 'passed', True) == 'x'
    assert acceptance_checkmark(' ', 'passed', False) == ' '
    assert acceptance_checkmark('x', 'passed', False) == 'x'
