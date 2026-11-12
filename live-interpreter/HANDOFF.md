# Handoff — Live Interpreter

**Read this first when picking the project back up** (new chat, after a context reset, or switching to the Mac mini). It holds the current state, the next step, and the rules. It is updated and pushed after every step.

Last updated: 2026-11-12 · by Claude (cloud session)

---

## 1. Where we are right now
- **Done:** research, use cases, v0 spec, decision log. Project folder created on branch `live-interpreter-kickoff`, PR #8 to `main`.
- **No code yet.**
- **Next step: M1, one-way pipe on the Mac.** Mic → `gpt-realtime-translate` → speakers, using OpenAI's own voice, with a timestamp at every stage so mouth-to-ear delay is measured. Also add a small `keys:set` script that stores API keys in the OS keychain.
- **Blocked on:** an OpenAI API key (M1). ElevenLabs is needed from M2, Twilio from M5 (see §6).

## 2. Milestones

| # | What | Needs | State |
|---|---|---|---|
| M1 | One-way pipe on the Mac (OpenAI voice), latency log | OpenAI key | **next** |
| M2 | Matched voice: transcript → phrase chunker → ElevenLabs TTS; 12-voice matrix; manual profiles | ElevenLabs | planned |
| M3 | Automatic voice profiling (audeering sidecar), voice picker, lock-in + 15 s re-check | — | planned |
| M4 | Web room, two-way: rooms, link + QR, captions, barge-in | — | planned |
| M5 | Phone bridge: Twilio number, outbound flow, two legs, disclosure, barge-in | Twilio | planned |
| M6 | In-person mode: PWA screen, earbuds routing, half-duplex gate | — | planned |
| M7 | Portfolio polish: README diagram, latency chart, 60 s demo of a real call, showcase update | — | planned |
| v1 | Wider language coverage (second engine), meeting recap (opt-in), glossary, inbound calls | — | after v0 |

Details for each: [spec](docs/spec.md) "Build milestones".

## 3. Standing rules (from Nico)
1. **Document everything in GitHub after every step**, and update this handoff, so nothing is lost when the chat compacts.
2. **Website (nicorudu.com):** don't edit it. Write the exact changes for Nico to hand to his website Claude assistant.
3. **Git:** branch first, never commit to `main`. Commit author `nicorudu <nicorudu@users.noreply.github.com>`. Never put Nico's personal email in commits or external requests.
4. **Secrets** (OpenAI, ElevenLabs, Twilio) go in the OS keychain locally and the host's secret store when deployed. Never in the repo.
5. **No audio, transcripts or call logs in the repo**, ever (`.gitignore` covers them).
6. Nico uses an **M4 Mac mini** (main) and an **HP OmniBook X Flip (Windows)**. Code must run on both.
7. **Voice cloning** is only ever opt-in, and only for the account owner's own voice. Never clone the other person on a call.

## 4. Design in one paragraph
A Node + TypeScript server runs two one-way translation pipelines per conversation (A → B and B → A). Each pipeline streams the speaker's audio into OpenAI `gpt-realtime-translate`, takes its translated text as it arrives, cuts it into speakable phrases, and speaks them with ElevenLabs streaming TTS in a voice picked from a pre-designed matrix (sex × age band × output language, with a light accent from the speaker's language). A Python sidecar guesses sex and age from the first ~4 seconds of speech. Audio gets in and out through transport adapters: Twilio call legs (phone bridge), browser WebSockets (web room, QR join) or the device's own mic and speaker (in person). Captions for both sides are always on.

Full detail: [spec](docs/spec.md) · [use cases](docs/use-cases.md) · [research](docs/research.md) · [decisions](docs/decisions.md) · [build log](BUILDLOG.md).

## 5. Key technical facts (so they don't need re-researching)
Checked 2026-11-12. Sources are in [research.md](docs/research.md).
- **OpenAI `gpt-realtime-translate`:**
  - 70+ input languages, 13 output: en, es, pt, fr, de, it, ru, zh, ja, ko, hi, id, vi. $0.034 per audio minute.
  - One target language per session, set with `session.audio.output.language`. A 1:1 call = 2 sessions. Group rooms ≈ active speakers × target languages.
  - Send base64 **24 kHz PCM16** with `session.input_audio_buffer.append`, **including silence** between phrases.
  - Events: `session.output_audio.delta` (translated audio), `session.output_transcript.delta` (translated text), `session.input_transcript.delta` (source text, when input transcription uses `gpt-realtime-whisper`, $0.017/min). Optional `noise_reduction: { type: "near_field" }`.
  - **No voice selection and no custom prompting.**
  - Reference: OpenAI Cookbook "Build live translation apps with gpt-realtime-translate" (browser, Twilio phone and LiveKit demos).
- **ElevenLabs Realtime Translation** (adapter slot only): `wss://api.elevenlabs.io/v1/translation/realtime`, query params `target_language` (required), `source_language` (optional, auto-detect), `voice_id` (required), `tts_model_id` (default `eleven_v4_turbo`; also `eleven_flash_v2_5`, `eleven_v3`), `eagerness` (low / medium / high). **Enterprise workspaces only** for now.
- **ElevenLabs Voice Design:** description plus `gender` (male / female / neutral), `age` (young / middle_aged / old), `accent` (free text), `accent_strength`. Returns three previews; saving one takes a voice slot.
- **Twilio Media Streams:** bidirectional streams send and receive audio over a WebSocket. **One bidirectional stream per call**, so a bridged conversation is two calls (two legs). Phone audio is **μ-law 8 kHz**.
- **iOS:** no API gives a third-party app the remote caller's audio on a cellular call. VoIP apps have their own raw audio. Apple's call translation in CallKit apps can only be switched on/off (`CXSetTranslatingCallAction`).
- **audeering `wav2vec2-large-robust-24-ft-age-gender`:** age 0–100, gender child / female / male, 318M params, CPU OK, **CC-BY-NC-SA 4.0**.
- **Hibiki-Zero (open source, MIT):** fr / es / pt / de → en only, 3B params, NVIDIA GPU (8 GB VRAM should work, 12 GB safe). Demo: `uvx -p 3.13 hibiki-zero serve`.
- **Qwen3-TTS (open source, Apache 2.0):** 10 languages, voice design from text, 3 s cloning, ~97 ms first audio.
- **Workflow quirks in the cloud sessions** (same repo as agent-controller):
  - Open PRs with `gh api repos/nicorudu/projects/pulls -X POST …`; the GitHub MCP tool returns 404 for this repo.
  - After pushing a new branch, run `git config --add remote.origin.fetch '+refs/heads/<b>:refs/remotes/origin/<b>'`, then fetch and `git branch -u`. Otherwise the stop hook reports "unpushed commits".

## 6. What Nico needs to do
- **Review and merge the kickoff PR (#8).** The README tells your story in first person; edit it however you like.
- **The `projects` repo is public**, so the branch, the PR and your story in the README are already visible. Edit or trim anything you'd rather keep private before merging.
- **Accounts, in the order they're needed:**
  1. **OpenAI API** key with Realtime API access (M1). Set a monthly spend limit.
  2. **ElevenLabs** plan with API access and at least 12 free voice slots for the voice matrix (M2).
  3. **Twilio** account and one phone number (M5). Check what the trial account allows (for example, which numbers it can call) before testing with friends.
- **Don't paste keys into chat or files.** M1 adds a `keys:set` script that asks for each key and stores it in the keychain.
- **Test speakers:** line up a few friends or family (Spanish and English speakers, different ages) who agree to be test callers for M2–M5.
- **Ask your wife** which scenarios and languages matter most for her students' families. It shapes the v1 language list.

## 7. Open questions
- Final name.
- Does ElevenLabs Voice Design produce a convincing light Colombian accent, or only a general Latin American one?
- Is ElevenLabs TTS after `gpt-realtime-translate` fast enough, or does "fast mode" (OpenAI's voice) need to be the phone default?
- Which second engine for wider language coverage (Soniox or another), and which TTS covers those languages well.
- License for the code when the repo goes public.

## 8. Step log (newest first)
- 2026-11-12 — Project kickoff: research, use cases (Nico's family; his wife's classroom), spec, decision log, handoff, build log, showcase.json. Branch `live-interpreter-kickoff`, PR #8.
