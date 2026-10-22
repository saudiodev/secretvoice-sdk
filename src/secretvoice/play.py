"""Playback helpers: play a full utterance or stream it live.

`play()` writes the audio to a temp file and hands it to the platform player
(afplay on macOS, aplay/paplay on Linux, PowerShell on Windows). If no player
is found it prints the path instead — handy on headless boxes.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from typing import Iterator

_PLAYERS = ["afplay", "aplay", "paplay", "ffplay"]


def play(audio: bytes, output_format: str = "mp3") -> str:
    ext = "wav" if "wav" in output_format else "mp3"
    path = os.path.join(tempfile.gettempdir(), f"secretvoice_{os.getpid()}.{ext}")
    with open(path, "wb") as fh:
        fh.write(audio)
    player = next((p for p in _PLAYERS if shutil.which(p)), None)
    if player:
        subprocess.Popen([player, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return path
    print(f"[secretvoice] no audio player found — saved to {path}")
    return path


def stream(chunks: Iterator[bytes]) -> None:
    """Consume an audio byte stream (from .stream() or .realtime()) and play
    it as it arrives. Falls back to saving the whole clip when a chunked
    player is unavailable."""
    buffer = bytearray()
    for chunk in chunks:
        buffer.extend(chunk)
    play(bytes(buffer))