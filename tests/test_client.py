"""Unit tests using an httpx MockTransport — no network required."""

from __future__ import annotations

import httpx
import pytest

from secretvoice.client import SecretVoiceClient
from secretvoice.errors import AuthenticationError, NotFoundError


def _client(handler):
    transport = httpx.MockTransport(handler)
    return SecretVoiceClient(
        api_key="test-key", client=httpx.Client(transport=transport)
    )


def test_convert_returns_bytes():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/text-to-speech/velvet"
        assert request.headers["xi-api-key"] == "test-key"
        assert request.url.params["output_format"] == "mp3_44100_128"
        body = request.read().decode()
        assert '"text"' in body and '"model_id"' in body
        return httpx.Response(200, content=b"\x00\x01AUDIO")

    client = _client(handler)
    audio = client.text_to_speech.convert("hi", voice_id="velvet")
    assert audio == b"\x00\x01AUDIO"
    client.close()


def test_similarity_boost_translated():
    """The API 500s on `similarity_boost` for many values — we must send
    `similarity` instead."""

    def handler(request: httpx.Request) -> httpx.Response:
        import json

        body = json.loads(request.read())
        settings = body["voice_settings"]
        assert "similarity_boost" not in settings
        assert settings["similarity"] == 0.7
        return httpx.Response(200, content=b"AUDIO")

    client = _client(handler)
    client.text_to_speech.convert(
        "hi", voice_id="velvet",
        voice_settings={"stability": 0.4, "similarity_boost": 0.7},
    )
    client.close()


def test_voices_list_parses():
    payload = {
        "voices": [
            {"voice_id": "velvet", "name": "Velvet", "category": "premade",
             "labels": {"gender": "female", "style": "rich"}},
            {"voice_id": "blaze", "name": "Blaze", "category": "premade",
             "labels": {"gender": "male"}},
        ]
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    client = _client(handler)
    voices = client.voices.list()
    assert len(voices) == 2
    assert voices[0].voice_id == "velvet"
    assert voices[1].labels["gender"] == "male"
    client.close()


def test_error_mapping():
    def handler(request: httpx.Request) -> httpx.Response:
        if "/v1/voices/" in request.url.path and "not-found" in request.url.path:
            return httpx.Response(404, json={"detail": "voice not found"})
        return httpx.Response(401, json={"detail": "Invalid API key"})

    client = _client(handler)
    with pytest.raises(NotFoundError):
        client.voices.get("not-found")
    with pytest.raises(AuthenticationError):
        client.account.user()
    client.close()