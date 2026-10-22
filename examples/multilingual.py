"""Multilingual — one voice, twenty-one languages."""

import asyncio
import os

from secretvoice.client import SecretVoiceClient

client = SecretVoiceClient(api_key=os.environ.get("SECRETVOICE_API_KEY"))

LINES = [
    ("es", "velvet", "Acércate. Quiero contarte un secreto."),
    ("ja", "whisper", "もっと近くに来て。秘密を教えてあげる。"),
    ("fr", "phoenix", "Approche-toi. Je vais te murmurer un secret."),
]

for lang, voice, text in LINES:
    audio = client.text_to_speech.convert(
        text=text, voice_id=voice, language_code=lang, output_format="mp3_44100_128"
    )
    print(f"[{lang}] {voice}: {len(audio)} bytes")