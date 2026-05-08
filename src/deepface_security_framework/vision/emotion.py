from __future__ import annotations

from collections import deque

from deepface_security_framework.config.schema import EmotionConfig


class EmotionAnalyzer:
    def __init__(self, config: EmotionConfig) -> None:
        self.config = config
        self.history: deque[dict[str, float]] = deque(maxlen=max(1, config.smoothing_window))

    def analyze(self, frame) -> dict:
        try:
            from deepface import DeepFace
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "DeepFace is not installed in this environment. Activate .venv and run: "
                "python -m pip install -r requirements.txt"
            ) from exc

        result = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False, silent=True)
        if isinstance(result, list):
            result = result[0]

        scores = result.get("emotion", {})
        normalized = {k: float(v) / 100.0 for k, v in scores.items()}
        self.history.append(normalized)

        smooth_scores = self._smooth_scores()
        dominant = max(smooth_scores, key=smooth_scores.get) if smooth_scores else None
        return {
            "dominant_emotion": dominant,
            "scores": smooth_scores,
            "raw_scores": normalized,
            "region": result.get("region"),
        }

    def _smooth_scores(self) -> dict[str, float]:
        if not self.history:
            return {}
        keys = set().union(*self.history)
        combined: dict[str, float] = {}
        for key in keys:
            combined[key] = sum(frame.get(key, 0.0) for frame in self.history) / len(self.history)
        return combined
