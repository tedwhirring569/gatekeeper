from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from deepface_security_framework.config.schema import IdentityConfig

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _write_temp_frame(frame) -> Path:
    temp_dir = Path(".dfs_tmp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = temp_dir / "live_frame.jpg"
    cv2.imwrite(str(tmp_path), frame)
    return tmp_path


def _load_image_any_path(path: Path):
    # Standard OpenCV path read first.
    image = cv2.imread(str(path))
    if image is not None:
        return image
    # Fallback for Windows/Unicode path handling.
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        if data.size == 0:
            return None
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    except Exception:
        return None


def _iter_image_files(directory: Path):
    for image_path in directory.rglob("*"):
        if image_path.is_file() and image_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
            yield image_path


def verify_reference(frame, config: IdentityConfig) -> tuple[bool, dict]:
    try:
        from deepface import DeepFace
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "DeepFace is not installed in this environment. Activate .venv and run: "
            "python -m pip install -r requirements.txt"
        ) from exc

    if not config.reference_image_path:
        return False, {"reason": "missing_reference_image"}
    if Path(config.reference_image_path).suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        return False, {"reason": "invalid_reference_image_format"}

    reference_path = Path(config.reference_image_path)
    reference_img = _load_image_any_path(reference_path)
    if reference_img is None:
        return False, {"reason": "reference_image_unreadable"}

    result = DeepFace.verify(
        img1_path=frame,
        img2_path=reference_img,
        model_name=config.model_name,
        detector_backend=config.detector_backend,
        enforce_detection=False,
    )
    distance = float(result.get("distance", 1.0))
    threshold = float(config.distance_threshold)
    verified = distance <= threshold
    return verified, {"distance": distance, "threshold": threshold, "source": "reference"}


def verify_admin_pool(frame, config: IdentityConfig) -> tuple[bool, dict]:
    try:
        from deepface import DeepFace
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "DeepFace is not installed in this environment. Activate .venv and run: "
            "python -m pip install -r requirements.txt"
        ) from exc

    if not config.admin_faces_dir:
        return False, {"reason": "missing_admin_pool"}

    admin_dir = Path(config.admin_faces_dir)
    if not admin_dir.exists():
        return False, {"reason": "admin_pool_not_found"}
    if not admin_dir.is_dir():
        return False, {"reason": "admin_pool_not_directory"}

    matches: list[dict] = []
    for image_path in _iter_image_files(admin_dir):
        admin_img = _load_image_any_path(image_path)
        if admin_img is None:
            continue
        result = DeepFace.verify(
            img1_path=frame,
            img2_path=admin_img,
            model_name=config.model_name,
            detector_backend=config.detector_backend,
            enforce_detection=False,
        )
        distance = float(result.get("distance", 1.0))
        threshold = float(config.distance_threshold)
        if distance <= threshold:
            matches.append(
                {
                    "path": str(image_path),
                    "distance": distance,
                    "threshold": threshold,
                }
            )

    if matches:
        best = sorted(matches, key=lambda x: x["distance"])[0]
        return True, {"source": "admin_pool", "match": best}

    return False, {"reason": "no_admin_match", "source": "admin_pool"}


def verify_identity(frame, config: IdentityConfig) -> tuple[bool, dict]:
    if config.reference_image_path:
        matched, details = verify_reference(frame, config)
        if matched:
            return True, details
        details = dict(details)
        details["reason"] = details.get("reason", "reference_no_match")
        return False, details

    if config.admin_faces_dir:
        return verify_admin_pool(frame, config)

    return False, {"reason": "no_identity_sources_configured"}
