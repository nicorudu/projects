# Handoff — Live Interpreter

**Read this first when picking the project back up** (new chat, after a context reset, or switching to the Mac mini). It holds the current state, the next step, and the rules. It is updated and pushed after every step.

Last updated: 2026-11-12 · by Claude (cloud session)

---

## 1. Where we are right now
- **Done:** research, use cases, v0 spec, decision log, free open-source path (Qwen models on the Mac mini, Oracle Always Free VM as the server). Project folder on branch `live-interpreter-kickoff`, PR #8 to `main`.
- **No code yet.**
- **Next step: M1, one-way pipe on the Mac, free path first.** Mic → Qwen3-ASR → Qwen3.5 → Qwen3-TTS (one stock voice) → speakers, all via MLX, with a timestamp at every stage so mouth-to-ear delay is measured. Then the same with `gpt-realtime-translate` once the OpenAI key exists, and compare. Also add a small `keys:set` script that stores API keys in the OS keychain.
- **Not blocked:** the free path needs no accounts. Needs a session on the Mac mini (MLX only runs on Apple Silicon). OpenAI key for the paid half of M1, ElevenLabs for M2, Twilio + Oracle VM for M6 (see §6).

## 2. Milestones

| # | What | Needs | State |
|---|---|---|---|
| M1 | One-way pipe on the Mac, free Qwen path then OpenAI path; latency + memory log | Mac mini; OpenAI key for the paid half | **next** |
| M2 | Matched voice on both paths: phrase chunker → ElevenLabs TTS and Qwen3-TTS; 12-voice matrix each; manual profiles | ElevenLabs for the paid half | planned |
| M3 | Automatic voice profiling (audeering sidecar), voice picker, lock-in + 15 s re-check | — | planned |
| M4 | Web room, two-way: rooms, link + QR, captions, barge-in | — | planned |
| M5 | Launch languages: language router, 8 languages (es, ar, zh, vi, pt, ru, hi, fil), voices per speaker language, native-speaker checks | ElevenLabs for ar / vi / hi / fil unless an open voice passes | planned |
| M6 | Phone bridge: server on the Oracle VM + Tailscale to the Mac mini; Twilio number, outbound flow, two legs, disclosure, barge-in | Twilio, Oracle VM | planned |
| M7 | In-person mode: PWA screen, earbuds routing, half-duplex gate | — | planned |
| M8 | Portfolio polish: README diagram, latency chart, 60 s demo of a real call, showcase update | — | planned |
| v1 | Next-wave languages (Haitian Creole, Hmong, Urdu, Somali, Swahili), meeting recap (opt-in), glossary, inbound calls | — | after v0 |

Details for each: [spec](docs/spec.md) "Build milestones".

## 3. Standing rules (from Nico)
1. **Document everything in GitHub after every step**, and update this handoff, so nothing is lost when the chat compacts.
2. **Website (nicorudu.com):** don't edit it. Write the exact changes for Nico to hand to his website Claude assistant.
3. **Git:** branch first, never commit to `main`. Commit author `nicorudu <nicorudu@users.noreply.github.com>`. Never put Nico's personal email in commits or external requests.
4. **Secrets** (OpenAI, ElevenLabs, Twilio) go in the OS keychain locally and the host's secret store when deployed. Never in the repo.
5. **No audio, transcripts or call logs in the repo**, ever (`.gitignore` covers them).
6. Nico uses an **M4 Mac mini** (main) and an **HP OmniBook X Flip (Windows)**. Code must run on both, except the free-path model server, which uses MLX (Apple Silicon only) in v0.
7. **Voice cloning** is only ever opt-in, and only for the account owner's own voice. Never clone the other person on a call.

## 4. Design in one paragraph
A Node + TypeScript server runs two one-way translation pipelines per conversation (A → B and B → A). Each pipeline turns the speaker's audio into translated text, cuts it into speakable phrases, and speaks them in a voice picked from a pre-designed matrix (sex × age band × output language, with a light accent from the speaker's language). Two interchangeable engines: **paid** (OpenAI `gpt-realtime-translate` + ElevenLabs TTS) and **free** (Qwen3-ASR → Qwen3.5 → Qwen3-TTS, running with MLX on the Mac mini). The server lives on an Oracle Always Free VM and reaches the Mac mini over Tailscale. A Python sidecar guesses sex and age from the first ~4 seconds of speech. Audio gets in and out through transport adapters: Twilio call legs (phone bridge), browser WebSockets (web room, QR join) or the device's own mic and speaker (in person). Captions for both sides are always on.

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
- **Free path (all Apache 2.0, details in [research.md §6](docs/research.md)):**
  - **Qwen3-ASR** 0.6B / 1.7B (2026-01-29): 30 languages + 22 Chinese dialects incl. en / es / ar, language ID, streaming. `pip install qwen-asr`. MLX port 30–36× real time (M5 Pro).
  - **Qwen3.5** small 0.8B / 2B / 4B / 9B (2026-03-02): prompted translator; glossary can go in the prompt.
  - **Qwen3-TTS** 0.6B / 1.7B (2026-01): 10 languages (zh, en, ja, ko, de, fr, ru, pt, es, it); VoiceDesign from a description, Base clones from 3 s; "design then clone" for a fixed voice matrix. MLX RTF ~0.55–0.8, peak ~4–6 GB. On CPU it's slower than real time.
  - **Qwen3.8-LiveTranslate** (2026-09-19): hosted only, no weights. 60 languages in, 29 spoken, keeps the speaker's voice.
- **Launch languages and coverage** (details: [spec "Languages"](docs/spec.md), [research §8](docs/research.md)):
  - Launch set: Spanish, Arabic, Chinese (Mandarin), Vietnamese, Portuguese, Russian, Hindi, Filipino (Tagalog). Picked from NCES fall 2021 English-learner home languages plus Nico's picks.
  - Qwen3-ASR hears all 8. Qwen3.5 translates all 8 as text.
  - Free voice: Qwen3-TTS speaks es / zh / pt / ru only. Chatterbox Multilingual (MIT) adds ar / hi / vi; OmniVoice (Apache 2.0, 600+ languages) is the candidate for fil. Quality to test.
  - Paid voice: ElevenLabs Flash v2.5 speaks all 8. OpenAI `gpt-realtime-translate` outputs 6 of 8 (no ar, no fil). Qwen3.8-LiveTranslate speaks all 8 plus Urdu.
  - Haitian Creole and Hmong (NCES #8 and #9) aren't output by Qwen3-TTS, Chatterbox, ElevenLabs Flash v2.5 or OpenAI, and Qwen3-ASR doesn't hear them. ElevenLabs v3 (74 languages) still to check.
- **Oracle Cloud Always Free Arm:** 2 OCPU / 12 GB total (halved in 2026, enforced 2026-08-18), no GPU. Going over the A1 limit at trial end disables **all** A1 instances. "Out of capacity" errors happen; idle VMs can be reclaimed. Cheapest Oracle GPU (A10) ≈ $2/hour.
- **Workflow quirks in the cloud sessions** (same repo as agent-controller):
  - Open PRs with `gh api repos/nicorudu/projects/pulls -X POST …`; the GitHub MCP tool returns 404 for this repo.
  - After pushing a new branch, run `git config --add remote.origin.fetch '+refs/heads/<b>:refs/remotes/origin/<b>'`, then fetch and `git branch -u`. Otherwise the stop hook reports "unpushed commits".

## 6. What Nico needs to do
- **Review and merge the kickoff PR (#8).** The README tells your story in first person; edit it however you like.
- **The `projects` repo is public**, so the branch, the PR and your story in the README are already visible. Edit or trim anything you'd rather keep private before merging.
- **Tell Claude how much memory (RAM) the Mac mini has.** It decides which Qwen model sizes the free path uses.
- **Accounts, in the order they're needed** (the free path needs none of them until M6):
  1. **OpenAI API** key with Realtime API access (paid half of M1). Set a monthly spend limit.
  2. **ElevenLabs** plan with API access (paid half of M2; also the voice for Arabic, Vietnamese, Hindi and Filipino in M5 if no open voice is good enough). Check how many saved voices the plan allows; the full launch set needs more than 12.
  3. **Oracle Cloud** account (M6). Create one Arm VM (`VM.Standard.A1.Flex`) at **no more than 2 OCPUs and 12 GB**, so it stays free when the trial ends.
  4. **Tailscale** (free for personal use) on the Mac mini and the Oracle VM (M6).
  5. **Twilio** account and one phone number (M6). Check what the trial account allows (for example, which numbers it can call) before testing with friends.
- **Don't paste keys into chat or files.** M1 adds a `keys:set` script that asks for each key and stores it in the keychain.
- **Test speakers:** line up a few friends or family (Spanish and English speakers, different ages) who agree to be test callers for M2–M6. For M5, find one native speaker per launch language to judge the translation and voice.
- **Ask your wife** which languages her students' families actually speak, and which Indian language(s) matter (Hindi is assumed; Urdu, Gujarati, Punjabi or Telugu are also possible).

## 7. Open questions
- Final name.
- Does ElevenLabs Voice Design produce a convincing light Colombian accent, or only a general Latin American one?
- Is ElevenLabs TTS after `gpt-realtime-translate` fast enough, or does "fast mode" (OpenAI's voice) need to be the phone default?
- Is the free Qwen path fast enough on the M4 for live calls, and which model sizes fit in its memory?
- Can Qwen3-TTS VoiceDesign do a believable light Colombian accent in English?
- Are the open voices (Chatterbox Multilingual for ar / hi / vi, OmniVoice for fil) good enough to keep those languages free, or do they need ElevenLabs?
- How to cover Haitian Creole and Hmong (none of the main engines checked handles them yet).
- License for the code (the repo is public, so this matters once code lands).

## 8. Step log (newest first)
- 2026-11-12 — Chose the launch languages (es, ar, zh, vi, pt, ru, hi, fil) from NCES data and Nico's picks; mapped coverage per engine; added a language router and new milestone M5 (old M5–M7 are now M6–M8).
- 2026-11-12 — Added the free path (Qwen3-ASR → Qwen3.5 → Qwen3-TTS on the Mac mini) and Oracle Always Free hosting to the spec, research, decisions and this handoff. M1 now starts with the free path.
- 2026-11-12 — Project kickoff: research, use cases (Nico's family; his wife's classroom), spec, decision log, handoff, build log, showcase.json. Branch `live-interpreter-kickoff`, PR #8.
