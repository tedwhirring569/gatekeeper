from __future__ import annotations

import asyncio
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt

from deepface_security_framework.config.schema import AppConfig
from deepface_security_framework.gateway import SecurityGateway

console = Console()
app = typer.Typer(add_completion=False)


def _clean_input_path(value: str) -> str:
    return value.strip().strip('"').strip("'")


def _normalize_emotion_label(value: str) -> str:
    aliases = {
        "anger": "angry",
    }
    normalized = value.strip().lower()
    return aliases.get(normalized, normalized)


def _apply_ideal_defaults(config: AppConfig) -> None:
    # Fast production profile: balances speed and stability for everyday use.
    config.identity.frames_per_check = 5
    config.identity.min_matches_required = 2
    config.identity.distance_threshold = 0.90
    config.emotion.blocked_emotions = ["angry", "fear"]
    config.emotion.weights = {"angry": 1.0, "fear": 1.0}
    config.emotion.threshold = 0.80
    config.emotion.frames_per_batch = 3
    config.emotion.max_batches = 2
    config.emotion.show_camera_window = True


def load_or_create_config(path: Path) -> AppConfig:
    if not path.exists():
        config = AppConfig()
        path.write_text(yaml.safe_dump(config.model_dump()), encoding="utf-8")
        return config
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return AppConfig.model_validate(raw)


def save_config(path: Path, config: AppConfig) -> None:
    path.write_text(yaml.safe_dump(config.model_dump()), encoding="utf-8")


@app.command()
def run(config_path: str = "config.yaml") -> None:
    config_file = Path(config_path)
    config = load_or_create_config(config_file)

    console.print(
        Panel(
            "[#d8f3dc]DeepFace Security Framework[/#d8f3dc]\n"
            "[#c7d2fe]Mission-Critical Access Gate[/#c7d2fe]",
            subtitle="[#fbcfe8]Biometric + Emotional Authorization[/#fbcfe8]",
        )
    )
    console.print("[#bfdbfe]Step 1/2[/#bfdbfe] Identity source configuration")
    console.print("Fill one source (reference image or admin folder). You do not need both.")
    ref_path = Prompt.ask(
        "Reference image path (single file: .jpg/.jpeg/.png/.webp/.bmp; leave blank to use admin pool folder)",
        default=config.identity.reference_image_path or "",
        show_default=False,
    )
    config.identity.reference_image_path = _clean_input_path(ref_path) or None
    admin_dir = Prompt.ask(
        "Admin faces directory (folder scan, nested files included: .jpg/.jpeg/.png/.webp/.bmp)",
        default=config.identity.admin_faces_dir or "",
        show_default=False,
    )
    config.identity.admin_faces_dir = _clean_input_path(admin_dir) or None
    console.print("[#bfdbfe]Step 2/2[/#bfdbfe] Advanced configuration")
    advanced = Confirm.ask("Customize advanced identity/emotion parameters?", default=False)
    if not advanced:
        _apply_ideal_defaults(config)
    else:
        console.print("[#bfdbfe]Advanced: Identity tuning[/#bfdbfe]")
        config.identity.frames_per_check = IntPrompt.ask(
            "Identity frames per check (multi-frame verification)",
            default=config.identity.frames_per_check,
        )
        config.identity.min_matches_required = IntPrompt.ask(
            "Minimum identity matches required",
            default=config.identity.min_matches_required,
        )
        config.identity.distance_threshold = FloatPrompt.ask(
            "Identity distance threshold (higher is more tolerant, lower is stricter)",
            default=config.identity.distance_threshold,
        )
        console.print("[#bfdbfe]Advanced: Emotion policy[/#bfdbfe]")
        console.print(
            f"Supported emotions: [#fde68a]{', '.join(config.emotion.supported_emotions)}[/#fde68a]"
        )
        blocked = Prompt.ask(
            "Blocked emotions (comma separated; these trigger denial when confidence is high)",
            default=",".join(config.emotion.blocked_emotions),
        )
        parsed_blocked = [_normalize_emotion_label(x) for x in blocked.split(",") if x.strip()]
        if parsed_blocked:
            config.emotion.blocked_emotions = parsed_blocked
        config.emotion.threshold = FloatPrompt.ask(
            "Confidence threshold (0.0-1.0). Example: 0.8 means 80% confidence required.",
            default=config.emotion.threshold,
        )
        console.print("[#bfdbfe]Advanced: Sampling controls[/#bfdbfe]")
        config.emotion.frames_per_batch = IntPrompt.ask(
            "Frames per batch (emotion voting window)",
            default=config.emotion.frames_per_batch,
        )
        config.emotion.max_batches = IntPrompt.ask(
            "Maximum batch attempts before timeout",
            default=config.emotion.max_batches,
        )
        config.emotion.show_camera_window = Confirm.ask(
            "Open live camera window with face map and emotion tags?",
            default=config.emotion.show_camera_window,
        )
        resource_name = Prompt.ask(
            "Protected resource name (optional)",
            default="",
            show_default=False,
        ).strip()
        if resource_name:
            config.resource.resource_name = resource_name

    console.print("[#bfdbfe]Running authorization[/#bfdbfe]")
    save_config(config_file, config)

    gateway = SecurityGateway.build(config)
    try:
        with console.status("[#c4b5fd]Running biometric and emotional authorization...[/#c4b5fd]"):
            passed, output = asyncio.run(gateway.authorize_access())
    except Exception as exc:
        console.print(
            "[#fda4af]Execution failed.[/#fda4af] "
            "If dependencies are missing, activate .venv and install requirements.\n"
            f"Details: {exc}"
        )
        raise typer.Exit(code=1) from exc
    if passed:
        console.print(f"[#86efac]ACCESS GRANTED[/#86efac]\n{output}")
    else:
        console.print(f"[#fda4af]ACCESS DENIED[/#fda4af]\n{output}")


def main() -> None:
    app()
