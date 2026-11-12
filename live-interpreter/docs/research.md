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

## 6. Free path: open Qwen models (checked 2026-11-12)

All Apache 2.0, open weights on Hugging Face and ModelScope.

| Model | Released | What it does | Speed notes |
| --- | --- | --- | --- |
| **Qwen3-ASR** 0.6B / 1.7B | 2026-01-29 | Speech-to-text and language ID for 30 languages + 22 Chinese dialects (incl. en, es, ar, fr, de, pt, it, ko, ru, vi, ja, th, id). Streaming and offline in one model. The 1.7B is state of the art among open ASR models per Qwen; the 0.6B trades a little accuracy for speed (average time-to-first-token ~92 ms). `pip install qwen-asr` | MLX port: 30–36× real time on an M5 Pro (soniqo benchmark) |
| **Qwen3.5** small: 0.8B, 2B, 4B, 9B | 2026-03-02 | General LLMs, used here as a prompted text translator. The family covers 201 languages. 9B is the strongest small model; 4B targets 6–8 GB machines | To be measured on the M4 |
| **Qwen3-TTS** 0.6B / 1.7B (Base, CustomVoice, VoiceDesign) | 2026-01 | 10 languages (zh, en, ja, ko, de, fr, ru, pt, es, it; Spanish includes Latin American). VoiceDesign makes voices from a description; Base clones from 3 s of audio; documented "voice design then clone" flow. Streaming, ~97 ms first audio on GPU | Apple Silicon MLX: RTF ~0.55 (M2 Max) to ~0.7–0.8, peak memory ~4–6 GB. CPU only: about 3× slower than real time on a shared 4-vCPU box, ~1.28 RTF on Neoverse-N1-class Arm cores |
| Qwen3.8-LiveTranslate (hosted) | 2026-09-19 | Simultaneous interpretation: 60 languages in, 29 spoken out, keeps the speaker's voice. **API only, no weights** | — |

Earlier generation, for reference: SenseVoice (Alibaba FunAudioLLM) is a fast multilingual ASR model; Qwen3-ASR is the newer, better-covered choice for this project.

## 7. Oracle Cloud (checked 2026-11-12)

- **Always Free Arm (Ampere A1, `VM.Standard.A1.Flex`):** 1,500 OCPU-hours and 9,000 GB-hours a month, which equals **2 OCPUs and 12 GB of memory** always on. Halved from 4 OCPUs / 24 GB in 2026; enforced from 2026-08-18. Usable as 1 or 2 VMs.
- **Watch-outs:** if a tenancy goes over the Always Free A1 limit when a trial ends, **all** A1 instances are disabled (deleted after 30 days), not just the excess. Create the VM at 2 OCPU / 12 GB or less. New A1 VMs can fail with "out of capacity"; idle Always Free VMs can be reclaimed.
- **No GPUs in the free tier.** The cheapest Oracle GPU (`VM.GPU.A10.1`, NVIDIA A10 24 GB) lists at about $2/hour.
- **Fit for this project:** great as the free, always-on public server (Twilio bridge, web rooms, session control). Too slow to run the voice models live on 2 Arm cores. Models run on the Mac mini, reached over a private Tailscale tunnel.

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
- [Qwen3-ASR on GitHub](https://github.com/QwenLM/Qwen3-ASR)
- [Qwen3-ASR open-source announcement (Alibaba Cloud)](https://www.alibabacloud.com/blog/qwen3-asr-%26-qwen3-forcedaligner-is-now-open-sourced-robust-streaming-and-multilingual_602843)
- [Qwen3-ASR technical report (arXiv 2601.21337)](https://arxiv.org/pdf/2601.21337v2)
- [Qwen3.5 small models (NYU Shanghai RITS)](https://rits.shanghai.nyu.edu/ai/qwen-3-5-small-models-9b-parameters-that-beat-120b/)
- [Qwen3.5 family guide (Codersera)](https://codersera.com/blog/qwen-3-5-complete-guide-2026/)
- [Qwen3-TTS model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base)
- [Qwen3-TTS languages (docs)](https://www.mintlify.com/QwenLM/Qwen3-TTS/concepts/languages)
- [Qwen3-TTS repository mirror (README sections incl. "Voice Design then Clone")](https://gitee.com/fmtx/Qwen3-TTS)
- [soniqo: Qwen3-TTS on Apple Silicon](https://soniqo.audio/guides/speak)
- [soniqo: Apple Silicon ASR/TTS benchmarks](https://soniqo.audio/benchmarks)
- [Qwen3-TTS MLX skill (performance table)](https://skills.sh/agiseek/agent-skills/qwen3-tts-mlx)
- [ocdevel: quantized Qwen3-TTS on CPU](https://dev.ocdevel.com/blog/20260711-quantized-cpu-tts)
- [Qwen3.8-LiveTranslate (artiverse)](https://www.artiverse.ca/alibabas-qwen38-livetranslate-targets-faster-real-time-speech-translation/)
- [Oracle docs: Always Free resources](https://docs.oracle.com/iaas/Content/FreeTier/resourceref.htm)
- [terminalbytes: Oracle free tier changes 2026](https://terminalbytes.com/oracle-cloud-free-tier-changes-2026)
- [Linuxiac: Oracle cuts free tier Ampere A1 resources in half](https://linuxiac.com/?p=214114)
- [issoh: Oracle Free Tier at 2 OCPU, trial-end rule, capacity errors (Japanese)](https://www.issoh.co.jp/tech/details/17531/)
- [computeprices: Oracle A10 pricing](https://computeprices.com/providers/oracle/gpus/a10)
- [BrainDetox: running a backend on Oracle Always Free (capacity and idle-reclaim risks, Japanese)](https://braindetox.kr/ja/posts/oracle_always_free_backend_2026.html)
- [ApX: Qwen3.5-2B model page (201-language coverage)](https://apxml.com/zh/models/qwen35-2b)
