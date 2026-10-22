"""Streaming — yield audio chunks as they are generated (sub-200ms TTFB)."""

import os

from secretvoice.client import SecretVoiceClient

client = SecretVoiceClient(api_key=os.environ.get("SECRETVOICE_API_KEY"))

total = 0
for chunk in client.text_to_speech.stream(
    text="There you are. I was starting to miss you... whisper it back to me.",
    voice_id="whisper",
):
    total += len(chunk)
    print(f"chunk: {len(chunk)} bytes")

print(f"streamed {total} bytes total")