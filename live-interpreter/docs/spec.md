# Live Interpreter — v0 Spec

Updated 2026-11-12. Portfolio software build (vibecode portfolio, not a business). Working name; rename anytime.

## Overview

This build must prove one thing: two people who don't share a language can hold a natural, two-way conversation, including a regular phone call, where each person hears the other in their own language, in a realistic voice that matches the speaker's sex and age and carries a slight version of their accent.

**Who it's for.** Families who don't speak the local language and the teachers, coaches and community leaders who need to reach them, from both sides of the conversation. Full detail and the requirements they drive: [use-cases.md](use-cases.md).

**What it is not trying to do in v0:** clone anyone's exact voice. "Same kind of person" is the goal (a man in his 30s with a light Colombian accent sounds like that in English), not "same person."

### Three ways to talk

| Mode | How it works | What the other person needs |
| --- | --- | --- |
| **Phone bridge** (headline feature) | The server calls you and the other person, then translates between the two calls | Nothing. They answer a normal phone call |
| **Web room** | You send a link; each person talks through their browser | A browser |
| **In person** | One phone between you; you wear earbuds, they hear the phone speaker | Nothing |

### Why the phone call needs a proxy

Phones don't let apps tap into regular carrier calls. Apple says outright that there is no supported API for a third-party iOS app to get the other caller's audio during a native cellular call. A VoIP app, though, has raw access to all of its own audio. So the app never touches the carrier call. Instead, **our server sits in the middle of the call**: each person is on their own phone line to the server, and the server only ever passes translated speech across.

Built-in options exist (Pixel 10 Voice Translate, Apple Live Translation for calls), but each is locked to its own phones, covers a short list of language pairs and can't be customized. Neither lets you pick or design the voice the other person hears. That gap is what this project fills.

## Key decisions

1. **Translation engine for v0: OpenAI `gpt-realtime-translate`.** It is self-serve, costs $0.034 per minute of audio, takes 70+ input languages and outputs 13 (English, Spanish, Portuguese, French, German, Italian, Russian, Chinese, Japanese, Korean, Hindi, Indonesian, Vietnamese). It streams translated audio plus a translated transcript while the speaker is still talking.
2. **Its built-in voices are not used for the main experience.** The model doesn't support voice selection or custom prompting. So we take its **translated transcript stream**, and speak it with our own matched voice (ElevenLabs). Its own audio stays available as a "fast mode" to compare latency.
3. **ElevenLabs Realtime Translation is the ideal engine but is gated.** It streams translated speech in a chosen `voice_id`, but its WebSocket API is currently for enterprise workspaces only. The code gets an engine adapter slot for it so it can be swapped in later.
4. **Voices: ElevenLabs Flash streaming TTS + a pre-designed voice matrix** made once with the Voice Design API (gender, age, accent, accent strength). No voice is generated during a call; the system picks from the matrix.
5. **Build with English ↔ Spanish first, then add the launch set.** Spanish is the founding use case (a Colombian family talking with an English-speaking school) and about three in four US English learners. Once the pipeline works, M5 adds seven more languages: Arabic, Chinese (Mandarin), Vietnamese, Portuguese, Russian, Hindi and Filipino (Tagalog). See "Languages" below.
6. **No audio is stored.** Logs keep timings, events and (optionally) text only.
7. **The other person never needs an app.** A parent can be reached on any phone, including a landline, or join a meeting by scanning a QR code into a web page. Only the person starting the conversation uses the app.
8. **Captions are always on.** Both sides can see the original and the translation, so a wrong number, date or name can be caught and corrected on the spot.
9. **A free, fully open-source path is built alongside the paid one.** Open Qwen models (Qwen3-ASR → Qwen3.5 → Qwen3-TTS) run on the Mac mini; a free Oracle Cloud VM is the public server. Both paths sit behind the same adapters, so each call can use either. See "Free path" below.

## Architecture

One server, two one-way translation pipelines per conversation (A → B and B → A). OpenAI's own guide describes calls this way: caller A's audio is translated into B's language and played to B, and the reverse.

```
Person A audio ──► resample/VAD ──► Translate session (A→B) ──► translated text deltas
                                                                       │
                                     voice picked for A ◄── Voice profiler (first ~4 s of A)
                                                                       ▼
                                          phrase chunker ──► ElevenLabs streaming TTS ──► Person B

Person B audio ──► (mirror of the above) ──────────────────────────────────────────────► Person A
```

**Modules** (each testable alone, all behind typed interfaces):

| Module | Job |
| --- | --- |
| Transport adapters | Twilio leg, browser WebSocket, in-person mic/speaker. All expose the same "audio in / audio out" interface |
| Audio utils | Resampling and format conversion (Twilio μ-law 8 kHz ↔ 24 kHz PCM16), voice activity detection |
| Translation engine adapter | `openai-realtime-translate` (v0, paid), `qwen-cascade` (v0, free: Qwen3-ASR → Qwen3.5), `elevenlabs-realtime` (if access), `qwen-livetranslate` (hosted Qwen API, optional), `hibiki-zero` (open-source stretch) |
| Phrase chunker | Turns translated text deltas into speakable chunks (clause or punctuation boundaries, max wait timer) |
| TTS adapter | ElevenLabs WebSocket streaming (v0, paid), Qwen3-TTS via MLX (v0, free) |
| Language router | Picks, per language pair, which engine hears, which translates and which voice speaks (see "Languages") |
| Voice profiler | Estimates gender and age band from the speaker's first few seconds |
| Voice picker | Maps profile + accent + target language to a voice ID from the matrix |
| Session controller | Starts/stops sessions, barge-in, disclosure prompt, logging |

## Voice matching

The goal is "sounds like the same kind of person," decided in the first few seconds and then locked for the call.

**Step 1 — Profile the speaker.** Run `audeering/wav2vec2-large-robust-24-ft-age-gender` on the first ~4 seconds of speech. It estimates age (0–100) and gender (child / female / male). It's a 318M-parameter model, so it runs fine on CPU in a small Python sidecar.
- Manual override always wins. Set your own profile once (for example "male, 30s, Colombian Spanish") so your voice is never guessed.
- Re-check once at ~15 s; switch only if the estimate changed bucket with high confidence.

**Step 2 — Decide the accent.** The accent is simply the speaker's source language (and region, if set). A Spanish speaker gets an English voice with a light Latin American Spanish accent; an English speaker gets a Spanish voice with a light American English accent. Regional accents (Colombian vs. Mexican Spanish) are worth testing early with Voice Design, since the accent field takes free text; if they don't come through clearly, fall back to a general Latin American accent.

**Step 3 — Pick from the voice matrix.** Built once with ElevenLabs Voice Design, which takes a description plus `gender`, `age` (young / middle_aged / old), `accent` and `accent_strength`. Each design returns three options; pick the best and save it (saving takes a voice slot on the plan).

| Speaker's language | Accent | Gender × age | Voices | Speaks |
| --- | --- | --- | --- | --- |
| Spanish | Light Latin American Spanish | 2 × 3 | 6 | English (and any other output language) |
| English | Light American English | 2 × 3 | 6 | Spanish (and any other output language) |

12 voices for the first pair; the launch set grows this by speaker language (see "Languages"). Store their IDs in `voices.json`, with the prompt used for each so they can be regenerated.

**Accent strength is a setting** (subtle / noticeable / off). Default: subtle.

**Cloning (later, opt-in only).** Instant cloning of the actual speaker would sound closest, but it means copying someone's voice. Only ever offer it to the account owner for their own voice, never to the other person on the call.

## Free path (all open source)

The same pipeline with every paid model swapped for an open one from Alibaba's Qwen team. All three are Apache 2.0: free to download, run and use, including commercially.

| Step | Model | What matters here |
| --- | --- | --- |
| **Hear** | **Qwen3-ASR** 0.6B or 1.7B (released 2026-01-29) | 30 languages plus 22 Chinese dialects, including English, Spanish and Arabic. Identifies the language itself. Streaming and offline in one model. An Apple Silicon (MLX) port runs about 30× faster than real time (measured on an M5 Pro; expect less on an M4, still far more than needed) |
| **Translate** | **Qwen3.5** small model, 4B or 9B (released 2026-03-02) | Text-to-text translation with a short prompt. Because it's prompted, a school glossary ("IEP", "permission slip") can go straight into the instructions, which the OpenAI model doesn't allow |
| **Speak** | **Qwen3-TTS** 1.7B VoiceDesign + Base (released 2026-01) | 10 languages: Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish (European and Latin American) and Italian. Designs voices from a text description, clones from 3 seconds of audio, streams. Faster than real time on Apple Silicon |

**Voice matching on the free path** works like the ElevenLabs matrix: design each of the 12 voices once with VoiceDesign ("a man in his 30s, warm, speaking English with a light Colombian accent"), keep a short reference clip of each, and speak with the Base model cloning from that clip so the voice stays identical every call. Qwen documents this "design, then clone" flow.

**Where it runs:**

```
Phone (Twilio) / browser ──► Oracle Cloud Always Free VM
                              public address, Twilio bridge, web rooms, session control
                                        │  private tunnel (Tailscale)
                                        ▼
                              Mac mini M4: Qwen3-ASR → Qwen3.5 → Qwen3-TTS (MLX)
```

- **Oracle's free VM hosts the server, not the models.** The Always Free Arm allowance is now 2 OCPUs and 12 GB of memory (halved from 4 / 24 in 2026), with no GPU. Qwen3-TTS on CPUs of that class runs a bit slower than real time even with more cores, so live speech would lag. As an always-on public address for Twilio and the web rooms it's ideal, and free.
- **The Mac mini does the AI work.** It stays private behind the tunnel; nothing on it is exposed to the internet. It has to be on and online during calls.
- **Memory:** Qwen3-TTS alone peaks around 4–6 GB in MLX. Check how much memory is used with all three models loaded; smaller variants (ASR 0.6B, Qwen3.5 4B, TTS 0.6B Base) are the fallback.

**What still costs money:** phone-bridge minutes on Twilio. The web room and in-person modes are completely free on this path.

**Limits to test:**
- **Speed.** Three models in a row may be slower than one streaming API. Measured in M1 against the OpenAI path. If it's too slow: smaller models, or a rented GPU by the hour (Oracle's A10 is about $2/hour, so not free).
- **Languages.** Qwen3-TTS speaks 10 languages, so the language gap from the school use case (Arabic, Haitian Creole and others) is still open on the voice side, even though Qwen3-ASR can hear Arabic.
- **Accent.** Whether VoiceDesign can produce a believable light Colombian accent in English.

**Related, but not free:** Qwen3.8-LiveTranslate (Sept 2026) is Qwen's own hosted interpreter: it understands 60 languages, speaks 29, and keeps the speaker's voice. It's API-only with no open weights, so it's a possible paid adapter, not part of the free path.

## Languages

### Launch set (M5)

Chosen from the most common home languages of English learners in US public schools (NCES, fall 2021) plus Nico's picks. Every language below is heard and translated by the free path; the voice is where coverage differs.

| Language | US English learners (rank, count) | Hears (free: Qwen3-ASR) | Speaks free | Speaks paid (ElevenLabs Flash v2.5) | OpenAI translate output |
| --- | --- | --- | --- | --- | --- |
| Spanish | #1, 4,023,289 | ✓ | ✓ Qwen3-TTS | ✓ | ✓ |
| Arabic | #2, 130,917 | ✓ | Chatterbox Multilingual (to test) | ✓ | ✗ |
| Chinese (Mandarin) | #4, 95,584 | ✓ | ✓ Qwen3-TTS | ✓ | ✓ |
| Vietnamese | #5, 75,070 | ✓ | Chatterbox Multilingual (to test) | ✓ | ✓ |
| Portuguese | #6, 50,205 | ✓ | ✓ Qwen3-TTS | ✓ | ✓ |
| Russian | #7, 39,403 | ✓ | ✓ Qwen3-TTS | ✓ | ✓ |
| Hindi | not in top 15 (Nico's pick) | ✓ | Chatterbox Multilingual (to test) | ✓ | ✓ |
| Filipino (Tagalog) | #15, 19,319 | ✓ | OmniVoice (to test) | ✓ | ✗ |

(#3 in the NCES list is English itself, reported for students from multilingual homes.)

**"Indian" means Hindi for now.** Urdu ranks higher among US English learners (#10, 26,567) and is close to Hindi when spoken, but uses a different script for captions, and Qwen3-ASR doesn't list it. Confirm with Nico's wife's school which Indian languages its families speak.

### Language router

One rule per language, kept in config:

1. **Hear:** Qwen3-ASR for all 8 (free). The OpenAI engine stays an option where it covers the pair.
2. **Translate:** Qwen3.5 for any pair (free, prompted, glossary-aware). `gpt-realtime-translate` when the target is one of its 13 outputs and the paid path is chosen.
3. **Speak:** Qwen3-TTS for es / zh / pt / ru. For ar / vi / hi / fil, an open voice if it passes the native-speaker check (Chatterbox Multilingual or OmniVoice), otherwise ElevenLabs Flash v2.5.

This means even the "free" setup may pay for voice in four languages, depending on how the open voices sound. ElevenLabs bills only by characters spoken, so that cost stays small.

### Voices grow by speaker language

The voice models are multilingual, so a voice is chosen by **who is speaking** (their sex, age band and accent), and then speaks whichever language the listener needs. Each speaker language gets 6 voices (2 sexes × 3 age bands) with a light accent of that language. The launch set plus English is 9 × 6 = **54 voices**.
- On the free path, each voice is a short reference clip, so there's no limit.
- On ElevenLabs, each saved voice takes a slot, and plans cap the number. Start with Spanish and English accents, and use neutral voices for the other languages until the plan allows more.

### Next wave (v1)

Haitian Creole (#8), Hmong (#9), Urdu (#10), Swahili (#13) and Somali (#14). Neither Qwen3-TTS, Chatterbox Multilingual, ElevenLabs Flash v2.5 nor OpenAI's translator outputs Haitian Creole or Hmong, and Qwen3-ASR doesn't hear them (ElevenLabs v3's 74-language list is still to check). Candidates: OmniVoice (open TTS, 600+ languages) for the voice and Meta's Omnilingual ASR (1,600+ languages) for hearing; Qwen3.8-LiveTranslate also speaks Urdu. Korean (#11) and French (#12) can be added any time, since every engine already covers them.

## Modes in detail

### Phone bridge (Twilio)

**Outbound flow ("call someone in Spanish"):**

1. In the app, enter the number and pick the languages, then tap Call.
2. The server calls **your** phone first. You answer.
3. The server dials the other person. When they answer, it plays a one-line disclosure in their language ("This call is being interpreted by AI").
4. Each call leg runs **one bidirectional Media Stream** (Twilio allows only one per call) over a WebSocket to the server.
5. The server never connects the two legs directly. Leg A's audio goes only into the A→B translator, and B hears only the translated voice (and the reverse).

**Details:**

- **Audio formats:** phone audio arrives as μ-law 8 kHz and must be resampled to 24 kHz PCM16 for OpenAI. Send continuous audio, including silence between phrases. For the return path, ask ElevenLabs for telephony-format output if its current docs offer it, otherwise convert.
- **Barge-in:** if the listener starts talking while translated speech is still playing, stop the playback (Twilio's `clear` message on the stream) so turn-taking stays natural.
- **"Hear the original underneath" setting:** the server mixes the original voice in at low volume under the translation, like a UN interpreter. Off by default; test whether it helps turn-taking.
- **Caller ID:** check whether Twilio lets the outbound leg show your own verified number instead of the Twilio number.
- **Inbound (v1):** people call your interpreter number; the server rings your cell and bridges.

Reference implementations to read first: OpenAI's realtime translation cookbook (its Twilio phone demo bridges phone audio into Realtime Translation and back) and Twilio's own OpenAI live-translation code exchange sample.

### Web room

- Create a room, share a link or show a **QR code**, each person picks their language.
- Browser captures the mic (with built-in echo cancellation) and streams PCM over a WebSocket; the server returns the other person's translated audio.
- Live captions on screen for both sides (original and translated), using the source and translated transcript streams.
- **In-room meetings use this mode too:** at a parent-teacher conference, the parent scans the QR code and listens on their own phone (ideally with earbuds), while the teacher uses a laptop. Two devices avoid the speaker-echo problem of a single shared phone.
- This is the fastest mode to build and the easiest to demo on the portfolio site.

### In person

- One phone. You wear earbuds and hear their speech translated; they hear yours from the phone speaker.
- **Echo is the main risk:** the phone speaker plays translated speech, and the mic picks it up again. v0 handles this with a half-duplex gate (mute input to the translator while playing to the speaker) plus the browser's echo cancellation. Best experience: both people in earbuds, or two phones in a web room.
- Big captions on screen as a backup.

## Tech stack

| Piece | Choice | Notes |
| --- | --- | --- |
| Server | Node.js + TypeScript (Fastify + `ws`) | Matches the OpenAI and Twilio reference demos |
| Client | Vite + TypeScript PWA | Works on iPhone, Android, Mac and Windows from one codebase |
| Translation (paid) | OpenAI `gpt-realtime-translate` | Optional source transcript via `gpt-realtime-whisper` ($0.017/min) |
| Translation (free) | Qwen3-ASR + Qwen3.5 (4B or 9B) via MLX on the Mac mini | Python model service the server calls over the tunnel |
| TTS (paid) | ElevenLabs Flash, WebSocket streaming | Voices from the Voice Design matrix |
| TTS (free) | Qwen3-TTS via MLX on the Mac mini | Voices designed once, then cloned from reference clips |
| Voice profiler | Python sidecar (FastAPI + transformers) | audeering age/gender model, CPU |
| Telephony | Twilio Programmable Voice + bidirectional Media Streams | One phone number |
| Local dev | M4 Mac mini + ngrok for a public WSS URL | Until the Oracle VM is set up |
| Hosting | Oracle Cloud Always Free Arm VM (≤ 2 OCPU / 12 GB) for the server; Mac mini for models over Tailscale | Must support long-lived WebSockets. Fly.io or Render as fallback |
| Secrets | OS keychain locally (macOS Keychain / Windows Credential Manager), the host's secret store when deployed | OpenAI, ElevenLabs, Twilio keys. Never in the repo, never in a committed file |

## Latency budget (targets to measure, not facts)

The number that matters is **mouth-to-ear**: from when a speaker says a phrase to when the listener starts hearing it translated.

| Stage | v0 target |
| --- | --- |
| Capture + network in | ≤ 150 ms (web), ≤ 300 ms (phone) |
| Translation first text for a phrase | ≤ 800 ms after the phrase's key words |
| Phrase chunker wait | ≤ 300 ms (max wait timer) |
| TTS first audio | ≤ 300 ms |
| Network out + playback | ≤ 150 ms (web), ≤ 300 ms (phone) |
| **Mouth-to-ear** | **≤ 1.5 s web, ≤ 2.0 s phone** |

Log a timestamp at every stage boundary for every phrase. Compare "matched voice" mode with "fast mode" (OpenAI's own audio). If the matched voice adds too much delay, try sending TTS smaller chunks before giving up on it.

## Cost per conversation minute (rough)

- **Free path:** $0 for models and the Oracle VM. Only Twilio minutes cost money, and only in phone-bridge mode.
- **Translation (paid path):** $0.034 per audio minute per direction. Both directions stream continuously, so roughly **$0.07 per conversation minute**.
- **Voice:** ElevenLabs bills by characters (Flash and Turbo use about 0.5–1 credit per character), so cost depends on how much is said and the plan's credit price.
- **Phone:** two billed Twilio legs per call plus the number's monthly fee. Check Twilio's current rates before testing.

Fine for a portfolio project. Add a hard per-call time limit and a monthly spend alert anyway.

## Build milestones

Build in order; each one working and logged before the next.

1. **One-way pipe on the Mac, two engines.** Free path first, because it needs no accounts: mic → Qwen3-ASR → Qwen3.5 → Qwen3-TTS (one stock voice) → speakers. Then the paid path when the OpenAI key arrives: mic → `gpt-realtime-translate` → speakers, using OpenAI's own audio. Stage-timing log for both. *Done when:* you speak Spanish and hear English on both paths, with mouth-to-ear measured side by side and memory use noted.
2. **Matched voice.** Translated text → phrase chunker → TTS, on both paths: ElevenLabs streaming TTS and Qwen3-TTS. Build the 12-voice matrix for each. Manual profiles only. *Done when:* a listener who hasn't heard the speaker correctly guesses their gender and rough age from the translated voice, and latency stays within budget.
3. **Automatic voice profiling.** Python sidecar with the audeering model, voice picker, lock-in and 15-second re-check. *Done when:* 10 test speakers (friends, recordings) get a sensible voice without manual setup.
4. **Web room, two-way.** Rooms, links, both directions, captions, barge-in. *Done when:* a 5-minute English ↔ Spanish conversation with a friend in another room feels usable.
5. **Launch languages.** Language router, the 7 added languages, voices per speaker language, and a voice test for ar / vi / hi / fil: open voice first (Chatterbox Multilingual, OmniVoice), ElevenLabs if it fails. *Done when:* a native speaker of each launch language holds a 3-minute web-room conversation with an English speaker and rates the translation and voice as understandable and natural.
6. **Phone bridge.** Server moves to the Oracle Always Free VM, connected to the Mac mini over Tailscale. Twilio number, outbound flow, two legs, disclosure, barge-in, "original underneath" setting. *Done when:* you call a Spanish-speaking friend's regular phone and hold a 5-minute conversation.
7. **In-person mode.** PWA screen, earbuds routing, half-duplex gate, big captions. *Done when:* a face-to-face exchange works without the phone's speaker feeding back into the translator.
8. **Portfolio polish.** README with architecture diagram, latency chart from real logs, a 60-second demo video of a real translated phone call, a "how it works" page. Hand any site changes for nicorudu.com to the website assistant.

**Stretch (v1+)**

- **Hibiki-Zero.** (MIT, 3B parameters) translates French, Spanish, Portuguese and German into English with voice transfer built in. It needs an NVIDIA GPU (8 GB VRAM should work, 12 GB is safe), so it would run on a rented GPU for the Spanish → English direction. (Qwen3-TTS moved into v0 as the free path.)
- **Qwen3.8-LiveTranslate adapter** (hosted, paid): 60 languages understood, 29 spoken, keeps the speaker's voice. Worth comparing against OpenAI once v0 works.
- **Accent knob from research:** the original Hibiki controls how close the output stays to the source voice; higher settings give very strong accents. Worth an experiment for the "slight accent" feature.
- **Next-wave languages (high priority after v0).** Haitian Creole, Hmong, Urdu, Swahili, Somali; see "Languages". Soniox (advertises any-to-any translation across 60+ languages) is another hearing-and-translating option to compare. Check each voice model's language list before promising a language.
- **Meeting recap in both languages (opt-in).** After a conference or call, a short summary of what was agreed (dates, forms, next steps), in both languages. Needs both people's consent, because it means keeping text.
- **Glossary for school terms** (IEP, ESOL, permission slip, field trip). `gpt-realtime-translate` doesn't support custom prompting, so this needs the second engine path or a correction step on the translated text.
- ElevenLabs Realtime Translation adapter if enterprise access comes through.
- Opt-in cloning of your own voice.
- Inbound calls, three-way calls (teacher + parent + student), more language pairs, regional accents (Colombian vs. Mexican Spanish).

## Test plan

| Scenario | Expected behavior | Starting target |
| --- | --- | --- |
| Short phrases back and forth | Each side hears the other translated | Mouth-to-ear within budget |
| Long monologue (60 s) | Translation keeps pace, no growing delay | Delay at 60 s ≤ delay at 10 s + 0.5 s |
| Interruption while translation plays | Playback stops, new speech is translated | Stops within 300 ms |
| Male / female, young / older speakers | Voice matches gender and age band | 8 of 10 test speakers |
| Accent setting subtle vs. off | Audible difference, still easy to understand | Blind listener prefers subtle or neutral |
| Noisy room / car | Still usable | Note accuracy drop |
| Phone call to a landline or mobile | Works with no app on their side | Clean audio both ways |
| Speakerphone in person mode | No feedback loop | No self-translation |
| Each launch language with a native speaker (web room) | Understandable translation and natural voice | Native speaker rates both "good" or better |
| Mock parent-teacher conference (QR web room, two devices) | Parent joins by QR with no app; both follow along with captions | Joined in under 30 s; dates and numbers come through correctly |
| 10-minute call | No drift, no crashes, cost logged | Stable |

## Working notes for Claude Code

- Keep transports, engines, TTS and voice picking behind adapter interfaces so engines can be swapped (OpenAI ↔ Qwen free path ↔ ElevenLabs Realtime ↔ Hibiki-Zero) without touching the rest.
- One config file for all timings, thresholds and the voice matrix path.
- Unit tests for the phrase chunker, resampler and voice picker. Replay recorded test audio (your own, with consent) for regression tests.
- After every step: commit, add an entry to `BUILDLOG.md`, and update `HANDOFF.md` so nothing is lost when a conversation compacts. Save key prompts in `prompts/`.
- Git: branch first, never commit to `main`. Commit author `nicorudu <nicorudu@users.noreply.github.com>`.
- Never commit audio, transcripts, call logs, keys or `.env` files (already in `.gitignore`).
- Code must run on the M4 Mac mini and the Windows laptop. Exception: the free-path model server uses MLX, which is Apple Silicon only. On Windows or Linux, Qwen3-TTS can use its GGML backend later.

## Risks and open questions

- **Transcript granularity.** If the translated text arrives in chunks that are too small or too late, the matched voice will lag. Fallback: fast mode with OpenAI's own voice.
- **Language coverage.** `gpt-realtime-translate` outputs 13 languages (no Arabic or Filipino) and Qwen3-TTS speaks 10, so the language router has to mix engines. Haitian Creole and Hmong aren't covered yet. See "Languages".
- **Translation quality varies by language.** Benchmarks lean toward big languages. Every launch language needs a native-speaker check before it's offered.
- **Accuracy on what matters.** A wrong date, time or amount is worse than a slow translation. Captions on both sides are the v0 safety net; a "repeat that" control and read-back of numbers are candidates for v1.
- **Disclosure and privacy.** The other person's speech goes to third-party APIs. Play the disclosure, store no audio, and don't use it for anything sensitive. Schools have their own student-privacy rules (in the US, FERPA) and often contracted interpreters; v0 is a personal prototype, not a school-approved tool. (Not legal advice.)
- **Model license.** The audeering age/gender model is CC-BY-NC-SA (non-commercial). Fine for a portfolio; swap it out if this ever becomes a product.

## Sources

- [OpenAI: Advancing voice intelligence with new models in the API (May 7, 2026)](https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/)
- [OpenAI: Realtime translation guide](https://developers.openai.com/api/docs/guides/realtime-translation)
- [OpenAI Cookbook: Build live translation apps with gpt-realtime-translate](https://developers.openai.com/cookbook/examples/voice_solutions/realtime_translation_guide)
- [OpenAI: GPT-Realtime-Translate model page](https://developers.openai.com/api/docs/models/gpt-realtime-translate)
- [ElevenLabs: Realtime Translation WebSocket API reference](https://elevenlabs.io/docs/api-reference/realtime-translation/v-1-translation-realtime)
- [ElevenLabs: Voice Design](https://elevenlabs.io/docs/eleven-creative/voices/voice-design)
- [ElevenLabs JS SDK: Voice Design parameters](https://tessl.io/registry/tessl/npm-elevenlabs--elevenlabs-js/files/docs/voices/voice-design.md)
- [Twilio: Media Streams overview](https://www.twilio.com/docs/voice/media-streams)
- [Twilio Code Exchange: Live translation with OpenAI Realtime API](https://twilio.com/code-exchange/live-translation-openai-realtime-api)
- [Apple Developer Forums: access to remote caller audio in a cellular call](https://developer.apple.com/forums/thread/848873)
- [audeering: wav2vec2 age and gender model](https://huggingface.co/audeering/wav2vec2-large-robust-24-ft-age-gender)
- [Kyutai: Hibiki-Zero on GitHub](https://github.com/kyutai-labs/hibiki-zero)
- [Kyutai: Hibiki samples (accent vs. voice fidelity)](https://kyutai-hibiki-samples.static.hf.space/)
- [Qwen3-TTS overview](https://comfyui-wiki.com/en/news/2026-01-22-alibaba-qwen3-tts-release)
- [Deepgram: Is ElevenLabs real-time? (credit pricing)](https://deepgram.com/learn/is-elevenlabs-real-time-what-developers-need-to-know)
- [Soniox vs. OpenAI translation comparison (vendor page)](https://soniox.com/compare-translation/openai)
- [Qwen3-ASR on GitHub](https://github.com/QwenLM/Qwen3-ASR) and [open-source announcement](https://www.alibabacloud.com/blog/qwen3-asr-%26-qwen3-forcedaligner-is-now-open-sourced-robust-streaming-and-multilingual_602843)
- [Qwen3.5 small models (NYU Shanghai RITS)](https://rits.shanghai.nyu.edu/ai/qwen-3-5-small-models-9b-parameters-that-beat-120b/)
- [Qwen3-TTS model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base) and [language notes](https://www.mintlify.com/QwenLM/Qwen3-TTS/concepts/languages)
- [Qwen3-TTS speed on Apple Silicon (soniqo)](https://soniqo.audio/guides/speak) and [Apple Silicon ASR benchmarks](https://soniqo.audio/benchmarks)
- [Quantized Qwen3-TTS on CPU, real-time factors (ocdevel)](https://dev.ocdevel.com/blog/20260711-quantized-cpu-tts)
- [Oracle Always Free limits halved (terminalbytes)](https://terminalbytes.com/oracle-cloud-free-tier-changes-2026)
- [Qwen3.8-LiveTranslate (API only)](https://www.artiverse.ca/alibabas-qwen38-livetranslate-targets-faster-real-time-speech-translation/)
- [NCES Digest table 204.27: English learners by home language (fall 2021)](https://nces.ed.gov/programs/digest/d23/tables/dt23_204.27.asp)
- [ElevenLabs: supported languages by model](https://elevenlabs.io/docs/help-center/other/what-languages-do-you-support)
- [Qwen3-ASR language list (PyPI)](https://pypi.org/project/qwen-asr/)
- [Chatterbox Multilingual (Resemble AI)](https://resemble.ai/introducing-chatterbox-multilingual-open-source-tts-for-23-languages)
- [OmniVoice: open TTS for 600+ languages](https://dev.to/_46ea277e677b888e0cd13/omnivoice-open-source-tts-with-600-languages-and-zero-shot-voice-cloning-1mpn)
- [Qwen speech-to-speech models and language table (Qwen docs)](https://docs.platform.qianwenai.com/developer-guides/speech/s2s-models)
