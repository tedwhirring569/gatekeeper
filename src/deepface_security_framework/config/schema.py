from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class IdentityConfig(BaseModel):
    reference_image_path: str | None = None
    admin_faces_dir: str | None = None
    model_name: str = "VGG-Face"
    detector_backend: str = "opencv"
    distance_threshold: float = 0.68
    frames_per_check: int = 5
    min_matches_required: int = 3

    def has_identity_source(self) -> bool:
        return bool(self.reference_image_path or self.admin_faces_dir)


class EmotionConfig(BaseModel):
    blocked_emotions: list[str] = Field(default_factory=lambda: ["angry", "fear"])
    weights: dict[str, float] = Field(default_factory=dict)
    threshold: float = 0.80
    smoothing_window: int = 3
    frames_per_batch: int = 5
    max_batches: int = 3
    supported_emotions: list[str] = Field(
        default_factory=lambda: ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
    )
    show_camera_window: bool = False


class ResourceConfig(BaseModel):
    resource_name: str = "mission_critical_gateway"
    action_timeout_seconds: int = 30


class AppConfig(BaseModel):
    identity: IdentityConfig = Field(default_factory=IdentityConfig)
    emotion: EmotionConfig = Field(default_factory=EmotionConfig)
    resource: ResourceConfig = Field(default_factory=ResourceConfig)
    cooldown_seconds: int = 2
    audit_log_path: str = "logs/security_audit.jsonl"


def resolve_path(path_like: str | None) -> Path | None:
    if not path_like:
        return None
    return Path(path_like).expanduser().resolve()
