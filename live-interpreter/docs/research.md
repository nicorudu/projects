# Research notes — Live Interpreter

What was checked before starting, so it doesn't need re-researching. Checked 2026-11-12, re-checked 2026-11-19 (see §9 for what changed); recheck anything older than a few months before relying on it (prices and access change).

## 1. What already exists (consumer)

| Product | What it does | Gap for this project |
| --- | --- | --- |
| Google Translate (conversation mode, live translate through headphones) | Two-way conversation on a phone; live speech translation through any headphones, 70+ languages | Phone-in-the-middle; generic voices; no phone-call bridging for any phone |
| Apple Live Translation (AirPods, Phone app, CallKit apps) | Hold both AirPod stems; needs iPhone 15 Pro or newer on iOS 26+. Also works in CallKit VoIP apps | Apple devices only, Apple's voices, short list of language pairs |
| Pixel 10 Voice Translate | Translates phone calls on-device in the speaker's own voice | Pixel 10 only; a handful of languages paired with English |
| Sanas Translate, LiveLingo, Microsoft Translator, DeepL Voice | Real-time conversation apps (Microsoft's runs on web, mobile and desktop; DeepL aims at work meetings and face-to-face talks) | Both people usually need the app or a shared screen; no voice matching |
| ElevenLabs Realtime Translation | Each person hears the other in their language in a natural voice, 90+ languages | Enterprise alpha only (contact centers, carriers) |
| Google Translate app / Google Meet with Gemini 3.5 Live Translate | Continuous speech-to-speech translation, 70+ languages | Inside Google's own apps; no phone-call bridge to any phone, no chosen voice |

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
| **ElevenLabs Realtime Translation** | Enterprise alpha (launched 2026-10-21); still not self-serve on 2026-11-19 | 90+ | Takes a `voice_id`; TTS model options incl. `eleven_v4_turbo` (default), `eleven_flash_v2_5`, `eleven_v3` | Custom | Ideal fit; adapter slot reserved |
| **Google Gemini 3.5 Live Translate** (2026-06-09) | Public preview, Gemini Live API and AI Studio | 70+ in and out, 2,000+ pairs, auto-detects the language | Keeps the speaker's intonation, pacing and pitch; voice choice to check | Reported $0.023/min; token-based listings differ and preview pricing can change | Candidate paid engine with wider output coverage than OpenAI. One review says it has no transcript mode, which would cost us captions; check before building on it |
| **Soniox** (STT + in-stream translation) | Self-serve | 60+ any-to-any (vendor claim) | Text only, pair with any TTS | ~$0.10–0.12/hr (vendor claim) | Candidate second engine for wider language coverage; benchmark claims come from Soniox's own pages |
| **Kyutai Hibiki-Zero** (open source, MIT) | Self-host | fr, es, pt, de → en only | Voice transfer built in | GPU cost | 3B params; NVIDIA GPU, 8 GB VRAM should work, 12 GB safe. Run with `uvx -p 3.13 hibiki-zero serve` |
| Kyutai Hibiki (original, open source) | Self-host | fr → en | Voice transfer; a guidance setting trades voice closeness against accent strength | — | 1B version runs on-device; Mac demo via `moshi_mlx` |

## 4. Voices

- **ElevenLabs Voice Design API:** create a voice from a description plus `gender`, `age` (young / middle_aged / old), `accent` and `accent_strength`. Each generation returns three options; saving one uses a voice slot on the plan.
- **ElevenLabs streaming TTS:** WebSocket input for text that arrives in pieces.
  - **Eleven v4 Turbo** (2026-09-28): 90+ languages, about 100 ms median inference and 150 ms to first speech, bidirectional streaming, listed at about $0.04 per minute. The current choice for the paid path.
  - **Flash v2.5:** still the lowest latency (~75 ms) but 32 languages. Fallback.
  - **Eleven v3** (now a previous model): 74 languages, including Urdu, Somali, Swahili, Pashto, Punjabi and Telugu; not Haitian Creole or Hmong.
  - **Voice slots** (saved custom voices): 3 on Free, 10 on Starter ($6/month), 30 on Creator ($22/month).
- **Qwen3-TTS** (open source, Apache 2.0, Jan 2026): 0.6B and 1.7B models, 10 languages, voice design from a text description, 3-second cloning, ~97 ms first audio when streaming. The open-source replacement for ElevenLabs.

## 5. Guessing the speaker's sex and age

- **audeering `wav2vec2-large-robust-24-ft-age-gender`:** estimates age (0–100) and gender (child / female / male) from raw audio. 318M parameters, runs on CPU. License CC-BY-NC-SA 4.0 (non-commercial: fine for a portfolio, replace if it ever becomes a product).
- The accent doesn't need a model in v0: it's the speaker's source language (plus region if set).

## 6. Free path: open Qwen models (checked 2026-11-12)

All Apache 2.0, open weights on Hugging Face and ModelScope.

| Model | Released | What it does | Speed notes |
| --- | --- | --- | --- |
| **Qwen3-ASR** 0.6B / 1.7B | 2026-01-29 | Speech-to-text and language ID for 30 languages + 22 Chinese dialects (incl. en, es, ar, fr, de, pt, it, ko, ru, vi, ja, th, id). Streaming and offline in one model, but streaming needs the vLLM backend (NVIDIA GPUs); the Mac (MLX) ports transcribe finished clips, so the free path works phrase by phrase. The 1.7B is state of the art among open ASR models per Qwen; the 0.6B trades a little accuracy for speed (average time-to-first-token ~92 ms). `pip install qwen-asr` | MLX port: 30–36× real time on an M5 Pro (soniqo benchmark) |
| **Qwen3.5** small: 0.8B, 2B, 4B, 9B | 2026-03-02 | General LLMs, used here as a prompted text translator. The family covers 201 languages. 9B is the strongest small model; 4B targets 6–8 GB machines | To be measured on the M4 |
| **Qwen3-TTS** 0.6B / 1.7B (Base, CustomVoice, VoiceDesign) | 2026-01 | 10 languages (zh, en, ja, ko, de, fr, ru, pt, es, it; Spanish includes Latin American). VoiceDesign makes voices from a description; Base clones from 3 s of audio; documented "voice design then clone" flow. Streaming, ~97 ms first audio on GPU | Apple Silicon MLX: RTF ~0.55 (M2 Max) to ~0.7–0.8, peak memory ~4–6 GB. CPU only: about 3× slower than real time on a shared 4-vCPU box, ~1.28 RTF on Neoverse-N1-class Arm cores |
| Qwen3.8-LiveTranslate (hosted) | 2026-09-19 | Simultaneous interpretation: 60 languages in, 29 spoken out, keeps the speaker's voice. **API only, no weights** | — |

Earlier generation, for reference: SenseVoice (Alibaba FunAudioLLM) is a fast multilingual ASR model; Qwen3-ASR is the newer, better-covered choice for this project.

## 7. Oracle Cloud (checked 2026-11-12)

- **Always Free Arm (Ampere A1, `VM.Standard.A1.Flex`):** 1,500 OCPU-hours and 9,000 GB-hours a month, which equals **2 OCPUs and 12 GB of memory** always on. Halved from 4 OCPUs / 24 GB in 2026; enforced from 2026-08-18. Usable as 1 or 2 VMs.
- **Watch-outs:** if a tenancy goes over the Always Free A1 limit when a trial ends, **all** A1 instances are disabled (deleted after 30 days), not just the excess. Create the VM at 2 OCPU / 12 GB or less. New A1 VMs can fail with "out of capacity"; idle Always Free VMs can be reclaimed.
- **No GPUs in the free tier.** The cheapest Oracle GPU (`VM.GPU.A10.1`, NVIDIA A10 24 GB) lists at about $2/hour.
- **Fit for this project:** great as the free, always-on public server (Twilio bridge, web rooms, session control). Too slow to run the voice models live on 2 Arm cores. Models run on the Mac mini, reached over a private Tailscale tunnel.

## 8. Languages (checked 2026-11-12)

**Most common home languages of US English learners, fall 2021 (NCES Digest table 204.27):** 1 Spanish 4,023,289 · 2 Arabic 130,917 · 3 English 116,771 · 4 Chinese 95,584 · 5 Vietnamese 75,070 · 6 Portuguese 50,205 · 7 Russian 39,403 · 8 Haitian Creole 31,122 · 9 Hmong 30,181 · 10 Urdu 26,567 · 11 Korean 24,270 · 12 French 23,648 · 13 Swahili 21,833 · 14 Somali 19,367 · 15 Tagalog 19,319. Spanish is 76.4% of all English learners. Hindi, Gujarati, Punjabi and Telugu aren't in the top 15. ("English" covers students from multilingual homes.)

**Who covers what:**

| Engine | Role | Launch languages covered | Notable gaps |
| --- | --- | --- | --- |
| Qwen3-ASR (free) | Hears | All 8 (es, ar, zh, vi, pt, ru, hi, fil) | Urdu, Haitian Creole, Hmong, Somali, Swahili not listed |
| Qwen3.5 (free) | Translates text | All 8 (family covers 201 languages) | Quality per language to test |
| Qwen3-TTS (free) | Speaks | es, zh, pt, ru | ar, vi, hi, fil |
| Chatterbox Multilingual (free, MIT, 23 languages claimed, 21 listed) | Speaks, zero-shot cloning | ar, zh, hi, pt, ru, es, vi | fil; Apple Silicon support not stated |
| OmniVoice (free, Apache 2.0, 600+ languages, 2026-03-31) | Speaks, zero-shot cloning, voice design from attributes; runs on Apple Silicon (MPS) | Claims all (its language list still to read) | Quality per language unknown; speed on an M4 unknown (40× real time claimed on a GPU) |
| ElevenLabs Flash v2.5 (paid, 32 languages, ~75 ms) | Speaks | All 8 | No Urdu, Haitian Creole or Hmong |
| ElevenLabs Eleven v4 Turbo (paid, 90+ languages, ~100 ms) | Speaks | Expected all 8 (confirm its list) | Haitian Creole and Hmong to check |
| Gemini 3.5 Live Translate (paid, preview, 70+ languages) | Hears + translates + speaks | To check | To check |
| OpenAI `gpt-realtime-translate` (paid) | Hears + translates + speaks | es, zh, vi, pt, ru, hi | ar, fil |
| Qwen3.8-LiveTranslate (paid, hosted) | Hears + translates + speaks, keeps the speaker's voice | All 8, plus Urdu (29 spoken languages) | Haitian Creole, Hmong |
| Meta Omnilingual ASR (free, 1,600+ languages) | Hears | — | Candidate for next-wave languages |

## 9. Re-check on 2026-11-19

What changed or was corrected a week after the first pass:

- **ElevenLabs Eleven v4 / v4 Turbo** (released 2026-09-28) replace Flash v2.5 as the paid voice choice: 90+ languages at about 100 ms. Missed in the first pass.
- **ElevenLabs Realtime Translation** is still an enterprise alpha. No self-serve access.
- **Google Gemini 3.5 Live Translate** (2026-06-09) was missing from the engine list. Added as a candidate paid engine.
- **Qwen3-ASR streaming** needs the vLLM backend (NVIDIA). On the Mac the free path is phrase by phrase, not word by word.
- **Chatterbox Multilingual** lists 21 languages on its page (23 claimed); no Tagalog.
- **ElevenLabs v3** speaks Urdu, Somali and Swahili (next-wave languages), but not Haitian Creole or Hmong.
- **OpenAI `gpt-realtime-translate`:** no change found (still 70+ in, 13 out, $0.034/min).
- **Not yet read:** OmniVoice's full language list (`docs/languages.md` in its repo) and Eleven v4 Turbo's language list.

## 10. Twilio trial and prices (checked 2026-11-19)

- **Trial:** 30 days. 75 voice minutes, 30 Media Streams minutes, 10 minutes per call, 5 concurrent calls. Calls only to verified numbers (up to 5 recipients) and only within your own country. Some TwiML verbs are blocked. One Twilio number.
- **After upgrading (pay as you go, US):** about $0.014/min for outbound calls, $0.0085/min inbound on a local number, $0.004/min for Media Streams, $1.15/month for a local number.
- **A bridged call** is two outbound legs, each with a media stream: about 2 × ($0.014 + $0.004) = $0.036 per call minute.
- **Consent:** the FCC ruled on 2024-02-08 that AI-generated voices on calls count as "artificial" voices under the TCPA, which requires the called person's prior consent. Keep the spoken disclosure and call only people who expect it. (Not legal advice.)

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
- [NCES Digest table 204.27: English learners by home language](https://nces.ed.gov/programs/digest/d23/tables/dt23_204.27.asp)
- [NCES Fast Facts: English learners](https://nces.ed.gov/fastfacts/display.asp?id=96)
- [ElevenLabs: supported languages by model](https://elevenlabs.io/docs/help-center/other/what-languages-do-you-support)
- [ElevenLabs: models overview](https://elevenlabs.io/docs/models)
- [Qwen3-ASR language list (PyPI)](https://pypi.org/project/qwen-asr/)
- [Chatterbox Multilingual (Resemble AI)](https://resemble.ai/introducing-chatterbox-multilingual-open-source-tts-for-23-languages)
- [OmniVoice: open TTS for 600+ languages (DEV Community)](https://dev.to/_46ea277e677b888e0cd13/omnivoice-open-source-tts-with-600-languages-and-zero-shot-voice-cloning-1mpn)
- [Qwen3.8-LiveTranslate speech output languages (DataLearner, Chinese)](https://www.datalearner.com/ai-models/pretrained-models/1093)
- [Qwen speech-to-speech models and language table (Qwen docs)](https://docs.platform.qianwenai.com/developer-guides/speech/s2s-models)
- [Omnilingual ASR on Apple Silicon (soniqo benchmarks)](https://soniqo.audio/benchmarks)
- [ElevenLabs: Eleven v4 announcement](https://elevenlabs.io/blog/eleven-v4)
- [ElevenLabs: text-to-speech API (v4 Turbo latency and price)](https://elevenlabs.io/text-to-speech-api)
- [ElevenLabs: v3 page with plan table (voice slots)](https://elevenlabs.io/v3)
- [ElevenLabs changelog 2026-10-19 (Realtime Translation for enterprise workspaces)](https://elevenlabs.io/docs/changelog/2026/10/19)
- [TechCrunch: ElevenLabs v4 supports 90 languages](https://techcrunch.com/?p=3170480)
- [Google Cloud: Gemini 3.5 Live Translate](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-5-live-translate)
- [Enterprise DNA: Gemini 3.5 Live Translate (price, language pairs)](https://enterprisedna.co/resources/news/google-gemini-35-live-translate-enterprise-multilingual-2026)
- [AnIntent: Gemini 3.5 Live Translate launch (transcript-mode caveat)](https://anintent.pages.dev/blog/google-gemini-3-5-live-translate-launch/)
- [qwen-asr on PyPI (streaming needs the vLLM backend)](https://pypi.org/project/qwen-asr/)
- [OmniVoice on Hugging Face](https://huggingface.co/k2-fsa/OmniVoice)
- [OmniVoice on a Mac (walkthrough)](https://pasqualepillitteri.it/en/news/15636/omnivoice-clone-voice-locally-mac)
- [Twilio: trial account](https://www.twilio.com/docs/usage/trials) and [trying out Voice](https://www.twilio.com/docs/usage/trials/try-out-voice)
- [Twilio: US voice pricing](https://www.twilio.com/voice/pricing/us)
- [Quiq: Twilio voice pricing summary](https://quiq.com/blog/twilio-voice-pricing/)
- [Mayer Brown: FCC ruling on AI-generated calls under the TCPA](https://www.mayerbrown.com/en/insights/publications/2024/02/fcc-declares-authority-and-intent-to-regulate-ai-generated-calls-under-the-tcpa)
