"""Models: list the TTS models the API exposes."""

from __future__ import annotations

from typing import List

from secretvoice.types import Model


class Models:
    def __init__(self, client):
        self._client = client

    def list(self) -> List[Model]:
        data = self._client.request("GET", "/v1/models").json()
        return [Model.from_dict(m) for m in data.get("models", [])]


class AsyncModels:
    def __init__(self, client):
        self._client = client

    async def list(self) -> List[Model]:
        data = (await self._client.request("GET", "/v1/models")).json()
        return [Model.from_dict(m) for m in data.get("models", [])]