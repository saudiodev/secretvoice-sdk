"""SecretVoice Python SDK — expressive, intimate AI text-to-speech.

29 sensual voices, 21 languages, HTTP streaming and realtime WebSocket.
Sync and async clients with a nested, resource-style API:

    from secretvoice.client import SecretVoiceClient

    client = SecretVoiceClient()                      # uses $SECRETVOICE_API_KEY
    audio = client.text_to_speech.convert("Come closer.", voice_id="velvet")
"""

__version__ = "0.1.0"

from secretvoice.client import AsyncSecretVoiceClient, SecretVoiceClient
from secretvoice.errors import (
    SecretVoiceError,
    AuthenticationError,
    InsufficientBalanceError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from secretvoice.types import (
    HistoryItem,
    Model,
    Subscription,
    User,
    Voice,
    VoiceSettings,
)
from secretvoice.play import play, stream

__all__ = [
    "__version__",
    "SecretVoiceClient",
    "AsyncSecretVoiceClient",
    "play",
    "stream",
    "SecretVoiceError",
    "AuthenticationError",
    "InsufficientBalanceError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "Voice",
    "VoiceSettings",
    "Model",
    "HistoryItem",
    "User",
    "Subscription",
]