from __future__ import annotations

import pytest

from deepface_security_framework.config.schema import AppConfig
from deepface_security_framework.gateway import SecurityGateway


@pytest.mark.asyncio
async def test_gateway_denies_when_identity_fails(monkeypatch) -> None:
    cfg = AppConfig()
    gateway = SecurityGateway(cfg)

    monkeypatch.setattr(gateway.camera, "open", lambda: None)
    monkeypatch.setattr(gateway.camera, "read", lambda: object())
    monkeypatch.setattr(gateway.camera, "close", lambda: None)
    monkeypatch.setattr("deepface_security_framework.gateway.verify_identity", lambda *_: (False, {"reason": "x"}))

    passed, message = await gateway.authorize_access()
    assert not passed
    assert "Access denied" in message


@pytest.mark.asyncio
async def test_gateway_allows_when_checks_pass(monkeypatch) -> None:
    cfg = AppConfig()
    gateway = SecurityGateway(cfg)

    monkeypatch.setattr(gateway.camera, "open", lambda: None)
    monkeypatch.setattr(gateway.camera, "read", lambda: object())
    monkeypatch.setattr(gateway.camera, "close", lambda: None)
    monkeypatch.setattr("deepface_security_framework.gateway.verify_identity", lambda *_: (True, {"source": "ref"}))
    monkeypatch.setattr(
        gateway.emotion_analyzer,
        "analyze",
        lambda *_: {"scores": {"angry": 0.1}, "raw_scores": {"angry": 0.1, "neutral": 0.9}, "dominant_emotion": "neutral"},
    )

    passed, message = await gateway.authorize_access()
    assert passed
    assert "ACCESS GRANTED" in message
