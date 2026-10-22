"""Typed responses for the SecretVoice API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class VoiceSettings:
    stability: Optional[float] = None
    similarity: Optional[float] = None
    style: Optional[float] = None
    speed: Optional[float] = None
    use_speaker_boost: Optional[bool] = None

    def to_dict(self) -> dict:
        out: dict = {}
        for key in ("stability", "similarity", "style", "speed", "use_speaker_boost"):
            val = getattr(self, key)
            if val is not None:
                out[key] = val
        return out

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "VoiceSettings":
        data = data or {}
        # accept the common spelling as well
        similarity = data.get("similarity", data.get("similarity_boost"))
        return cls(
            stability=data.get("stability"),
            similarity=similarity,
            style=data.get("style"),
            speed=data.get("speed"),
            use_speaker_boost=data.get("use_speaker_boost"),
        )


@dataclass
class Voice:
    voice_id: str
    name: Optional[str] = None
    category: Optional[str] = None
    labels: Dict[str, Any] = field(default_factory=dict)
    preview_url: Optional[str] = None
    settings: Optional[VoiceSettings] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Voice":
        return cls(
            voice_id=data.get("voice_id", ""),
            name=data.get("name"),
            category=data.get("category"),
            labels=data.get("labels") or {},
            preview_url=data.get("preview_url"),
            settings=VoiceSettings.from_dict(data.get("settings")),
        )


@dataclass
class Model:
    model_id: str
    name: Optional[str] = None
    can_do_text_to_speech: Optional[bool] = None
    can_do_voice_conversion: Optional[bool] = None
    languages: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Model":
        return cls(
            model_id=data.get("model_id", ""),
            name=data.get("name"),
            can_do_text_to_speech=data.get("can_do_text_to_speech"),
            can_do_voice_conversion=data.get("can_do_voice_conversion"),
            languages=list(data.get("languages") or []),
        )


@dataclass
class HistoryItem:
    history_item_id: str
    voice_id: Optional[str] = None
    text: Optional[str] = None
    date_unix: Optional[int] = None
    seconds: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryItem":
        return cls(
            history_item_id=data.get("history_item_id", ""),
            voice_id=data.get("voice_id"),
            text=data.get("text"),
            date_unix=data.get("date_unix"),
            seconds=data.get("seconds"),
        )


@dataclass
class User:
    id: Optional[str] = None
    email: Optional[str] = None
    is_new_user: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data.get("id"),
            email=data.get("email"),
            is_new_user=data.get("is_new_user"),
        )


@dataclass
class Subscription:
    tier: Optional[str] = None
    character_count: Optional[int] = None
    character_limit: Optional[int] = None
    next_character_count_reset_unix: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Subscription":
        return cls(
            tier=data.get("tier"),
            character_count=data.get("character_count"),
            character_limit=data.get("character_limit"),
            next_character_count_reset_unix=data.get("next_character_count_reset_unix"),
        )