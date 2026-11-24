# Mitzi

Glasses with a language tutor inside. They label the things around you in the language you're learning, turn each one into a flashcard that schedules itself, and give you a friend to talk to who can see what you see. First language: Japanese. First learner: me, starting from zero.

**Mitzi** is the name of the glasses and the project. **Suki** is the conversation partner inside them.

## Why I'm building this

My wife's grandmother speaks Japanese, and her English is limited. I'm learning Japanese from zero so I can talk with her in her own language, and I'm building the glasses that teach me. The project is named after her.

There's a bigger reason too. I grew up with Spanish and English, and I believe learning each other's languages brings cultures closer. Many people start a language app and never reach the point of speaking. Mitzi is my attempt to close that gap: a tutor that gets you speaking, in your own home, about your own life.

## Status: planning (Phase 0)

| Area | State |
|---|---|
| Idea | Chosen 2026-11-24 after a wide brainstorm of AR glasses uses |
| Prior work | Checked 2026-11-24 ([research](docs/research.md)) |
| Plan | Five phases written ([plan](docs/plan.md)) |
| Phase 0 | Brief, success measures, risk list, label ladder and Suki's profile written ([phase 0](docs/phase0.md)) |
| Code | Not started. Phase 1 is a phone prototype that proves the learning works before any hardware |
| Hardware | Not started. Own design; research runs alongside Phase 1 |

**Picking the project up?** Start with the [handoff](HANDOFF.md): current step, next step, rules and key facts.

**Follow along:** [Build log](BUILDLOG.md) · [Decision log](docs/decisions.md) · [Plan](docs/plan.md) · [Phase 0](docs/phase0.md) · [Research](docs/research.md)

## How it will work

```
See       look at an object             ─► its word appears, with sound
Keep      the object becomes a card     ─► a scheduler decides when it comes back
Recall    a word is due and you look    ─► the glasses ask, you answer out loud
Use       Suki asks about your day      ─► your due words, in real sentences
Rehearse  "Obaachan mode"               ─► practise the conversations that matter
```

- **Speaking first.** Reading and writing are optional. The top of the learning path is saying the word and using it in a sentence.
- **Labels that fade.** A new word starts as English plus the Japanese sound. As you learn it, the help drops away until there is no label and the glasses just ask "What's this?" Details: [the label ladder](docs/phase0.md#5-the-label-ladder).
- **Your world is the deck.** Every object becomes a flashcard with a photo of *your* object. Scheduling uses FSRS, the open-source scheduler that modern Anki uses.
- **Suki.** A goofy, warm friend from Okinawa who speaks casual, everyday Japanese. She sees what you see, steers the chat toward the words you're due to review, and mixes in English when you're stuck. She corrects by repeating your sentence the right way, as a friend would.
- **Obaachan mode.** Suki plays a grandmother so you can rehearse real family conversations, including the warmer, more polite speech used with elders.
- **Topic packs.** Word sets for what you care about: family, food, lifting, your job. Later, the glasses can switch packs by where you are.
- **Split brain.** The glasses only see, hear, speak and show. The phone does the AI. A self-hosted open model on a home computer is a goal to test.

## What already exists

Research prototypes have shown that labels on real objects beat flashcards for remembering words, and a few have run on headsets. I found no product you can buy, and nothing that combines fading labels, a self-building review deck and a conversation partner who uses your due words, aimed at speaking. Sources: [research](docs/research.md).

## Phases

| # | Phase | What it proves |
|---|---|---|
| 0 | Define and de-risk | We know what we're building, how success is measured and what could sink it |
| 1 | Learning loop on a phone | The method teaches better than plain flashcards, before any hardware |
| 2 | Hardware research (alongside 1) | A display, camera and audio that pass bench tests; architecture chosen |
| 3 | Build the glasses | Ugly rig → printed frame → daily wearable |
| 4 | Validate, share, expand | Other learners, open-source release, a second language, topic packs |

Each phase has a gate that must pass before the next starts. Details: [plan](docs/plan.md).

## Layout

```
mitzi/
├── README.md          this page
├── HANDOFF.md         where we are, what's next, rules — updated after every step
├── BUILDLOG.md        dated progress entries, newest first
├── showcase.json      short summary for the portfolio site (nicorudu.com)
├── docs/
│   ├── plan.md        the five phases and their gates
│   ├── phase0.md      brief, success measures, risks, label ladder, Suki's profile
│   ├── research.md    what exists already (with sources)
│   └── decisions.md   every decision and why
├── prompts/
│   └── suki-v0.md     the prompt for testing Suki in any AI voice app
├── app/               phone prototype (Phase 1)
├── hardware/          optics tests, 3D models, parts lists (Phase 2+)
├── firmware/          code that runs on the glasses (Phase 3)
└── media/web/         images and clips for the website and posts
```

Folders marked with a phase are created when that phase starts.

## Conventions
- **Dates** are `YYYY-MM-DD` everywhere.
- **No camera captures, audio, transcripts or keys** in the repo, ever. Photos of my home and practice recordings stay local.
- **Family privacy.** This repo tells the story in the words above and no more. No names, ages, places, photos or recordings of family members.
- **Public use.** A visible light whenever the camera is on, a quiet mode, and no saving of images of other people.
- **Every step** gets a build log entry, a decision log line if something changed, and an update to `showcase.json` so the website stays current.
