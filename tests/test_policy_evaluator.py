from deepface_security_framework.config.schema import EmotionConfig
from deepface_security_framework.policy.evaluator import evaluate_emotion_policy


def test_policy_denies_when_weighted_score_exceeds_threshold() -> None:
    config = EmotionConfig(
        blocked_emotions=["angry", "fear"],
        weights={"angry": 1.0, "fear": 0.8},
        threshold=0.7,
    )
    decision = evaluate_emotion_policy({"angry": 0.75, "fear": 0.2}, config)
    assert not decision.passed
    assert decision.top_blocked_emotion == "angry"


def test_policy_allows_when_scores_below_threshold() -> None:
    config = EmotionConfig(blocked_emotions=["angry"], threshold=0.7)
    decision = evaluate_emotion_policy({"angry": 0.3}, config)
    assert decision.passed
