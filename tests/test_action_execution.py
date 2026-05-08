from __future__ import annotations

import pytest

from deepface_security_framework.config.schema import AppConfig
from deepface_security_framework.gateway import SecurityGateway


@pytest.mark.asyncio
async def test_authorize_and_execute_runs_action_when_authorized(monkeypatch) -> None:
    cfg = AppConfig()
    gateway = SecurityGateway(cfg)

    monkeypatch.setattr(gateway, "authorize_access", lambda: _async_return((True, "ok")))

    async def action() -> str:
        return "protected_action_completed"

    passed, output = await gateway.authorize_and_execute(action)
    assert passed
    assert output == "protected_action_completed"


async def _async_return(value):
    return value
