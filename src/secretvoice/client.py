"""SecretVoice SDK — sync and async clients.

Nested resource-style API:

    client.text_to_speech.convert(text, voice_id) -> bytes
    client.voices.list()                          -> list[Voice]
    client.models.list()                          -> list[Model]
    client.history.list()                         -> list[HistoryItem]
    client.account.subscription()                 -> Subscription

Both clients accept an `api_key` or read $SECRETVOICE_API_KEY, and share the
same transports. The async client additionally exposes the realtime
WebSocket (`text_to_speech.realtime`).
"""

from __future__ import annotations

import os
from typing import Optional

import httpx

from secretvoice.account import Account, AsyncAccount
from secretvoice.errors import SecretVoiceError, error_for_status
from secretvoice.history import AsyncHistory, History
from secretvoice.models import AsyncModels, Models
from secretvoice.tts import AsyncTextToSpeech, TextToSpeech
from secretvoice.voices import AsyncVoices, Voices

DEFAULT_BASE_URL = "https://api.secretvoice.dev"


def _resolve_api_key(api_key: Optional[str]) -> str:
    key = api_key or os.environ.get("SECRETVOICE_API_KEY")
    if not key:
        raise SecretVoiceError(
            "missing API key — pass api_key=... or set $SECRETVOICE_API_KEY"
        )
    return key


class _Base:
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    @property
    def _auth_headers(self) -> dict:
        return {"xi-api-key": self._api_key}


class SecretVoiceClient(_Base):
    """Synchronous SecretVoice client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
        client: Optional[httpx.Client] = None,
    ):
        super().__init__(_resolve_api_key(api_key), base_url)
        self._http = client or httpx.Client(timeout=timeout, follow_redirects=True)
        self.text_to_speech = TextToSpeech(self)
        self.voices = Voices(self)
        self.models = Models(self)
        self.history = History(self)
        self.account = Account(self)
        # convenience aliases
        self.tts = self.text_to_speech

    # -- raw request plumbing (used by resources) --------------------------

    def request(self, method: str, path: str, **kwargs) -> httpx.Response:
        resp = self._http.request(
            method, f"{self._base_url}{path}", headers=self._auth_headers, **kwargs
        )
        if resp.status_code >= 400:
            detail = _detail(resp)
            raise error_for_status(resp.status_code, detail)
        return resp

    def close(self) -> None:
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


class AsyncSecretVoiceClient(_Base):
    """Asynchronous SecretVoice client (also hosts the realtime WebSocket)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
        client: Optional[httpx.AsyncClient] = None,
    ):
        super().__init__(_resolve_api_key(api_key), base_url)
        self._http = client or httpx.AsyncClient(timeout=timeout, follow_redirects=True)
        self.text_to_speech = AsyncTextToSpeech(self)
        self.voices = AsyncVoices(self)
        self.models = AsyncModels(self)
        self.history = AsyncHistory(self)
        self.account = AsyncAccount(self)
        self.tts = self.text_to_speech

    async def request(self, method: str, path: str, **kwargs) -> httpx.Response:
        resp = await self._http.request(
            method, f"{self._base_url}{path}", headers=self._auth_headers, **kwargs
        )
        if resp.status_code >= 400:
            detail = _detail(resp)
            raise error_for_status(resp.status_code, detail)
        return resp

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.close()
        return False


def _detail(resp: httpx.Response) -> str:
    try:
        data = resp.json()
        return str(data.get("detail", data))
    except Exception:
        return resp.text[:300]