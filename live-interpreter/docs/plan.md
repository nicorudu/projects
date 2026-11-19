# Live Interpreter — Project Plan

Version 1, 2026-11-19. Owner: Nico. This is the plan of record: what gets built, in what order, how we know each step is done, and where the decisions are. The technical design is in the [spec](spec.md); the reasons behind it are in [use cases](use-cases.md), [research](research.md) and [decisions](decisions.md).

## 1. Goal

Two people who don't share a language hold a natural two-way conversation, on a regular phone call, through a web link or face to face. Each hears the other in their own language, in a realistic voice of the same sex and age with a light accent. The other person installs nothing.

It's a portfolio project first. The use case that drives it is families and schools: parents who can't talk with teachers and coaches, and teachers who can't reach their students' families.

## 2. What "done" means for v0

v0 is complete when all of these are true:

1. A 5-minute English ↔ Spanish **phone call** to a regular phone works, and neither person has to repeat themselves more than once or twice.
2. A **web room** joined by QR code works on two devices, with captions for both sides.
3. The translated voice matches the speaker's sex and age band for at least 8 of 10 test speakers.
4. The listener starts hearing the translation within 2 seconds on a phone call (measured, with logs).
5. A **free path** (open models on the Mac mini) and a **paid path** (OpenAI + ElevenLabs) both run behind the same app, and their speed is measured side by side.
6. At least Spanish is approved by native speakers; each other launch language ships only when a native speaker has approved it.
7. The repo has a README with a diagram, real latency numbers and a 60-second demo video of a real translated call.

## 3. Scope

| In v0 | Not in v0 |
| --- | --- |
| Phone bridge (outbound), web room with QR join, in-person mode | Inbound calls to an interpreter number, three-way calls |
| English ↔ Spanish, then the launch set: Arabic, Chinese, Vietnamese, Portuguese, Russian, Hindi, Filipino | Haitian Creole, Hmong, Urdu, Swahili, Somali (next wave) |
| Voice matched by sex, age band and light accent | Cloning anyone's actual voice |
| Free path and paid path, switchable per call | ElevenLabs Realtime Translation (enterprise only), native iPhone or Android apps |
| Captions for both sides, spoken disclosure on calls | Meeting recap, school glossary screen, accounts, payments |
| One user (Nico) running it | Other people signing up to use it |

## 4. Approach in brief

- **Two engine paths.** Free: Qwen3-ASR hears, Qwen3.5 translates, Qwen3-TTS (or OmniVoice) speaks, all on the Mac mini. Paid: OpenAI `gpt-realtime-translate` translates and ElevenLabs speaks.
- **Two interpreting styles.** The paid path translates while the person is still talking. The free path waits for a short pause and translates that phrase.
- **Three ways in.** Twilio phone bridge, browser web room, in-person screen. All feed the same pipeline.
- **Hosting.** A free Oracle Cloud VM is the public server. It reaches the Mac mini over a private Tailscale connection.

## 5. Who does what

| Who | Does |
| --- | --- |
| **Nico** | Decides at each gate, creates accounts and keys, keeps the Mac mini available, judges Spanish quality, recruits testers, records the demo |
| **Claude in cloud sessions** | Research, docs, server code, automated tests, pull requests. Anything that needs no microphone, speaker or Mac |
| **Claude Code on the Mac mini** | The model server (MLX), microphone and speaker tests, latency and memory measurements |
| **Testers** | Spanish and English speakers of different ages (M2–M6); one native speaker per launch language (M5); Nico's wife for the school scenarios and feedback |

The free-path model server only runs on Apple Silicon, so M1's free half needs the Mac mini. The Windows laptop can run the server, the client and the paid path.

## 6. Milestones

A session is one focused sitting of 2–3 hours. Estimates are rough and will be corrected after M1.

| # | Milestone | Delivers | Done when | Runs on | Needs | Sessions |
| --- | --- | --- | --- | --- | --- | --- |
| **M0** | Scaffold | Repo layout, adapter interfaces, phrase chunker, resampler, pause detection, timing logger, fake engines | An automated test runs a recorded clip through the whole pipeline with fake engines and writes a timing log | Cloud | Nothing | 1–2 |
| **M1** | One-way pipe, two engines | Speak Spanish, hear English, on the free path and then the paid path | Both paths work on the Mac with delay and memory measured side by side | Mac mini | Mac mini; OpenAI key for the paid half | 2–3 |
| **M2** | Matched voice | Voice matrix for both paths; Qwen3-TTS vs. OmniVoice comparison; manual profiles | A listener who hasn't heard the speaker guesses their sex and rough age from the translated voice; delay stays in budget | Mac mini | ElevenLabs for the paid half | 2–3 |
| **M3** | Automatic voice profiling | Sex and age guessed from the first seconds; voice picked and locked | 10 test speakers get a sensible voice with no setup | Mac mini + cloud | Test speakers | 1–2 |
| **M4** | Web room, two-way | Rooms, link and QR join, both directions, captions, interruption handling | A 5-minute English ↔ Spanish conversation between two rooms feels usable | Mac mini + cloud | A Spanish-speaking tester | 3–4 |
| **M5** | Launch languages | Language router, 7 more languages, voices per speaker language | A native speaker of each language approves translation and voice in a 3-minute web-room talk | Mac mini + cloud | Native-speaker testers; ElevenLabs if open voices fail | 3–4 |
| **M6** | Phone bridge | Server on the Oracle VM, Tailscale link, Twilio outbound flow, disclosure | A 5-minute call to a Spanish-speaking friend's regular phone works | Oracle VM + Mac mini | Oracle, Tailscale, Twilio accounts | 3–4 |
| **M7** | In-person mode | Phone screen, earbud routing, echo control, big captions | A face-to-face exchange works without the speaker feeding back into the translator | Mac mini + phone | Earbuds | 1–2 |
| **M8** | Portfolio polish | README diagram, latency chart from real logs, demo video, showcase entry, site notes | Everything in section 2 is true | Cloud | Demo recording | 2 |

**Order.** M0 to M4 in sequence. After M4, M5 and M6 can swap or overlap: M5 waits on native-speaker testers, M6 doesn't. M7 and M8 close it out.

**Three points worth showing publicly:**

- **Demo 1** (after M4): two people talking through a web link, English ↔ Spanish.
- **Demo 2** (after M6): a real translated phone call. This is the headline.
- **v0 complete** (after M8).

## 7. Decision gates

Each gate is a short stop where Nico decides, with the measurements in front of him.

| Gate | When | Decision | Decided by |
| --- | --- | --- | --- |
| **G1** | End of M1 | Which path is the default. Free wins if the listener hears the translation within 2.0 s of the phrase ending and Nico judges the Spanish ↔ English translation good. Otherwise paid is the default and free stays an option. Also: which Qwen model sizes fit the Mac's memory | Delay and memory logs; Nico's ear |
| **G2** | End of M2 | Which free voice model (Qwen3-TTS or OmniVoice). Whether a light Colombian accent is achievable. Whether the ElevenLabs subscription is worth keeping | Blind listening test |
| **G3** | End of M4 | Publish Demo 1? Do M5 or M6 next? | Tester availability |
| **G4** | During M5, per language | Does this language ship, and with which voice (open or ElevenLabs) | Native speaker's rating |
| **G5** | Start of M6 | Hosting (Oracle VM if one can be created, otherwise a fallback host), Twilio upgrade, disclosure wording | Setup results |
| **G6** | End of M8 | Code license, portfolio page, what to post | Nico |

## 8. Schedule

Total estimate: **18–26 sessions**. Calendar time depends on how many sessions a week fit around the other projects.

| At this pace | Demo 1 (after M4) | Demo 2 (after M6, if M6 goes before M5) | v0 complete |
| --- | --- | --- | --- |
| 2 sessions a week | 5–7 weeks | 6–9 weeks | 9–13 weeks |
| 1 session a week | 9–14 weeks | 12–18 weeks | 18–26 weeks |

These are estimates, not commitments. M1 is the first real data point; the table gets redone after it.

## 9. Budget

Running cost per conversation minute, from list prices checked 2026-11-19:

| | Web room or in person | Phone call |
| --- | --- | --- |
| **Free path** | $0 | about $0.04 (Twilio only) |
| **Paid path** | about $0.11 (OpenAI $0.068 + ElevenLabs about $0.04) | about $0.14 |

Estimated cost of building v0:

| Item | When | Cost |
| --- | --- | --- |
| Oracle Cloud VM, Tailscale, open models | M1 onward | $0 |
| OpenAI API | Paid half of M1 onward | About $20 for 5 hours of test conversations |
| ElevenLabs Creator plan (30 voice slots) | M2 to M5, only while testing the paid voice | $22 a month |
| Twilio | M6 onward | $20 top-up covers about 9 hours of bridged calls, plus $1.15 a month for the number |
| **Total, free path only** | | **About $20** |
| **Total, both paths over 3 months** | | **About $110** |

Proposed cap: **$150** for the whole build, with spend limits set in each account. ElevenLabs can be cancelled after G2 if the open voices win.

## 10. Accounts and setup

Create each account when its milestone starts, not before. Twilio's trial in particular lasts only 30 days.

| Account | Needed for | Notes |
| --- | --- | --- |
| None | M0, free half of M1 | |
| OpenAI API | Paid half of M1 | Needs Realtime API access. Set a monthly limit |
| ElevenLabs | Paid half of M2 | Creator plan for the 30 voice slots; Starter (10 slots) isn't enough for 12 voices |
| Oracle Cloud | M6 | One Arm VM at no more than 2 OCPUs and 12 GB, so it stays free |
| Tailscale | M6 | On the Mac mini and the VM |
| Twilio | M6 | Trial: verified numbers only, 10 minutes a call, US only. Upgrade for real tests |

Keys never go in chat or in the repo. M0 includes a script that stores them in the system keychain.

## 11. Risks

| Risk | Chance | Effect | What we do |
| --- | --- | --- | --- |
| Free path is too slow on the Mac mini | Medium | Free path can't be the default | Smaller models and shorter pauses first; G1 decides; the paid path is already built |
| Models don't fit the Mac's memory together | Unknown until RAM is known | Free path needs smaller models | Measure in M1; fall back to the 0.6B and 4B sizes |
| Light accent sounds fake or stereotyped | Medium | The "sounds like you" promise weakens | G2 listening test; default to a neutral voice if it fails |
| Wrong dates, times or amounts in translation | Medium | Real harm in a school conversation | Captions always on; native-speaker checks; number read-back in v1 |
| Open voices are poor in Arabic, Vietnamese, Hindi or Filipino | Medium | Those languages cost money | ElevenLabs fallback per language (G4) |
| Oracle free VM can't be created ("out of capacity") or gets reclaimed | Medium | No free public server | Retry in another region; fallback host at a few dollars a month (G5) |
| Mac mini asleep or offline during a call | Medium | Free-path call fails | Fall back to the paid path automatically, or fail with a clear message |
| Voice guess is wrong on phone audio | Medium | Wrong voice on calls | Set the other person's profile before the call |
| Not enough testers, especially native speakers | High for some languages | M5 stalls | M5 doesn't block M6; ship languages one at a time |
| Prices or access change (preview models, plans) | Medium | Budget or design shifts | Engines sit behind adapters; re-check research at each gate |
| Other projects take the time | High | Schedule slips | Demo 1 is a complete, showable result on its own |

## 12. Quality and testing

- Every milestone has a "done when" test (section 6). It isn't done until that test passes and the build log says so.
- Automated tests cover the parts that don't need a person: chunker, resampler, codec, voice picker, language router, and a full pipeline run with fake engines.
- Delay is logged at every stage for every phrase from M1 on. Charts in M8 come from those logs.
- People judge what machines can't: translation quality, voice match, accent, whether a conversation feels natural. The scenarios are in the spec's test plan.

## 13. Privacy and responsible use

1. No audio is stored. Logs hold timings and events; text only if both people agree.
2. Every phone call starts with a spoken notice, in the listener's language, that an AI is interpreting.
3. Only call people who expect the call.
4. No one's voice is cloned except, later and by choice, the account owner's own.
5. Not for legal, medical or formal school proceedings; those need a professional interpreter.
6. Test recordings stay on the test machine and never enter the repo.

## 14. How we work

- Every step ends with a commit on a branch, a pull request, a build log entry and an updated [handoff](../HANDOFF.md).
- Decisions go in the [decision log](decisions.md) the day they're made.
- This plan gets a new version at each gate if the estimates or order change.
- Website changes for nicorudu.com are written up for the website assistant, not made from here.

## 15. Next actions

| # | Action | Who | Needs |
| --- | --- | --- | --- |
| 1 | Answer the open questions below | Nico | |
| 2 | M0 scaffold as a pull request | Claude, cloud session | Nico's go-ahead |
| 3 | M1 free half on the Mac mini | Nico + Claude Code on the Mac | M0 merged |
| 4 | Create the OpenAI key, then M1 paid half | Nico, then Claude Code | Action 3 |
| 5 | G1 review with the measurements | Nico + Claude | Actions 3 and 4 |

## 16. Open questions for Nico

1. How much memory (RAM) does the Mac mini have?
2. How many sessions a week can this project get?
3. Is the $150 cap right?
4. Which languages do the families at your wife's school speak, and which Indian language(s)?
5. Should M6 (phone) come before M5 (languages)? The plan assumes whichever has testers ready.
