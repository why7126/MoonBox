"""Approved pytest entry inside the disposable product application's container."""
import asyncio
import anyio
import httpx


def test_real_application_http_and_thread_pool():
    from acceptance_product_adapter import configure
    configure()  # Refuse a database outside the isolated acceptance container.
    response = httpx.get('http://127.0.0.1:8000/chat', timeout=10)
    assert response.status_code == 200
    assert '<div id="root"></div>' in response.text and '/assets/' in response.text

    async def probe():
        with anyio.fail_after(5):
            assert await anyio.to_thread.run_sync(lambda: 42) == 42
    asyncio.run(probe())
