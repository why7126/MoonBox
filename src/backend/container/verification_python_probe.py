"""Bounded external caller runs this probe inside the approved Python image."""
import asyncio
import json
from importlib.metadata import version
import anyio
import httpx
import pytest

async def main():
    with anyio.fail_after(5):
        assert await anyio.to_thread.run_sync(lambda: 42) == 42
    print(json.dumps({'status':'ready','versions':{name:version(name) for name in ('pytest','httpx','anyio')}}))

if __name__=='__main__':
    asyncio.run(main())
