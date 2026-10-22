"""Basic usage — synthesize a full utterance and save/play it."""

import os

from secretvoice.client import SecretVoiceClient
from secretvoice.play import play

client = SecretVoiceClient(api_key=os.environ.get("SECRETVOICE_API_KEY"))

audio = client.text_to_speech.convert(
    text="Come closer. Let me tell you a secret. Now, just listen to my voice.",
    voice_id="velvet",
    model_id="secret-v1",
    output_format="mp3_44100_128",
)

path = play(audio)
print(f"saved {len(audio)} bytes -> {path}")