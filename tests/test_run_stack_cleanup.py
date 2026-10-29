"""A5-03 failure-path and child process cleanup qualification.

The process lifecycle is isolated from PostgreSQL and Next.js: patches
exercise the actual context-manager orchestration without starting servers.
"""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest
from examples.run_stack import run_integration_stack


def _child() -> MagicMock:
    child = MagicMock()
    child.poll.return_value = None
    child.wait.return_value = 0
    return child


def test_dashboard_spawn_failure_reaps_started_fastapi() -> None:
    api = _child()
    with (
        patch("examples.run_stack.subprocess.Popen", side_effect=[api, OSError("npm unavailable")])
        as spawn,
        pytest.raises(OSError, match="npm unavailable"),
    ):
        with run_integration_stack():
            pytest.fail("context must not yield when dashboard launch fails")

    assert spawn.call_count == 2
    api.terminate.assert_called_once_with()
    api.wait.assert_called_once_with(timeout=3.0)


@pytest.mark.parametrize("failed_service", ("api", "dashboard"))
def test_readiness_failure_cleans_both_children(failed_service: str) -> None:
    api, dashboard = _child(), _child()
    url_ready = [False] if failed_service == "api" else [True, False]
    with (
        patch("examples.run_stack.subprocess.Popen", side_effect=[api, dashboard]),
        patch("examples.run_stack.wait_for_url", side_effect=url_ready) as ready,
        pytest.raises(TimeoutError, match="failed to respond"),
    ):
        with run_integration_stack():
            pytest.fail("startup failure must not yield")

    assert ready.call_count == len(url_ready)
    dashboard.terminate.assert_called_once_with()
    api.terminate.assert_called_once_with()
    dashboard.wait.assert_called_once_with(timeout=3.0)
    api.wait.assert_called_once_with(timeout=3.0)


def test_context_exception_still_reaps_both_children() -> None:
    api, dashboard = _child(), _child()
    with (
        patch("examples.run_stack.subprocess.Popen", side_effect=[api, dashboard]),
        patch("examples.run_stack.wait_for_url", return_value=True),
        pytest.raises(RuntimeError, match="consumer failed"),
    ):
        with run_integration_stack() as urls:
            assert urls["api_url"] == "http://127.0.0.1:8000"
            raise RuntimeError("consumer failed")

    dashboard.terminate.assert_called_once_with()
    api.terminate.assert_called_once_with()
    dashboard.wait.assert_called_once_with(timeout=3.0)
    api.wait.assert_called_once_with(timeout=3.0)


def test_termination_timeout_escalates_and_waits_for_reaping() -> None:
    api, dashboard = _child(), _child()
    dashboard.wait.side_effect = [subprocess.TimeoutExpired(cmd="next", timeout=3.0), 0]
    with (
        patch("examples.run_stack.subprocess.Popen", side_effect=[api, dashboard]),
        patch("examples.run_stack.wait_for_url", return_value=True),
    ):
        with run_integration_stack():
            pass

    dashboard.terminate.assert_called_once_with()
    dashboard.kill.assert_called_once_with()
    assert dashboard.wait.call_count == 2
    dashboard.wait.assert_any_call(timeout=3.0)
    dashboard.wait.assert_any_call()
    api.terminate.assert_called_once_with()
    api.wait.assert_called_once_with(timeout=3.0)


def test_exited_child_does_not_receive_a_signal() -> None:
    api, dashboard = _child(), _child()
    api.poll.return_value = 0
    with (
        patch("examples.run_stack.subprocess.Popen", side_effect=[api, dashboard]),
        patch("examples.run_stack.wait_for_url", return_value=True),
    ):
        with run_integration_stack():
            pass

    api.terminate.assert_not_called()
    dashboard.terminate.assert_called_once_with()
