from __future__ import annotations

from dataclasses import dataclass

from deepface_security_framework.config.schema import EmotionConfig


@dataclass
class EmotionDecision:
    passed: bool
    score: float
    top_blocked_emotion: str | None
    details: dict[str, float]


def evaluate_emotion_policy(scores: dict[str, float], config: EmotionConfig) -> EmotionDecision:
    weighted: dict[str, float] = {}
    for emotion in config.blocked_emotions:
        confidence = scores.get(emotion, 0.0)
        weight = config.weights.get(emotion, 1.0)
        weighted[emotion] = confidence * weight

    if not weighted:
        return EmotionDecision(True, 0.0, None, {})

    top_emotion = max(weighted, key=weighted.get)
    top_score = weighted[top_emotion]
    passed = top_score < config.threshold
    return EmotionDecision(passed, top_score, top_emotion, weighted)
