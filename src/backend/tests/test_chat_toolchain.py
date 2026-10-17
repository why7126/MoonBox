import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import subprocess

import pytest
from app.chat.app_server import AppServer, ExecutorError
from app.chat.container_server import ContainerAppServer, verify_toolchain

spec = importlib.util.spec_from_file_location('check_toolchain', Path(__file__).parents[1] / 'container/check_toolchain.py')
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


def test_pins_match_build_inputs():
    root = Path(__file__).parents[1]
    packages = json.loads((root / 'container/toolchain/package.json').read_text())['dependencies']
    lock = json.loads((root / 'container/toolchain/package-lock.json').read_text())['packages']
    assert packages['@fission-ai/openspec'] == inventory.PINNED['openspec']
    assert packages['pnpm'] == inventory.PINNED['pnpm']
    for name, version in packages.items():
        assert lock['node_modules/' + name]['version'] == version
    dockerfile = (root / 'Dockerfile.chat-executor').read_text()
    assert 'node:' + inventory.PINNED['node'][1:] + '-bookworm-slim' in dockerfile
    assert 'uv==' + inventory.PINNED['uv'].split()[1] in dockerfile


@pytest.mark.parametrize('missing', [None, 'node', 'openspec', 'pnpm', 'uv'])
def test_tool_inventory(monkeypatch, missing):
    monkeypatch.setattr(inventory.shutil, 'which', lambda name: None if name == missing else '/bin/' + name)
    def run(args, **kwargs):
        assert kwargs['env']['OPENSPEC_TELEMETRY'] == '0'
        return SimpleNamespace(returncode=0, stdout=inventory.PINNED.get(Path(args[0]).name, 'version'))
    monkeypatch.setattr(inventory.subprocess, 'run', run)
    assert inventory.check_tools() == {'ready': missing is None, 'unavailable': [missing] if missing else []}


def test_package_cli_cold_start_gets_longer_probe_budget(monkeypatch):
    monkeypatch.setattr(inventory, 'TOOLS', {'node': ['--version'], 'npm': ['--version'], 'pnpm': ['--version'], 'openspec': ['--version']})
    monkeypatch.setattr(inventory.shutil, 'which', lambda name: '/bin/' + name)
    timeouts = {}
    def run(args, **kwargs):
        name = Path(args[0]).name
        timeouts[name] = kwargs['timeout']
        return SimpleNamespace(returncode=0, stdout=inventory.PINNED.get(name, 'version'))
    monkeypatch.setattr(inventory.subprocess, 'run', run)
    assert inventory.check_tools() == {'ready': True, 'unavailable': []}
    assert timeouts == {'node': 10, 'npm': 120, 'pnpm': 120, 'openspec': 120}


def test_container_cold_start_uses_separate_timeout():
    assert AppServer.version_timeout(None) == 30
    assert ContainerAppServer.version_timeout(None) == 180


@pytest.mark.parametrize('output,code', [('{}', 0), ('not-json secret', 1), ('{"ready":false,"unavailable":["node"]}', 1), ('{"ready":true,"unavailable":[]}', 0)])
def test_preflight_fail_closed(monkeypatch, output, code):
    run = Mock(return_value=SimpleNamespace(returncode=code, stdout=output))
    monkeypatch.setattr('app.chat.container_server.subprocess.run', run)
    server = SimpleNamespace(docker='docker', container_name='test')
    if output == '{"ready":true,"unavailable":[]}':
        verify_toolchain(server)
    else:
        with pytest.raises(ExecutorError, match='container_toolchain_unavailable'):
            verify_toolchain(server)
    assert 'moonbox-read' in run.call_args.args[0]


def test_preflight_timeout(monkeypatch):
    monkeypatch.setattr('app.chat.container_server.subprocess.run', Mock(side_effect=subprocess.TimeoutExpired('docker', 180)))
    with pytest.raises(ExecutorError, match='container_toolchain_unavailable'):
        verify_toolchain(SimpleNamespace(docker='docker', container_name='test'))


@pytest.mark.parametrize('failure', ['version', 'exit', 'timeout'])
def test_inventory_rejects_broken_tool(monkeypatch, failure):
    monkeypatch.setattr(inventory, 'TOOLS', {'node': ['--version']})
    monkeypatch.setattr(inventory.shutil, 'which', lambda _: '/bin/node')
    if failure == 'timeout':
        run = Mock(side_effect=subprocess.TimeoutExpired('node', 10))
    else:
        run = Mock(return_value=SimpleNamespace(returncode=1 if failure == 'exit' else 0, stdout='v18.0.0'))
    monkeypatch.setattr(inventory.subprocess, 'run', run)
    assert inventory.check_tools() == {'ready': False, 'unavailable': ['node']}


def test_tool_environment_keeps_credentials_private(tmp_path):
    import tomllib
    from app.chat.container_server import write_profiles
    write_profiles(tmp_path)
    config = tomllib.loads((tmp_path / 'config.toml').read_text())
    assert config['shell_environment_policy']['set']['HOME'] == '/tmp'
    assert config['shell_environment_policy']['set']['OPENSPEC_TELEMETRY'] == '0'
    assert config['shell_environment_policy']['set']['PATH'] == '/usr/local/bin:/usr/bin:/bin'
    for profile in config['permissions'].values():
        assert profile['filesystem']['/runtime'] == 'deny'
        assert profile['filesystem']['/work/.git'] == 'read'
        assert profile['network']['enabled'] is False
