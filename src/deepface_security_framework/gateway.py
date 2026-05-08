from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from pathlib import Path

import cv2

from deepface_security_framework.config.schema import AppConfig
from deepface_security_framework.policy.evaluator import evaluate_emotion_policy
from deepface_security_framework.policy.reasons import emotion_reason, identity_reason
from deepface_security_framework.ui.overlay import draw_overlay
from deepface_security_framework.vision.camera import CameraStream
from deepface_security_framework.vision.emotion import EmotionAnalyzer
from deepface_security_framework.vision.identity import verify_identity


class SecurityGateway:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.emotion_analyzer = EmotionAnalyzer(config.emotion)
        self.camera = CameraStream()
        self._window_initialized = False

    @classmethod
    def build(cls, config: AppConfig) -> "SecurityGateway":
        return cls(config=config)

    async def authorize_access(self) -> tuple[bool, str]:
        window_name = "DeepFace Security Live View"
        self.camera.open()
        try:
            if self.config.emotion.show_camera_window:
                initial_frame = self.camera.read()
                self._ensure_window_ready(window_name)
                warmup = draw_overlay(
                    initial_frame.copy(),
                    dominant_emotion=None,
                    dominant_confidence=0.0,
                    risk_score=0.0,
                    threshold=self.config.emotion.threshold,
                    status="Initializing identity model",
                    scores=None,
                    batch_idx=0,
                    max_batches=max(1, self.config.identity.frames_per_check),
                )
                cv2.imshow(window_name, warmup)
                cv2.waitKey(1)

            try:
                identity_ok, identity_details = self._run_identity_consensus(window_name)
            except RuntimeError as exc:
                reason = f"Startup failed: {exc}"
                self._audit("deny", reason, {"phase": "identity_bootstrap"})
                return False, reason

            if not identity_ok:
                reason = identity_reason(identity_ok, identity_details)
                self._audit("deny", reason, {"identity": identity_details})
                return False, (
                    f"Identity check: failed. {reason}\n"
                    "Emotion check: skipped due to identity failure.\n"
                    "Final decision: ACCESS DENIED (1/2 checks failed)."
                )

            for batch_idx in range(1, self.config.emotion.max_batches + 1):
                batch_scores: list[dict[str, float]] = []
                latest = None
                for _ in range(self.config.emotion.frames_per_batch):
                    frame = self.camera.read()
                    try:
                        latest = self.emotion_analyzer.analyze(frame)
                    except RuntimeError as exc:
                        reason = f"Startup failed: {exc}"
                        self._audit("deny", reason, {"phase": "emotion_bootstrap"})
                        return False, reason
                    batch_scores.append(latest["raw_scores"])

                    if self.config.emotion.show_camera_window:
                        self._ensure_window_ready(window_name)
                        live = draw_overlay(
                            frame.copy(),
                            latest["dominant_emotion"],
                            latest["raw_scores"].get(latest["dominant_emotion"] or "", 0.0),
                            0.0,
                            self.config.emotion.threshold,
                            "Analyzing emotional state",
                            latest["raw_scores"],
                            batch_idx=batch_idx,
                            max_batches=self.config.emotion.max_batches,
                        )
                        cv2.imshow(window_name, live)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            reason = "Session cancelled by operator."
                            self._audit("deny", reason, {"phase": "manual_cancel"})
                            return False, reason

                aggregate_scores = self._aggregate_scores(batch_scores)
                dominant = max(aggregate_scores, key=aggregate_scores.get) if aggregate_scores else None
                dominant_conf = aggregate_scores.get(dominant, 0.0) if dominant else 0.0
                decision = evaluate_emotion_policy(aggregate_scores, self.config.emotion)

                if self.config.emotion.show_camera_window:
                    self._ensure_window_ready(window_name)
                    summary = draw_overlay(
                        frame.copy(),
                        dominant,
                        dominant_conf,
                        decision.score,
                        self.config.emotion.threshold,
                        "Batch voting complete",
                        aggregate_scores,
                        batch_idx=batch_idx,
                        max_batches=self.config.emotion.max_batches,
                    )
                    cv2.imshow(window_name, summary)
                    cv2.waitKey(450)

                if dominant_conf >= self.config.emotion.threshold:
                    if not decision.passed:
                        reason = emotion_reason(
                            False,
                            decision.top_blocked_emotion,
                            decision.score,
                            self.config.emotion.threshold,
                        )
                        self._audit(
                            "deny",
                            reason,
                            {
                                "identity": identity_details,
                                "emotion": aggregate_scores,
                                "weighted": decision.details,
                                "batch": batch_idx,
                            },
                        )
                        return False, (
                            f"Identity check: passed ({identity_details.get('matches', '?')}/{identity_details.get('required', '?')} matches).\n"
                            f"Emotion check: failed. {reason}\n"
                            "Final decision: ACCESS DENIED (1/2 checks failed)."
                        )

                    allow_reason = (
                        f"Identity check: passed ({identity_details.get('matches', '?')}/{identity_details.get('required', '?')} matches).\n"
                        f"Emotion check: passed (dominant='{dominant}', confidence={dominant_conf:.2f}).\n"
                        f"Final decision: ACCESS GRANTED to '{self.config.resource.resource_name}' (2/2 checks passed)."
                    )
                    self._audit(
                        "allow",
                        allow_reason,
                        {"identity": identity_details, "emotion": aggregate_scores, "batch": batch_idx},
                    )
                    return True, allow_reason

            timeout_reason = (
                "Unable to establish stable emotional classification within allowed attempts. "
                "Ensure camera is connected, lens is clear, face is visible, and note that masks/deepfakes/spoofing attempts fail policy."
            )
            self._audit("deny", timeout_reason, {"identity": identity_details, "phase": "emotion_timeout"})
            return False, (
                f"Identity check: passed ({identity_details.get('matches', '?')}/{identity_details.get('required', '?')} matches).\n"
                f"Emotion check: failed. {timeout_reason}\n"
                "Final decision: ACCESS DENIED (1/2 checks failed)."
            )
        finally:
            self.camera.close()
            cv2.destroyAllWindows()

    async def authorize_and_execute(
        self,
        action: Callable[[], Awaitable[str]],
    ) -> tuple[bool, str]:
        passed, message = await self.authorize_access()
        if not passed:
            return passed, message
        try:
            action_result = await asyncio.wait_for(
                action(),
                timeout=self.config.resource.action_timeout_seconds,
            )
            return True, action_result
        except asyncio.TimeoutError:
            return False, "Authorized, but protected action timed out."
        except Exception as exc:
            return False, f"Authorized, but protected action failed: {exc}"

    def _audit(self, status: str, reason: str, payload: dict) -> None:
        log_path = Path(self.config.audit_log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "status": status,
            "reason": reason,
            "payload": payload,
        }
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")

    @staticmethod
    def _aggregate_scores(scores_list: list[dict[str, float]]) -> dict[str, float]:
        if not scores_list:
            return {}
        keys = set().union(*scores_list)
        return {k: sum(scores.get(k, 0.0) for scores in scores_list) / len(scores_list) for k in keys}

    def _run_identity_consensus(self, window_name: str) -> tuple[bool, dict]:
        matches = 0
        last_details: dict = {}
        iterations = max(1, self.config.identity.frames_per_check)
        required = max(1, min(self.config.identity.min_matches_required, iterations))

        for idx in range(1, iterations + 1):
            frame = self.camera.read()

            if self.config.emotion.show_camera_window:
                self._ensure_window_ready(window_name)
                status = f"Identity check {idx}/{iterations} | matches={matches}/{required} | scanning"
                overlay = draw_overlay(
                    frame.copy(),
                    dominant_emotion=None,
                    dominant_confidence=0.0,
                    risk_score=0.0,
                    threshold=self.config.emotion.threshold,
                    status=status,
                    scores=None,
                    batch_idx=idx,
                    max_batches=iterations,
                )
                cv2.imshow(window_name, overlay)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    return False, {"reason": "manual_cancel"}

            matched, details = verify_identity(frame, self.config.identity)
            last_details = details
            if matched:
                matches += 1

        if matches >= required:
            return True, {**last_details, "source": "identity_consensus", "matches": matches, "required": required}

        return (
            False,
            {
                **last_details,
                "reason": "identity_consensus_failed",
                "matches": matches,
                "required": required,
            },
        )

    def _ensure_window_ready(self, window_name: str) -> None:
        if not self._window_initialized:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.moveWindow(window_name, 40, 40)
            self._window_initialized = True
        try:
            cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
        except Exception:
            # Some OpenCV backends/platforms do not support this property.
            pass
