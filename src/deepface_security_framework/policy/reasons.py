from __future__ import annotations


def identity_reason(identity_ok: bool, details: dict) -> str:
    if identity_ok:
        return "Identity verification passed."
    reason = details.get("reason", "identity_verification_failed")
    if reason == "no_admin_match":
        return "Access denied: requesting user did not match any admin face."
    if reason == "missing_reference_image":
        return "Access denied: reference image is not configured."
    if reason == "invalid_reference_image_format":
        return "Access denied: reference image format is unsupported."
    if reason == "reference_image_unreadable":
        return "Access denied: reference image file could not be read."
    if reason == "reference_no_match":
        distance = details.get("distance")
        threshold = details.get("threshold")
        if distance is not None and threshold is not None:
            return (
                "Access denied: live face did not match reference image "
                f"(distance={float(distance):.4f}, threshold={float(threshold):.4f})."
            )
        return "Access denied: live face did not match reference image."
    if reason == "identity_consensus_failed":
        matches = details.get("matches")
        required = details.get("required")
        return (
            "Access denied: identity consensus failed across multiple frames "
            f"(matches={matches}, required={required})."
        )
    if reason == "admin_pool_not_found":
        return "Access denied: admin face pool path does not exist."
    if reason == "admin_pool_not_directory":
        return "Access denied: admin face pool path is not a directory."
    return f"Access denied: identity verification failed ({reason})."


def emotion_reason(emotion_ok: bool, top_emotion: str | None, score: float, threshold: float) -> str:
    if emotion_ok:
        return "Emotion policy passed."
    if top_emotion:
        return (
            f"Access denied: elevated risk emotion '{top_emotion}' detected "
            f"(score={score:.2f}, threshold={threshold:.2f}). "
            "Please normalize emotional state and retry."
        )
    return "Access denied: emotion policy failed."
