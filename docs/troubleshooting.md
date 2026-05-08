# Troubleshooting

## DeepFace or TensorFlow install fails on Python 3.13

Use the fallback profile:

```powershell
py -3.12 -m venv .venv-fallback
.\.venv-fallback\Scripts\Activate.ps1
python -m pip install -r requirements-fallback.txt
```

## Startup failed: DeepFace is not installed

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Startup failed while downloading `vgg_face_weights.h5`

DeepFace attempts to download this file on first identity verification for the default `VGG-Face` model.

Expected destination:

`$env:USERPROFILE\.deepface\weights\vgg_face_weights.h5`

Manual command:

```powershell
curl.exe -L "https://github.com/serengil/deepface_models/releases/download/v1.0/vgg_face_weights.h5" -o "$env:USERPROFILE\.deepface\weights\vgg_face_weights.h5"
```

If command-line download still fails due firewall/proxy/network resets:
- open the same URL in browser,
- download the file manually,
- move it to `$env:USERPROFILE\.deepface\weights\`.

## Camera cannot be opened

- Confirm no other app is locking the webcam.
- Validate camera index in your environment.
- Test with a simple OpenCV capture script.

## Identity check always fails

- Ensure good lighting and frontal face orientation.
- Use higher quality reference/admin images.
- Tune `identity.distance_threshold` and detector backend.
- For faster and more tolerant local matching, use the default non-advanced profile or lower `identity.min_matches_required`.

## Camera appears to lag during identity but not emotion

This is expected in many environments:
- identity phase loads and runs face-verification embeddings (heavier compute),
- emotion phase model may already be warm by then,
- first run after startup is usually the slowest due model initialization.

What helps:
- keep default fast profile (`frames_per_check=5`, `min_matches_required=2`),
- avoid high identity frame counts unless needed,
- keep camera resolution moderate and lighting stable.

## `Exception while processing img2_path`

This typically means DeepFace/OpenCV could not read the reference/admin source image.

Common causes:
- path contains Unicode characters and OpenCV default file read fails on your environment,
- OneDrive sync state/permissions,
- unsupported/corrupted image file.

What to do:
- Use supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`.
- Confirm image opens normally in local image viewer.
- Prefer local ASCII-only path if issue persists.
- Keep using latest framework version (includes Unicode-safe image read fallback).

## Emotion gate too strict

- Reduce `emotion.threshold`.
- Adjust `emotion.weights`.
- Increase smoothing window to reduce frame-level spikes.
- Increase `emotion.frames_per_batch` and/or `emotion.max_batches` for more stable voting.

## Authorized action fails after access granted

- Verify your protected action callback/service is reachable.
- Increase `resource.action_timeout_seconds` for long-running operations.
- Confirm your action execution path handles authorized context correctly.

## Camera window not visible

- Set `emotion.show_camera_window: true`.
- Ensure no remote/headless session is blocking OpenCV windows.
- Close other apps currently locking camera output.
- On supported platforms, the app sets the window as top-most, but OS/window manager behavior can still vary.
