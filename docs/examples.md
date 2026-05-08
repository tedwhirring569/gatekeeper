# Integration Examples

This framework is intentionally generic.  
After `authorize_access()` passes, your application can unlock any protected operation.

## Example: Door Access Service

- Protected action: trigger smart-lock controller API.
- Deny policy: identity mismatch or blocked emotional state.
- Result: no unlock event is sent unless both checks pass.

## Example: Single Image vs Admin Folder Identity Sources

- Single reference image mode:
  - `identity.reference_image_path = "C:/secure/operator.png"`
  - compares live camera face against that one file.
- Admin pool folder mode:
  - `identity.admin_faces_dir = "C:/secure/admin_faces"`
  - recursively scans all supported images in folder/subfolders and matches against live camera feed.

## Example: Privileged Database Session

- Protected action: issue temporary database credentials.
- Deny policy: risky emotional state blocks session token issuance.
- Result: audit trail records each denied or granted attempt.

## Example: Internal Tool or Microservice

- Protected action: call a high-impact admin endpoint.
- Deny policy: failed 2/2 gate prevents endpoint invocation.
- Result: only stable, verified operators can invoke critical controls.

## Example: Financial or Legal Document Signing

- Protected action: release signing key or approval workflow stage.
- Deny policy: if emotional risk score exceeds threshold, signing is blocked.
- Result: helps reduce coerced or emotionally unstable approvals.

## Example: Optional AI Gateway (Reference Only)

AI use is optional and not the primary purpose of this framework.

If authorization passes, you can call local or cloud inference services in your own application layer:

1. `passed, reason = await gateway.authorize_access()`
2. If `passed` is true, invoke your inference adapter.
3. If false, return the deny reason and log incident handling.

This keeps security logic separated from model-provider implementation.

## Example: `authorize_and_execute()` (Code)

```python
import asyncio

from deepface_security_framework.config.schema import AppConfig
from deepface_security_framework.gateway import SecurityGateway


async def open_restricted_valve() -> str:
    # Replace with your real protected action.
    # Example targets: door controller, key vault, privileged API, signing workflow.
    return "Valve control action completed."


async def main() -> None:
    config = AppConfig()
    config.resource.resource_name = "plant_valve_control"
    config.identity.reference_image_path = "C:/secure/authorized_operator.jpg"
    config.identity.frames_per_check = 5
    config.identity.min_matches_required = 2
    config.identity.distance_threshold = 0.9
    config.emotion.blocked_emotions = ["angry", "fear"]
    config.emotion.threshold = 0.8
    config.emotion.frames_per_batch = 3
    config.emotion.max_batches = 2

    gateway = SecurityGateway.build(config)
    passed, message = await gateway.authorize_and_execute(open_restricted_valve)

    if passed:
        print("ACCESS GRANTED:", message)
    else:
        print("ACCESS DENIED:", message)


if __name__ == "__main__":
    asyncio.run(main())
```
