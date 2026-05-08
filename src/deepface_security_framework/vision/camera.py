from __future__ import annotations

import cv2
import numpy as np


class CameraStream:
    def __init__(self, camera_index: int = 0) -> None:
        self.camera_index = camera_index
        self.capture: cv2.VideoCapture | None = None

    def open(self) -> None:
        self.capture = cv2.VideoCapture(self.camera_index)
        if not self.capture.isOpened():
            raise RuntimeError("Unable to access camera.")

    def read(self) -> np.ndarray:
        if self.capture is None:
            raise RuntimeError("Camera is not open.")
        ok, frame = self.capture.read()
        if not ok:
            raise RuntimeError("Failed to read camera frame.")
        return frame

    def close(self) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None
