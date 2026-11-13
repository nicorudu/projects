# Live Interpreter

Talk to anyone, in any language, in real time. You speak your language; the other person hears you in theirs, in a natural voice that sounds like the same kind of person (same sex, similar age, a light version of your accent). It works on a regular phone call to any phone, in a shared web room, or face to face.

Working name.

## Why I'm building this

I'm from Colombia. Growing up, my parents often couldn't communicate with my teachers, coaches and community leaders, the people who had important information for our family. My wife is a teacher, and she sees the same problem from the other side: students arrive from all over the world, and when she can't communicate well with them and their families, they do less well than they could.

Both sides want the conversation to happen. This project is my attempt to make it possible in real time, with a voice that feels human, and with nothing for the other person to install. More in [use cases](docs/use-cases.md).

## Status: planning

| Area | State |
|---|---|
| Spec | v0 written ([spec](docs/spec.md)) |
| Research | Engines, phone-call access, voices and costs checked 2026-11-12 ([research](docs/research.md)) |
| Code | Not started. Next: M1, a one-way Spanish → English pipe on the Mac, free path first, with latency measured |
| Accounts | None for the free path. OpenAI API and ElevenLabs for the paid path, Twilio for phone calls, Oracle Cloud for hosting (see [handoff](HANDOFF.md) §6) |

**Picking the project up?** Start with the [handoff](HANDOFF.md): current step, next step, rules and key facts.

**Follow along:** [Build log](BUILDLOG.md) · [Decision log](docs/decisions.md) · [Spec](docs/spec.md) · [Use cases](docs/use-cases.md) · [Research](docs/research.md)

## How it will work

```
You speak Spanish ─► server ─► live translation ─► matched voice (English) ─► they hear English
They speak English ─► server ─► live translation ─► matched voice (Spanish) ─► you hear Spanish
```

- **Phone bridge:** phones don't let apps tap into carrier calls, so the server sits in the middle. It calls you, then calls them (Twilio), and only passes translated speech between the two calls. They just answer their phone.
- **Web room:** share a link or QR code; each person talks through a browser. Good for in-person meetings with two devices.
- **In person:** one phone, you in earbuds, them on the speaker.
- **Two engines, same app:**
  - **Free path:** open Qwen models on a Mac mini. Qwen3-ASR hears, Qwen3.5 translates, Qwen3-TTS speaks. A free Oracle Cloud VM is the public server.
  - **Paid path:** OpenAI `gpt-realtime-translate` with ElevenLabs voices.
  - Both sit behind adapters, so ElevenLabs Realtime Translation, Qwen LiveTranslate or Hibiki-Zero can be swapped in later.
- **Voice:** a small model guesses the speaker's sex and age in the first seconds; the app picks a pre-designed voice of the same kind, with a light accent from the speaker's language.
- **Languages:** built with English ↔ Spanish first, then the launch set: Spanish, Arabic, Chinese, Vietnamese, Portuguese, Russian, Hindi and Filipino. Next: Haitian Creole, Hmong, Urdu, Swahili and Somali.

## Layout

```
live-interpreter/
├── README.md          this page
├── HANDOFF.md         where we are, what's next, rules — updated after every step
├── BUILDLOG.md        dated progress entries, newest first
├── showcase.json      short summary for the portfolio site (nicorudu.com)
├── docs/
│   ├── spec.md        the v0 plan: modes, architecture, voice matching, milestones, tests
│   ├── use-cases.md   who it's for and the requirements that come from that
│   ├── research.md    what exists, engines, phone access, voices, costs (with sources)
│   └── decisions.md   every decision and why
├── server/            Node + TypeScript: transports, engines, TTS, session control (M1+)
├── modelserver/       Python + MLX on the Mac mini: Qwen3-ASR, Qwen3.5, Qwen3-TTS for the free path (M1)
├── client/            Vite + TypeScript PWA (M4+)
├── profiler/          Python sidecar: speaker sex/age estimate (M3)
├── voices/            voice matrix: IDs + the prompts that made them (M2)
├── prompts/           key prompts used during the build
└── media/web/         images and clips for the website and posts
```

Folders marked with a milestone are created when that milestone starts.

## Conventions
- **Dates** are `YYYY-MM-DD` everywhere.
- **No audio, transcripts, call logs or keys** in the repo, ever. Test recordings stay local.
- **Every milestone** gets a build log entry, a decision log line if something changed, and an update to `showcase.json` so the website stays current.
