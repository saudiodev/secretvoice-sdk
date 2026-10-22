<div align="center">

# 🎙️ SecretVoice Python SDK

### Expressive, intimate AI text-to-speech for Python.

**Sensual voices, soft whispers, and intimate audio synthesis.** 29 curated
voices (13 female · 16 male), 21 languages, sub-200ms streaming latency, and a
realtime WebSocket — in a clean, typed, sync **and** async SDK.

```bash
pip install secretvoice
```

</div>

---

## What is SecretVoice?

An AI text-to-speech API **tuned for closeness**: breathy whispers, close-mic
narration, and natural conversational turns. Built for romantic fiction,
interactive audio stories, AI companions, ASMR apps, and immersive character
performance — voices that preserve breath, warmth, and micro-inflections
instead of flattening them into robotic audio.

This SDK wraps the full API: full-utterance synthesis, HTTP chunked streaming,
a realtime WebSocket for live agent turn-taking, voice browsing, history
management, and account/credit tracking.

> **One voice, twenty-one languages.** Pass a `language_code` and the same
> voice speaks it natively — same warmth, same intimacy.

---

## 🎧 Hear it

Real clips generated with this SDK:

**her — sultry & soft**
- velvet — *"Come closer. Let me tell you a secret. Now, just listen to my voice."* → [▶️ listen](https://github.com/saudiodev/secretvoice-sdk/raw/main/demo_audio/velvet-comecloser.mp3)
- whisper — *"There you are. I was starting to miss you... whisper it back to me."* → [▶️ listen](https://github.com/saudiodev/secretvoice-sdk/raw/main/demo_audio/whisper-missing.mp3)
- candy — *"Hey you... I saved a spot for you right here. What are you waiting for?"* → [▶️ listen](https://github.com/saudiodev/secretvoice-sdk/raw/main/demo_audio/candy-intro.mp3)
- angel — *"Rest your head. I will stay awake and watch the stars with you."* → [▶️ listen](https://github.com/saudiodev/secretvoice-sdk/raw/main/demo_audio/angel-stars.mp3)

**him — deep & commanding**
- blaze — *"Come a little closer. I have something to tell you..."* → [▶️ listen](https://github.com/saudiodev/secretvoice-sdk/raw/main/demo_audio/blaze-secret.mp3)
- titan — *"Sit with me. Whatever is on your mind, you can say it here."* → [▶️ listen](https://github.com/saudiodev/secretvoice-sdk/raw/main/demo_audio/titan-sitwithme.mp3)
- professor — *"There is a quiet comfort in your presence. Stay a while."* → [▶️ listen](https://github.com/saudiodev/secretvoice-sdk/raw/main/demo_audio/professor-stay.mp3)

**🌍 multilingual — one voice, many tongues**
- velvet (es) — *"Acércate. Quiero contarte un secreto."* → [▶️ listen](https://github.com/saudiodev/secretvoice-sdk/raw/main/demo_audio/es-velvet-secreto.mp3)
- whisper (ja) — *"もっと近くに来て。秘密を教えてあげる。"* → [▶️ listen](https://github.com/saudiodev/secretvoice-sdk/raw/main/demo_audio/ja-whisper-himitsu.mp3)
- phoenix (fr) — *"Approche-toi. Je vais te murmurer un secret."* → [▶️ listen](https://github.com/saudiodev/secretvoice-sdk/raw/main/demo_audio/fr-phoenix-secret.mp3)

---

## ⚡ Quickstart

```python
from secretvoice.client import SecretVoiceClient
from secretvoice.play import play

client = SecretVoiceClient()               # uses $SECRETVOICE_API_KEY

audio = client.text_to_speech.convert(
    text="Come closer. Let me tell you a secret.",
    voice_id="velvet",
    output_format="mp3_44100_128",
)
play(audio)                                # or: open("voice.mp3","wb").write(audio)
```

Set your key: `export SECRETVOICE_API_KEY=...` (or pass `api_key=`).

---

## 🧩 API at a glance

```python
client = SecretVoiceClient()

# — text to speech
audio = client.text_to_speech.convert(text="...", voice_id="velvet")
for chunk in client.text_to_speech.stream(text="...", voice_id="whisper"):
    ...                                    # HTTP chunked, <200ms TTFB

# — voices
voices = client.voices.list()              # all 29
voice  = client.voices.get("velvet")
preview = client.voices.preview("velvet")  # audition bytes

# — models
models = client.models.list()              # [{secret-v1: 21 languages}]

# — history
items  = client.history.list()
audio  = client.history.audio(item_id)
client.history.delete(item_id)

# — account
user   = client.account.user()
sub    = client.account.subscription()
credits = client.account.credits()         # characters left this cycle
```

## ⚡ Async client

```python
import asyncio
from secretvoice.client import AsyncSecretVoiceClient

async def main():
    async with AsyncSecretVoiceClient() as client:
        audio = await client.text_to_speech.convert("hi there", voice_id="velvet")
        voices = await client.voices.list()

asyncio.run(main())
```

## 🔌 Realtime WebSocket

Stream audio frames live from LLM token output — perfect for AI companions
and interactive voice agents that never break character:

```python
import asyncio
from secretvoice.client import AsyncSecretVoiceClient

async def main():
    async with AsyncSecretVoiceClient() as client:
        async for frame in client.text_to_speech.realtime(
            text=["There you are. ", "I was starting to miss you. "],
            voice_id="velvet",
        ):
            ...  # base64-decoded audio frames, ready for WebRTC/LiveKit

asyncio.run(main())
```

The sync client has a `realtime()` with the same signature for parity.

---

## 🎛️ Voice settings & tuning

```python
audio = client.text_to_speech.convert(
    text="Whisper this to me.",
    voice_id="whisper",
    voice_settings={
        "stability": 0.4,        # 0-1: how consistent the timbre stays
        "similarity_boost": 0.7, # 0-1: how closely it matches the voice
        "style": 0.5,            # 0-1: expressiveness
        "speed": 0.95,           # 0.5-2.0
    },
)
```

> Note: the API accepts `similarity_boost` (and its alias `similarity`) — the
> SDK normalizes either spelling for you, because the verbose field name is
> unreliable server-side for several values.

Output formats: `mp3_*` (22/24/44.1 kHz, 32–192 kbps), `wav_*` (8–44.1 kHz),
`pcm_*` (8–48 kHz), `opus_48000_*`, `ulaw_8000`, `alaw_8000`.

---

## 🌍 Multilingual

All 21 languages: `en, es, de, fr, it, pt, ru, zh, ja, ko, th, id, vi, ms, nl,
pl, et, fi, hi, ta, cs`. Just pass `language_code`:

```python
audio = client.text_to_speech.convert(
    text="もっと近くに来て。秘密を教えてあげる。",
    voice_id="whisper", language_code="ja",
)
```

## 🗣️ The voice catalog

Female: velvet (sultry), whisper (intimate), angel (soft), candy, jade,
dominique, chloe, honey, crystal, diamond, sunny, star, bubbles.
Male: professor (measured), titan (deep), blaze (passionate), phoenix, stone,
duke, ace, chase, rico, rocco, steele, sage, rex, chill, maverick, tender.

Preview them all: `client.voices.list()` → `preview_url`, or
`client.voices.preview(voice_id)`.

---

## 💳 Credits & billing

1 credit = 1 character of speech. Plans (Starter $59/600k, Pro $99/1.2M,
Scale $199/2.5M, Business $299/4M) share the same credit pool; streaming and
realtime are included from Pro up. Check your balance anytime:

```python
client.account.credits()   # -> int
```

---

## 🧪 Examples

`examples/` contains runnable scripts: `basic.py`, `streaming.py`,
`realtime_ws.py`, `multilingual.py` — each reads `$SECRETVOICE_API_KEY`.

## 🛠️ Development

```bash
pip install -e .[dev]    # or: pip install -e .
python -m pytest
```

## 📦 Install

```bash
pip install secretvoice
```

## License

MIT