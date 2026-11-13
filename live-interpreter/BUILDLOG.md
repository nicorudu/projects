# Build log — Live Interpreter

Newest first. Each entry covers what changed, why, and links to its docs.

---

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
