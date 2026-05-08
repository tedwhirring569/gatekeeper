# Architecture

## Core Components

- `vision/camera.py`: frame capture.
- `vision/identity.py`: DeepFace verification against single reference or admin pool.
- `vision/emotion.py`: DeepFace emotion extraction + smoothing.
- `policy/evaluator.py`: weighted threshold checks.
- `gateway.py`: 2/2 gate orchestration with multi-frame identity consensus, multi-frame emotion voting, and timeout handling.
- `ui/overlay.py`: live camera overlay with face box, labels, and confidence bars.
- `ui/terminal_menu.py`: 2-step CLI (identity source + optional advanced tuning) and authorization.

## Access Flow

```mermaid
flowchart TD
    request[UserRequest] --> capture[CaptureFrame]
    capture --> identity[VerifyIdentity]
    capture --> emotion[AnalyzeEmotionBatch]
    identity --> identityCheck{IdentityPass}
    emotion --> emotionCheck{EmotionPassOrRetry}
    identityCheck -->|No| denyId[ReturnIdentityDeny]
    emotionCheck -->|No and retries left| emotion
    emotionCheck -->|No and retries exhausted| denyEm[ReturnEmotionTimeoutOrRiskDeny]
    identityCheck -->|Yes| gate[Gate2of2]
    emotionCheck -->|Yes| gate
    gate --> allow[GrantProtectedAccess]
    allow --> audit[AuditEventWrite]
```

## Threat Model Framing

- Biometric identity confirms the requester is enrolled/authorized.
- Emotional analysis adds a situational safety layer for high-risk operations.
- This can reduce risk during coercion, panic, aggression, or other unstable states in mission-critical environments.
