# Configuration

## Main YAML keys

- `identity.reference_image_path`: path to canonical single user image (`.jpg/.jpeg/.png/.webp/.bmp`).
- `identity.admin_faces_dir`: folder of authorized admin images (recursive scan across nested folders).
- `identity.model_name`: DeepFace model for verification.
- `identity.detector_backend`: detector backend.
- `identity.distance_threshold`: identity match tolerance; higher values are more permissive.
- `identity.frames_per_check`: number of frames used for identity consensus.
- `identity.min_matches_required`: minimum positive matches required to pass identity.
- `emotion.blocked_emotions`: list of risky emotions to block.
- `emotion.supported_emotions`: list shown in terminal menu for valid labels.
- `emotion.weights`: per-emotion multipliers.
- `emotion.threshold`: deny when weighted score meets or exceeds this value.
- `emotion.smoothing_window`: moving average length for emotion scores.
- `emotion.frames_per_batch`: number of frames to collect per voting batch.
- `emotion.max_batches`: maximum voting batches before timeout denial.
- `emotion.show_camera_window`: when true, opens live OpenCV overlay window.
- `resource.resource_name`: protected gateway identifier for audit and policy context.
- `resource.action_timeout_seconds`: timeout for optional protected action execution.

## Terminal Input Notes

- `anger` is accepted and normalized to DeepFace label `angry`.
- If blocked emotions input is left blank, previous configured values are preserved.
- Protected resource name is optional in prompt; empty input keeps existing config value.
- Fill one identity source (`reference_image_path` or `admin_faces_dir`). You do not need both.
- Identity threshold and emotion threshold are separate controls.
- Basic flow only asks identity source, then asks whether to open advanced config.
- If advanced config is skipped, tuned defaults are applied:
  - `identity.distance_threshold = 0.90`
  - `identity.frames_per_check = 5`
  - `identity.min_matches_required = 2`
  - `emotion.blocked_emotions = ['angry', 'fear']`
  - `emotion.threshold = 0.80`
  - `emotion.frames_per_batch = 3`
  - `emotion.max_batches = 2`
  - `emotion.show_camera_window = true`

## Environment Variables

No required environment variables are used by the core framework runtime at this time.
