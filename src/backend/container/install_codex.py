"""构建时下载固定官方Linux包，校验npm摘要，仅提取二进制白名单。"""
import base64
import hashlib
import io
import json
from pathlib import Path
import platform
import tarfile
import urllib.request

arch = {'aarch64': 'arm64', 'x86_64': 'x64'}[platform.machine()]
version = '0.153.4-linux-' + arch
with urllib.request.urlopen('https://registry.npmjs.org/@openai/codex/' + version, timeout=60) as response:
    package = json.load(response)
url = package['dist']['tarball']
assert url.startswith('https://registry.npmjs.org/@openai/codex/-/')
with urllib.request.urlopen(url, timeout=120) as response:
    data = response.read()
assert package['dist']['integrity'] == 'sha512-' + base64.b64encode(hashlib.sha512(data).digest()).decode()
with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
    for member in archive.getmembers():
        parts = Path(member.name).parts
        if not member.isfile() or parts[:2] != ('package', 'vendor'):
            continue
        assert len(parts) >= 4 and '..' not in parts
        output = Path('/out').joinpath(*parts[3:])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(archive.extractfile(member).read())
        output.chmod(0o755 if member.mode & 0o111 else 0o644)
    assert Path('/out/bin/codex').is_file()
