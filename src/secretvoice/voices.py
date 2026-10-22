"""Voices: list the full roster, inspect one, or fetch the preview audio."""

from __future__ import annotations

from typing import List, Optional

from secretvoice.types import Voice, VoiceSettings


class Voices:
    def __init__(self, client):
        self._client = client

    def list(self) -> List[Voice]:
        data = self._client.request("GET", "/v1/voices").json()
        return [Voice.from_dict(v) for v in data.get("voices", [])]

    def get(self, voice_id: str) -> Voice:
        data = self._client.request("GET", f"/v1/voices/{voice_id}").json()
        return Voice.from_dict(data)

    def preview(self, voice_id: str) -> bytes:
        """Fetch the audition clip for a voice as audio bytes."""
        return self._client.request("GET", f"/v1/voices/{voice_id}/preview.mp3").content

    def settings(self, voice_id: str) -> VoiceSettings:
        data = self._client.request("GET", f"/v1/voices/{voice_id}/settings").json()
        return VoiceSettings.from_dict(data)


class AsyncVoices:
    def __init__(self, client):
        self._client = client

    async def list(self) -> List[Voice]:
        data = (await self._client.request("GET", "/v1/voices")).json()
        return [Voice.from_dict(v) for v in data.get("voices", [])]

    async def get(self, voice_id: str) -> Voice:
        data = (await self._client.request("GET", f"/v1/voices/{voice_id}")).json()
        return Voice.from_dict(data)

    async def preview(self, voice_id: str) -> bytes:
        return (await self._client.request("GET", f"/v1/voices/{voice_id}/preview.mp3")).content

    async def settings(self, voice_id: str) -> VoiceSettings:
        data = (await self._client.request("GET", f"/v1/voices/{voice_id}/settings")).json()
        return VoiceSettings.from_dict(data)