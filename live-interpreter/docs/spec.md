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
5. **First language pair: English ↔ Spanish.** It's the founding use case (a Colombian family talking with an English-speaking school), and every engine in this spec supports it, including the open-source Hibiki-Zero (Spanish → English). Adding a pair later means adding voices to the matrix, not code.
6. **No audio is stored.** Logs keep timings, events and (optionally) text only.
7. **The other person never needs an app.** A parent can be reached on any phone, including a landline, or join a meeting by scanning a QR code into a web page. Only the person starting the conversation uses the app.
8. **Captions are always on.** Both sides can see the original and the translation, so a wrong number, date or name can be caught and corrected on the spot.

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
| Translation engine adapter | `openai-realtime-translate` (v0), `elevenlabs-realtime` (if access), `hibiki-zero` (open-source stretch) |
| Phrase chunker | Turns translated text deltas into speakable chunks (clause or punctuation boundaries, max wait timer) |
| TTS adapter | ElevenLabs WebSocket streaming (v0), Qwen3-TTS (open-source stretch) |
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

| Output language | Accent | Gender × age | Voices |
| --- | --- | --- | --- |
| English | Light Latin American Spanish | 2 × 3 | 6 |
| Spanish | Light American English | 2 × 3 | 6 |

12 voices for the first pair. Store their IDs in `voices.json`, with the prompt used for each so they can be regenerated.

**Accent strength is a setting** (subtle / noticeable / off). Default: subtle.

**Cloning (later, opt-in only).** Instant cloning of the actual speaker would sound closest, but it means copying someone's voice. Only ever offer it to the account owner for their own voice, never to the other person on the call.

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
| Translation | OpenAI `gpt-realtime-translate` | Optional source transcript via `gpt-realtime-whisper` ($0.017/min) |
| TTS | ElevenLabs Flash, WebSocket streaming | Voices from the Voice Design matrix |
| Voice profiler | Python sidecar (FastAPI + transformers) | audeering age/gender model, CPU |
| Telephony | Twilio Programmable Voice + bidirectional Media Streams | One phone number |
| Local dev | M4 Mac mini + ngrok for a public WSS URL | Twilio needs to reach the server |
| Hosting (later) | Fly.io or Render | Must support long-lived WebSockets |
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

- **Translation:** $0.034 per audio minute per direction. Both directions stream continuously, so roughly **$0.07 per conversation minute**.
- **Voice:** ElevenLabs bills by characters (Flash and Turbo use about 0.5–1 credit per character), so cost depends on how much is said and the plan's credit price.
- **Phone:** two billed Twilio legs per call plus the number's monthly fee. Check Twilio's current rates before testing.

Fine for a portfolio project. Add a hard per-call time limit and a monthly spend alert anyway.

## Build milestones

Build in order; each one working and logged before the next.

1. **One-way pipe on the Mac.** Mic → `gpt-realtime-translate` → speakers, using OpenAI's own audio. Stage-timing log. *Done when:* you speak Spanish and hear English with mouth-to-ear measured and logged.
2. **Matched voice.** Translated text deltas → phrase chunker → ElevenLabs streaming TTS. Generate the 12-voice matrix. Manual profiles only. *Done when:* a listener who hasn't heard the speaker correctly guesses their gender and rough age from the translated voice, and latency stays within budget.
3. **Automatic voice profiling.** Python sidecar with the audeering model, voice picker, lock-in and 15-second re-check. *Done when:* 10 test speakers (friends, recordings) get a sensible voice without manual setup.
4. **Web room, two-way.** Rooms, links, both directions, captions, barge-in. *Done when:* a 5-minute English ↔ Spanish conversation with a friend in another room feels usable.
5. **Phone bridge.** Twilio number, outbound flow, two legs, disclosure, barge-in, "original underneath" setting. *Done when:* you call a Spanish-speaking friend's regular phone and hold a 5-minute conversation.
6. **In-person mode.** PWA screen, earbuds routing, half-duplex gate, big captions. *Done when:* a face-to-face exchange works without the phone's speaker feeding back into the translator.
7. **Portfolio polish.** README with architecture diagram, latency chart from real logs, a 60-second demo video of a real translated phone call, a "how it works" page. Hand any site changes for nicorudu.com to the website assistant.

**Stretch (v1+)**

- **Open-source path.** Hibiki-Zero (MIT, 3B parameters) translates French, Spanish, Portuguese and German into English with voice transfer built in. It needs an NVIDIA GPU (8 GB VRAM should work, 12 GB is safe), so run it on a rented GPU for the Spanish → English direction. Qwen3-TTS (Apache 2.0, 10 languages, voice design from descriptions, ~97 ms first audio) can replace ElevenLabs for the voice step.
- **Accent knob from research:** the original Hibiki controls how close the output stays to the source voice; higher settings give very strong accents. Worth an experiment for the "slight accent" feature.
- **Wider language coverage (high priority after v0).** `gpt-realtime-translate` only outputs 13 languages, and several common among newcomer families (for example Arabic, Haitian Creole, Dari, Pashto, Swahili) aren't among them. Add a second engine path: streaming speech-to-text + translation (Soniox advertises any-to-any across 60+ languages) feeding the same TTS step. Check each TTS's language list before promising a language.
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
| Mock parent-teacher conference (QR web room, two devices) | Parent joins by QR with no app; both follow along with captions | Joined in under 30 s; dates and numbers come through correctly |
| 10-minute call | No drift, no crashes, cost logged | Stable |

## Working notes for Claude Code

- Keep transports, engines, TTS and voice picking behind adapter interfaces so engines can be swapped (OpenAI → ElevenLabs Realtime → Hibiki-Zero) without touching the rest.
- One config file for all timings, thresholds and the voice matrix path.
- Unit tests for the phrase chunker, resampler and voice picker. Replay recorded test audio (your own, with consent) for regression tests.
- After every step: commit, add an entry to `BUILDLOG.md`, and update `HANDOFF.md` so nothing is lost when a conversation compacts. Save key prompts in `prompts/`.
- Git: branch first, never commit to `main`. Commit author `nicorudu <nicorudu@users.noreply.github.com>`.
- Never commit audio, transcripts, call logs, keys or `.env` files (already in `.gitignore`).
- Code must run on the M4 Mac mini and the Windows laptop.

## Risks and open questions

- **Transcript granularity.** If the translated text arrives in chunks that are too small or too late, the matched voice will lag. Fallback: fast mode with OpenAI's own voice.
- **Output language limit.** `gpt-realtime-translate` only outputs 13 languages, which misses many families the school use case is about. See "Wider language coverage" above.
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
