from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

# Reduce TensorFlow / oneDNN startup noise in terminal.
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
warnings.filterwarnings("ignore", message=".*sparse_softmax_cross_entropy.*")

# Allow direct execution from repo root without editable install.
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from deepface_security_framework.ui.terminal_menu import main


if __name__ == "__main__":
    main()
