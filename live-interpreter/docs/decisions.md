# Decision log

One line per decision: what, why, and what it replaced. Newest first.

| Date | Decision | Why | Replaces |
|---|---|---|---|
| 2026-11-12 | Wider language coverage is the first priority after v0 | The school use case includes families who speak languages outside `gpt-realtime-translate`'s 13 outputs (e.g. Arabic, Haitian Creole) | — |
| 2026-11-12 | Captions always on, for both sides | Dates, amounts and names must be catchable when the translation is wrong | — |
| 2026-11-12 | The other person never needs an app (phone bridge for any phone, QR code for web rooms) | Families may have no smartphone, no app, no account | — |
| 2026-11-12 | In-person meetings use a two-device QR web room by default | One shared phone on speaker feeds translated audio back into the mic | Single shared phone only |
| 2026-11-12 | Secrets in the OS keychain locally, the host's secret store when deployed | Same rule as other projects: no keys in the repo or in committed files | `.env` file |
| 2026-11-12 | First language pair English ↔ Spanish | The founding use case, and every engine considered supports it | — |
| 2026-11-12 | Voice matching from a pre-designed ElevenLabs voice matrix (2 sexes × 3 ages per output language, light accent) | Similar voice was the goal, not the same voice; no generation during a call keeps latency down | Voice cloning |
| 2026-11-12 | Speaker sex/age guessed by audeering's wav2vec2 age/gender model in a Python sidecar | Open model, runs on CPU; manual profile overrides it | — |
| 2026-11-12 | Use `gpt-realtime-translate` transcript deltas + ElevenLabs TTS; keep OpenAI's own audio as "fast mode" | The OpenAI model has no voice selection; fast mode gives a latency baseline | OpenAI voices only |
| 2026-11-12 | Translation engine for v0: OpenAI `gpt-realtime-translate`, behind an adapter | Self-serve, streaming, $0.034/min; ElevenLabs Realtime Translation is enterprise-only | — |
| 2026-11-12 | Phone calls go through a Twilio bridge (two legs, one bidirectional Media Stream each) | No phone OS lets an app get carrier-call audio; the server in the middle can | Native call integration |
| 2026-11-12 | Three modes: phone bridge, web room, in person | Covers calls, meetings and face-to-face with one pipeline | — |
