# Build log — Live Interpreter

Newest first. Each entry covers what changed, why, and links to its docs.

---

## 2026-11-19 — Plan version 1.1: Spanish first, phone before languages
- Nico answered the plan's open questions.
- **v0 is English ↔ Spanish only.** Spanish is the largest language gap in US schools. The other seven languages (M5) come right after v0.
- **The phone call comes first.** Build order is now M0–M4, M6 (phone bridge), M7, M8, then M5.
- **The Mac mini has 16 GB**, so the free path starts with the smallest model of each kind (an estimated 12–15 GB in total). If that doesn't fit, the fallback is a hybrid: hear and translate on the Mac, speak with ElevenLabs.
- **Pace and budget:** 3–4 sessions a week puts v0 at an estimated 4–7 weeks. The $150 cap is approved.
- Details: [plan](docs/plan.md).

## 2026-11-19 — Audit and formal plan
- **Kickoff merged.** PR #8 is on `main`.
- **Went through every doc and re-checked the facts a week later.** What changed:
  - ElevenLabs released Eleven v4 Turbo (90+ languages, about 100 ms). It replaces Flash v2.5 as the paid voice.
  - Qwen3-ASR can't stream on a Mac, so the free path translates phrase by phrase after each short pause. The paid path still translates while you talk.
  - Google's Gemini 3.5 Live Translate (70+ languages) was missing from the research. It's now a candidate paid engine.
  - OmniVoice (600+ languages, runs on Apple Silicon) might replace two free voice models with one. It joins the M2 comparison.
  - Twilio's trial is tighter than assumed: 30 days, verified numbers only, 10 minutes a call. Start it only at M6.
  - ElevenLabs voice slots: 30 on the $22 Creator plan, which the first 12 voices need.
- **New first milestone, M0:** the scaffold and an automated test with fake engines. No hardware or accounts needed.
- **Formal plan written** ([plan](docs/plan.md)): what v0 means, scope, who does what, milestones with exit tests, six decision gates, schedule (18–26 sessions), budget (about $20 free-path only, about $110 with both paths, $150 cap proposed) and risks.
- Next: Nico answers the plan's open questions, then M0.

## 2026-11-12 — Launch languages chosen
- **Launch set:** Spanish, Arabic, Chinese (Mandarin), Vietnamese, Portuguese, Russian, Hindi and Filipino (Tagalog). Nico picked Spanish, Hindi, Vietnamese and Filipino; Arabic, Chinese, Portuguese and Russian are among the most common home languages of US English learners (NCES, fall 2021).
- **Coverage:** the free path hears and translates all 8. Its voice (Qwen3-TTS) speaks only Spanish, Chinese, Portuguese and Russian, so Arabic, Vietnamese, Hindi and Filipino will try open voices first (Chatterbox Multilingual, OmniVoice) and fall back to ElevenLabs.
- **New milestone M5 (launch languages)** after the web room; phone bridge, in-person and polish move to M6–M8.
- **Next wave:** Haitian Creole, Hmong, Urdu, Swahili, Somali. Haitian Creole and Hmong need engines we haven't found yet.
- Details: [spec "Languages"](docs/spec.md), [research §8](docs/research.md).

## 2026-11-12 — Free path and Oracle hosting added to the plan
- **Free, fully open-source path:** Qwen3-ASR (hears 30 languages) → Qwen3.5 small model (translates) → Qwen3-TTS (speaks 10 languages, designs and clones voices). All Apache 2.0, running on the Mac mini with MLX. Same adapters as the paid path, so every call can use either.
- **Oracle Cloud:** the Always Free Arm VM (now 2 OCPU / 12 GB, no GPU) becomes the free public server for Twilio and web rooms. It's too small to run the models live, so they stay on the Mac mini behind a Tailscale tunnel.
- **M1 now starts with the free path**, since it needs no accounts, then adds the OpenAI path and compares speed side by side.
- Only phone-bridge minutes (Twilio) still cost money on the free path.
- Details: [spec "Free path"](docs/spec.md), [research §6–7](docs/research.md).

## 2026-11-12 — Project started
- **The idea:** speak your language on a call or face to face, and the other person hears you live in theirs, in a realistic voice of the same sex and age with a light accent.
- **Why:** Nico's parents struggled to talk with his teachers and coaches growing up; his wife, a teacher, sees the same gap with students and families from around the world. See [use cases](docs/use-cases.md).
- **Research** ([notes](docs/research.md)):
  - Phones don't let apps get carrier-call audio, so calls go through a Twilio bridge on our server.
  - ElevenLabs Realtime Translation is the ideal engine but enterprise-only for now.
  - OpenAI's `gpt-realtime-translate` (May 2026) is self-serve at $0.034/min but outputs only 13 languages and has no voice choice, so we pair its translated text with ElevenLabs voices.
  - Open-source path for later: Kyutai Hibiki-Zero (translation with voice transfer) and Qwen3-TTS (voice design).
- **Spec written** ([spec](docs/spec.md)): three modes, architecture, voice matching, latency budget, costs, 7 milestones, test plan.
- **Decisions logged** ([decisions](docs/decisions.md)).
- Next: M1, a one-way Spanish → English pipe on the Mac.
