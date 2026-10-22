"""Text-to-speech: synchronous synthesis, HTTP streaming, and realtime WS.

API (see secretvoice.dev):
  convert:  POST /v1/text-to-speech/{voice_id}?output_format=...
  stream:   POST /v1/text-to-speech/{voice_id}/stream   (chunked audio)
  realtime: WS  wss://ws.secretvoice.dev/v1/text-to-speech/{voice_id}/stream-input

The realtime session speaks in base64 audio frames; the SDK decodes them to
raw bytes and re-exposes them as an (async) iterator.
"""

from __future__ import annotations

import asyncio
import base64
import json
import queue
import threading
from typing import Any, Dict, Iterator, List, Optional, Union

from secretvoice.errors import WebSocketError
from secretvoice.types import VoiceSettings

DEFAULT_MODEL = "secret-v1"
WS_URL = "wss://ws.secretvoice.dev/v1/text-to-speech/{voice}/stream-input"


def _settings_payload(settings: Optional[Union[dict, VoiceSettings]]) -> Optional[dict]:
    if settings is None:
        return None
    if isinstance(settings, VoiceSettings):
        out = settings.to_dict()
    else:
        out = dict(settings)
    # The API's `similarity_boost` spelling 500s for many values; the
    # `similarity` alias works everywhere. Accept either, send the working one.
    if "similarity_boost" in out and "similarity" not in out:
        out["similarity"] = out.pop("similarity_boost")
    return out or None


class TextToSpeech:
    """Synchronous TTS (convert + HTTP stream; realtime runs the async core)."""

    def __init__(self, client):
        self._client = client

    def convert(
        self,
        text: str,
        voice_id: str,
        model_id: str = DEFAULT_MODEL,
        language_code: Optional[str] = None,
        voice_settings: Optional[Union[dict, VoiceSettings]] = None,
        output_format: str = "mp3_44100_128",
        apply_text_normalization: Optional[str] = None,
    ) -> bytes:
        """Synthesize a full utterance and return the audio bytes."""
        body: Dict[str, Any] = {"text": text, "model_id": model_id}
        if language_code:
            body["language_code"] = language_code
        settings = _settings_payload(voice_settings)
        if settings:
            body["voice_settings"] = settings
        if apply_text_normalization:
            body["apply_text_normalization"] = apply_text_normalization
        resp = self._client.request(
            "POST",
            f"/v1/text-to-speech/{voice_id}",
            params={"output_format": output_format},
            json=body,
        )
        return resp.content

    def stream(
        self,
        text: str,
        voice_id: str,
        model_id: str = DEFAULT_MODEL,
        language_code: Optional[str] = None,
        voice_settings: Optional[Union[dict, VoiceSettings]] = None,
    ) -> Iterator[bytes]:
        """Yield audio chunks as they are generated (HTTP chunked streaming)."""
        body: Dict[str, Any] = {"text": text, "model_id": model_id}
        if language_code:
            body["language_code"] = language_code
        settings = _settings_payload(voice_settings)
        if settings:
            body["voice_settings"] = settings
        with self._client._http.stream(
            "POST",
            f"{self._client._base_url}/v1/text-to-speech/{voice_id}/stream",
            headers=self._client._auth_headers,
            json=body,
        ) as resp:
            if resp.status_code >= 400:
                raise _stream_error(resp)
            for chunk in resp.iter_bytes():
                if chunk:
                    yield chunk

    # -- realtime (sync wrapper around the async core) ---------------------

    def realtime(
        self,
        text: Union[str, List[str]],
        voice_id: str,
        model_id: str = DEFAULT_MODEL,
        language_code: Optional[str] = None,
        voice_settings: Optional[Union[dict, VoiceSettings]] = None,
        flush: bool = True,
    ) -> Iterator[bytes]:
        """Speak `text` (str or list of parts) over the realtime WebSocket,
        yielding audio frames as they arrive. A worker thread runs the async
        core so the sync client gets full realtime parity."""
        parts = [text] if isinstance(text, str) else list(text)
        out: "queue.Queue[Union[bytes, Exception, None]]" = queue.Queue()

        def _worker():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                async def _run():
                    async for frame in self._realtime_async(
                        parts, voice_id, model_id, language_code, voice_settings, flush
                    ):
                        out.put(frame)
                    out.put(None)
                loop.run_until_complete(_run())
                loop.close()
            except Exception as exc:  # surface WS errors to the consumer
                out.put(exc)

        threading.Thread(target=_worker, daemon=True).start()
        while True:
            item = out.get()
            if item is None:
                break
            if isinstance(item, Exception):
                raise item
            yield item

    async def _realtime_async(self, parts, voice_id, model_id, language_code, settings, flush):
        import websockets

        uri = WS_URL.format(voice=voice_id)
        headers = {"xi-api-key": self._client._api_key}
        if language_code:
            uri += f"?language_code={language_code}"
        if settings:
            uri += f"&voice_settings={json.dumps(settings)}"
        async with websockets.connect(uri, additional_headers=headers) as ws:
            # init handshake
            await ws.send(json.dumps({"text": " "}))
            for part in parts:
                await ws.send(json.dumps({"text": part}))
            if flush:
                await ws.send(json.dumps({"flush": True}))
            await ws.send(json.dumps({"text": ""}))  # close input
            while True:
                raw = await ws.recv()
                msg = json.loads(raw)
                if "error" in msg:
                    raise WebSocketError(msg["error"])
                audio = msg.get("audio")
                if audio:
                    yield base64.b64decode(audio)
                if msg.get("isFinal") is True:
                    break


class AsyncTextToSpeech:
    """Async TTS — including the native realtime WebSocket generator."""

    def __init__(self, client):
        self._client = client

    async def convert(self, *args, **kwargs) -> bytes:
        """Synthesize a full utterance and return the audio bytes."""
        return await self._convert_async(*args, **kwargs)

    async def _convert_async(self, text, voice_id, model_id=DEFAULT_MODEL, language_code=None,
                             voice_settings=None, output_format="mp3_44100_128",
                             apply_text_normalization=None) -> bytes:
        body: Dict[str, Any] = {"text": text, "model_id": model_id}
        if language_code:
            body["language_code"] = language_code
        settings = _settings_payload(voice_settings)
        if settings:
            body["voice_settings"] = settings
        if apply_text_normalization:
            body["apply_text_normalization"] = apply_text_normalization
        resp = await self._client.request(
            "POST",
            f"/v1/text-to-speech/{voice_id}",
            params={"output_format": output_format},
            json=body,
        )
        return resp.content

    async def stream(
        self,
        text: str,
        voice_id: str,
        model_id: str = DEFAULT_MODEL,
        language_code: Optional[str] = None,
        voice_settings: Optional[Union[dict, VoiceSettings]] = None,
    ):
        body: Dict[str, Any] = {"text": text, "model_id": model_id}
        if language_code:
            body["language_code"] = language_code
        settings = _settings_payload(voice_settings)
        if settings:
            body["voice_settings"] = settings
        async with self._client._http.stream(
            "POST",
            f"{self._client._base_url}/v1/text-to-speech/{voice_id}/stream",
            headers=self._client._auth_headers,
            json=body,
        ) as resp:
            if resp.status_code >= 400:
                raise _stream_error(resp)
            async for chunk in resp.aiter_bytes():
                if chunk:
                    yield chunk

    async def realtime(
        self,
        text: Union[str, List[str]],
        voice_id: str,
        model_id: str = DEFAULT_MODEL,
        language_code: Optional[str] = None,
        voice_settings: Optional[Union[dict, VoiceSettings]] = None,
        flush: bool = True,
    ):
        """Native async realtime generator over the WebSocket."""
        import websockets

        parts = [text] if isinstance(text, str) else list(text)
        uri = WS_URL.format(voice=voice_id)
        headers = {"xi-api-key": self._client._api_key}
        if language_code:
            uri += f"?language_code={language_code}"
        if settings := _settings_payload(voice_settings):
            uri += f"&voice_settings={json.dumps(settings)}"
        async with websockets.connect(uri, additional_headers=headers) as ws:
            await ws.send(json.dumps({"text": " "}))
            for part in parts:
                await ws.send(json.dumps({"text": part}))
            if flush:
                await ws.send(json.dumps({"flush": True}))
            await ws.send(json.dumps({"text": ""}))
            while True:
                raw = await ws.recv()
                msg = json.loads(raw)
                if "error" in msg:
                    raise WebSocketError(msg["error"])
                audio = msg.get("audio")
                if audio:
                    yield base64.b64decode(audio)
                if msg.get("isFinal") is True:
                    break


def _stream_error(resp) -> Exception:
    from secretvoice.errors import error_for_status

    try:
        detail = str(resp.json().get("detail", ""))
    except Exception:
        detail = ""
    return error_for_status(resp.status_code, detail)