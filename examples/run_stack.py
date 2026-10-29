"""Reproducible orchestrator to boot and manage FastAPI and Next.js services."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from examples.bootstrap_integration import (
    DEFAULT_NEXT_DASHBOARD_DB_URL,
    DEFAULT_PYSRMKIT_DB_URL,
    bootstrap,
)

DEFAULT_API_PORT = 8000
DEFAULT_DASHBOARD_PORT = 3000


def wait_for_url(url: str, timeout: float = 15.0, interval: float = 0.25) -> bool:
    """Poll a URL until it responds with a success status code or timeout expires."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status in (200, 307, 308):
                    return True
        except Exception:
            time.sleep(interval)
    return False


@contextmanager
def run_integration_stack(
    api_port: int = DEFAULT_API_PORT,
    dashboard_port: int = DEFAULT_DASHBOARD_PORT,
    pysrmkit_db_url: str = DEFAULT_PYSRMKIT_DB_URL,
    nextjs_db_url: str = DEFAULT_NEXT_DASHBOARD_DB_URL,
    dev_mode: bool = False,
) -> Iterator[dict[str, str]]:
    """Context manager that starts FastAPI and Next.js and guarantees clean termination."""
    pysrmkit_root = Path(__file__).resolve().parent.parent
    dashboard_root = pysrmkit_root.parent / "resources" / "nextjs-acme-dashboard"

    # 1. Environment variables
    api_env = os.environ.copy()
    api_env["PYSRMKIT_DATABASE_URL"] = pysrmkit_db_url

    dashboard_env = os.environ.copy()
    dashboard_env["POSTGRES_URL"] = nextjs_db_url
    dashboard_env["PYSRMKIT_API_URL"] = f"http://127.0.0.1:{api_port}"
    dashboard_env["PORT"] = str(dashboard_port)

    # 2. Launch FastAPI
    api_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "examples.http_api:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(api_port),
    ]
    # Create both children under one ownership boundary. If launching
    # Next.js fails, the already-started FastAPI process is still cleaned up.
    api_proc: subprocess.Popen[bytes] | None = None
    dashboard_proc: subprocess.Popen[bytes] | None = None
    try:
        api_proc = subprocess.Popen(
            api_cmd,
            cwd=str(pysrmkit_root),
            env=api_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Production start is preferred over the development server.
        dashboard_cmd = (
            ["npm", "run", "dev", "--", "-p", str(dashboard_port)]
            if dev_mode
            else ["npx", "next", "start", "-p", str(dashboard_port)]
        )
        dashboard_proc = subprocess.Popen(
            dashboard_cmd,
            cwd=str(dashboard_root),
            env=dashboard_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        api_url = f"http://127.0.0.1:{api_port}"
        dashboard_url = f"http://localhost:{dashboard_port}"

        if not wait_for_url(f"{api_url}/health", timeout=10.0):
            raise TimeoutError(f"FastAPI host failed to respond on {api_url}/health")

        if not wait_for_url(dashboard_url, timeout=20.0):
            raise TimeoutError(f"Next.js dashboard failed to respond on {dashboard_url}")

        yield {
            "api_url": api_url,
            "dashboard_url": dashboard_url,
        }
    finally:
        for proc in (dashboard_proc, api_proc):
            if proc is None or proc.poll() is not None:
                continue
            proc.terminate()
            try:
                proc.wait(timeout=3.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                # Reap the child even after escalation; do not leave zombies.
                proc.wait()


def main() -> None:
    print("=== PySRMKit + Next.js Reproducible Integration Runner ===")
    print("[1/3] Ensuring PostgreSQL databases, Alembic migrations, and seeds are ready...")
    bootstrap()

    print("[2/3] Starting FastAPI and Next.js services...")
    with run_integration_stack() as urls:
        print("[3/3] Services operational!")
        print(f"  - Next.js Dashboard: {urls['dashboard_url']}")
        print(f"  - Suppliers View:    {urls['dashboard_url']}/dashboard/suppliers")
        print(f"  - PySRMKit API:      {urls['api_url']}")
        print(f"  - OpenAPI Docs:      {urls['api_url']}/docs")
        print("\nCredentials: user@nextmail.com / 123456")
        print("\nPress Ctrl+C to stop both services gracefully.")

        # Wait for interrupt
        stop_event = False

        def _handle_signal(_signum: int, _frame: object) -> None:
            nonlocal stop_event
            stop_event = True

        signal.signal(signal.SIGINT, _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)

        while not stop_event:
            time.sleep(0.5)

    print("\nServices terminated cleanly.")


if __name__ == "__main__":
    main()
