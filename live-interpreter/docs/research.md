# Research notes — Live Interpreter

What was checked before starting, so it doesn't need re-researching. Checked 2026-11-12; recheck anything older than a few months before relying on it (prices and access change).

## 1. What already exists (consumer)

| Product | What it does | Gap for this project |
| --- | --- | --- |
| Google Translate (conversation mode, live translate through headphones) | Two-way conversation on a phone; live speech translation through any headphones, 70+ languages | Phone-in-the-middle; generic voices; no phone-call bridging for any phone |
| Apple Live Translation (AirPods, Phone app, CallKit apps) | Hold both AirPod stems; needs iPhone 15 Pro or newer on iOS 26+. Also works in CallKit VoIP apps | Apple devices only, Apple's voices, short list of language pairs |
| Pixel 10 Voice Translate | Translates phone calls on-device in the speaker's own voice | Pixel 10 only; a handful of languages paired with English |
| Sanas Translate, LiveLingo, Microsoft Translator, DeepL Voice | Real-time conversation apps (Microsoft's runs on web, mobile and desktop; DeepL aims at work meetings and face-to-face talks) | Both people usually need the app or a shared screen; no voice matching |
| ElevenLabs Realtime Translation | Each person hears the other in their language in a natural voice, 90+ languages | Enterprise only (contact centers, carriers) |

**Takeaway:** nobody offers "call any phone, the other person hears you in their language, in a voice like yours" as something an individual can use. That's the gap.

## 2. Phone-call access (the hard constraint)

- **iOS:** there is no public API for a third-party app to get the remote caller's audio during a native cellular call (Apple DTS, Developer Forums). A VoIP app has raw access to all of its own audio.
- **Apple's call translation for VoIP apps:** apps using CallKit can turn on Apple's Live Translation (`CXSetTranslatingCallAction`), but that's the only control; it uses Apple's on-device models and voices.
- **Conclusion:** put a server in the middle. Twilio Programmable Voice with **bidirectional Media Streams** streams each call's audio to our server over WebSockets and lets the server send audio back into the call. One bidirectional stream per call, so a bridged conversation is two calls (two legs). Phone audio is μ-law 8 kHz.
- Reference code: OpenAI's realtime translation cookbook includes a Twilio phone-call demo; Twilio's Code Exchange has a bidirectional translation sample with OpenAI's Realtime API.

## 3. Translation engines

| Engine | Access | Languages | Voice control | Price | Notes |
| --- | --- | --- | --- | --- | --- |
| **OpenAI `gpt-realtime-translate`** (May 7, 2026) | Self-serve API | 70+ in, 13 out (en, es, pt, fr, de, it, ru, zh, ja, ko, hi, id, vi) | None (no voice selection or custom prompting) | $0.034/min | Streams translated audio + transcript deltas while the speaker talks. One target language per session. **v0 choice.** |
| OpenAI `gpt-realtime-whisper` | Self-serve | — | — | $0.017/min | Streaming source-language transcript, for captions |
| **ElevenLabs Realtime Translation** | Enterprise workspaces only | 90+ | Takes a `voice_id`; TTS model options incl. `eleven_v4_turbo` (default), `eleven_flash_v2_5`, `eleven_v3` | Custom | Ideal fit; adapter slot reserved |
| **Soniox** (STT + in-stream translation) | Self-serve | 60+ any-to-any (vendor claim) | Text only, pair with any TTS | ~$0.10–0.12/hr (vendor claim) | Candidate second engine for wider language coverage; benchmark claims come from Soniox's own pages |
| **Kyutai Hibiki-Zero** (open source, MIT) | Self-host | fr, es, pt, de → en only | Voice transfer built in | GPU cost | 3B params; NVIDIA GPU, 8 GB VRAM should work, 12 GB safe. Run with `uvx -p 3.13 hibiki-zero serve` |
| Kyutai Hibiki (original, open source) | Self-host | fr → en | Voice transfer; a guidance setting trades voice closeness against accent strength | — | 1B version runs on-device; Mac demo via `moshi_mlx` |

## 4. Voices

- **ElevenLabs Voice Design API:** create a voice from a description plus `gender`, `age` (young / middle_aged / old), `accent` and `accent_strength`. Each generation returns three options; saving one uses a voice slot on the plan.
- **ElevenLabs streaming TTS:** WebSocket input for text that arrives in pieces; Flash and Turbo models use about 0.5–1 credit per character (Deepgram's write-up).
- **Qwen3-TTS** (open source, Apache 2.0, Jan 2026): 0.6B and 1.7B models, 10 languages, voice design from a text description, 3-second cloning, ~97 ms first audio when streaming. The open-source replacement for ElevenLabs.

## 5. Guessing the speaker's sex and age

- **audeering `wav2vec2-large-robust-24-ft-age-gender`:** estimates age (0–100) and gender (child / female / male) from raw audio. 318M parameters, runs on CPU. License CC-BY-NC-SA 4.0 (non-commercial: fine for a portfolio, replace if it ever becomes a product).
- The accent doesn't need a model in v0: it's the speaker's source language (plus region if set).

## Sources

- [OpenAI: Advancing voice intelligence with new models in the API](https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/)
- [OpenAI: Realtime translation guide](https://developers.openai.com/api/docs/guides/realtime-translation)
- [OpenAI Cookbook: Build live translation apps with gpt-realtime-translate](https://developers.openai.com/cookbook/examples/voice_solutions/realtime_translation_guide)
- [OpenAI: GPT-Realtime-Translate model page](https://developers.openai.com/api/docs/models/gpt-realtime-translate)
- [Pricing summary of the May 2026 OpenAI voice models (NYU Shanghai RITS)](https://rits.shanghai.nyu.edu/ai/openai-launches-gpt-realtime-2-with-gpt-5-class-voice-reasoning/)
- [ElevenLabs: Realtime Translation WebSocket API](https://elevenlabs.io/docs/api-reference/realtime-translation/v-1-translation-realtime)
- [ElevenLabs: Realtime Translation announcement](https://elevenlabs.io/blog/realtime-translation)
- [ElevenLabs: Voice Design](https://elevenlabs.io/docs/eleven-creative/voices/voice-design)
- [ElevenLabs JS SDK: Voice Design parameters](https://tessl.io/registry/tessl/npm-elevenlabs--elevenlabs-js/files/docs/voices/voice-design.md)
- [Deepgram: Is ElevenLabs real-time?](https://deepgram.com/learn/is-elevenlabs-real-time-what-developers-need-to-know)
- [Twilio: Media Streams overview](https://www.twilio.com/docs/voice/media-streams)
- [Twilio Code Exchange: Live translation with OpenAI Realtime API](https://twilio.com/code-exchange/live-translation-openai-realtime-api)
- [Apple Developer Forums: remote caller audio in a cellular call](https://developer.apple.com/forums/thread/848873)
- [Apple Developer Forums: Live Translation in VoIP apps on iOS 26](https://developer.apple.com/forums/thread/795830)
- [3CX: iOS live call translation with CallKit](https://www.3cx.com/blog/releases/ios-live-call-translation/)
- [Android Central: AirPods Pro 3 vs Pixel Buds Pro 2 for live translate](https://www.androidcentral.com/apps-software/ai/airpods-pro-3-vs-google-pixel-buds-pro-2-best-for-live-translate)
- [Google Pixel Help: Voice Translate](https://support.google.com/pixelphone/answer/16477051?hl=en-GB)
- [PhoneArena: Google Translate live translation for any headphones](https://phonearena.com/news/google-is-turning-any-headphone-into-real-time-translator_id176618)
- [Soniox vs OpenAI translation (vendor page)](https://soniox.com/compare-translation/openai)
- [Kyutai: Hibiki announcement](https://kyutai.org/2025/02/10/hibiki.html)
- [Kyutai: Hibiki samples](https://kyutai-hibiki-samples.static.hf.space/)
- [Kyutai: Hibiki-Zero on GitHub](https://github.com/kyutai-labs/hibiki-zero)
- [Hibiki-Zero paper (arXiv 2602.11072)](https://arxiv.org/abs/2602.11072)
- [Qwen3-TTS release overview](https://comfyui-wiki.com/en/news/2026-01-22-alibaba-qwen3-tts-release)
- [audeering age/gender model](https://huggingface.co/audeering/wav2vec2-large-robust-24-ft-age-gender)
