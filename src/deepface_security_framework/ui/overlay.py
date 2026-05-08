from __future__ import annotations

import cv2


def draw_overlay(
    frame,
    dominant_emotion: str | None,
    dominant_confidence: float,
    risk_score: float,
    threshold: float,
    status: str,
    scores: dict[str, float] | None = None,
    batch_idx: int = 1,
    max_batches: int = 3,
):
    color = (130, 220, 170) if risk_score < threshold else (180, 150, 255)
    cv2.putText(frame, f"Status: {status}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(
        frame,
        f"Emotion: {dominant_emotion or 'unknown'} | conf={dominant_confidence:.2f} | risk={risk_score:.2f}",
        (20, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2,
    )
    cv2.putText(
        frame,
        f"Threshold={threshold:.2f} | Batch {batch_idx}/{max_batches}",
        (20, 92),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (220, 220, 220),
        1,
    )

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(80, 80))
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, "Face map", (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

    if scores:
        bar_y = 130
        for emotion, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)[:4]:
            width = int(200 * max(0.0, min(score, 1.0)))
            cv2.rectangle(frame, (20, bar_y - 12), (20 + width, bar_y), color, -1)
            cv2.putText(
                frame,
                f"{emotion}: {score:.2f}",
                (230, bar_y - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (235, 235, 235),
                1,
            )
            bar_y += 22
    return frame
