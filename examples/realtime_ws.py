"""Realtime WebSocket — send text chunks, receive audio frames as they speak.

Run with:  python examples/realtime_ws.py
"""

import asyncio
import os

from secretvoice.client import AsyncSecretVoiceClient


async def main():
    async with AsyncSecretVoiceClient(api_key=os.environ.get("SECRETVOICE_API_KEY")) as client:
        frames = 0
        total = 0
        async for frame in client.text_to_speech.realtime(
            text=[
                "There you are. ",
                "I was starting to miss you. ",
                "Come here... I have a secret for you.",
            ],
            voice_id="velvet",
        ):
            frames += 1
            total += len(frame)
        print(f"realtime done: {frames} frames, {total} bytes")


asyncio.run(main())