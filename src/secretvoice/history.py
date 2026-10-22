"""History: list past generations, download the audio, or delete items."""

from __future__ import annotations

from typing import List

from secretvoice.types import HistoryItem


class History:
    def __init__(self, client):
        self._client = client

    def list(self, page_size: int = 100) -> List[HistoryItem]:
        data = self._client.request(
            "GET", "/v1/history", params={"page_size": page_size}
        ).json()
        items = data.get("history", [])
        if isinstance(items, dict):  # some responses wrap it
            items = items.get("items", [])
        return [HistoryItem.from_dict(h) for h in items]

    def audio(self, history_item_id: str) -> bytes:
        return self._client.request("GET", f"/v1/history/{history_item_id}").content

    def delete(self, history_item_id: str) -> None:
        self._client.request("DELETE", f"/v1/history/{history_item_id}")


class AsyncHistory:
    def __init__(self, client):
        self._client = client

    async def list(self, page_size: int = 100) -> List[HistoryItem]:
        data = (
            await self._client.request("GET", "/v1/history", params={"page_size": page_size})
        ).json()
        items = data.get("history", [])
        if isinstance(items, dict):
            items = items.get("items", [])
        return [HistoryItem.from_dict(h) for h in items]

    async def audio(self, history_item_id: str) -> bytes:
        return (await self._client.request("GET", f"/v1/history/{history_item_id}")).content

    async def delete(self, history_item_id: str) -> None:
        await self._client.request("DELETE", f"/v1/history/{history_item_id}")