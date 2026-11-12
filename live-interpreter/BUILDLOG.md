# Build log — Live Interpreter

Newest first. Each entry covers what changed, why, and links to its docs.

---

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
