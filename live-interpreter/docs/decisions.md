# Decision log

One line per decision: what, why, and what it replaced. Newest first.

| Date | Decision | Why | Replaces |
|---|---|---|---|
| 2026-11-12 | Voices are chosen by the speaker's language (6 per language: sex × age band, light accent), then speak any output language | The voice models are multilingual; avoids a separate matrix per language pair | 6 voices per output language |
| 2026-11-12 | A language router picks hear / translate / speak engines per language: Qwen3-ASR + Qwen3.5 for all; Qwen3-TTS for es / zh / pt / ru; open voice or ElevenLabs for ar / vi / hi / fil | No single engine speaks all 8 for free; Qwen3-TTS covers 4 of them | One engine for everything |
| 2026-11-12 | Launch languages (new M5, after the web room): Spanish, Arabic, Chinese, Vietnamese, Portuguese, Russian, Hindi, Filipino. Build and tune with Spanish first | Top NCES English-learner languages plus Nico's picks (Hindi, Filipino); Haitian Creole and Hmong lack engine support for now | English ↔ Spanish only |
| 2026-11-12 | M1 builds the free path first, then the OpenAI path, and compares them | The free path needs no accounts, so work can start right away; the comparison decides the default | M1 = OpenAI only |
| 2026-11-12 | Server hosted on an Oracle Cloud Always Free Arm VM (≤ 2 OCPU / 12 GB); models stay on the Mac mini, reached over Tailscale | Free, always-on public address for Twilio and web rooms; 2 Arm cores with no GPU are too slow to run the voice models live | Fly.io / Render |
| 2026-11-12 | Add a free, fully open-source path: Qwen3-ASR → Qwen3.5 → Qwen3-TTS on the Mac mini (MLX), behind the same adapters as the paid path | Nico wants a version that costs nothing to run; all three are Apache 2.0, and Qwen3.5 can take a glossary in its prompt | Paid APIs only |
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
