# Build log — Mitzi

Newest first. Each entry covers what changed, why, and links to its docs.

---

## 2026-11-24 — First Suki session
- **Ten minutes, total beginner, full sentences.** Starting from one object (the car), Nico said "my car is blue," "her car is blue too" and "lots of cars." Objects led to sentences on day one, which is early evidence against the biggest risk.
- **Too much, too fast:** 13 new items; the last, longest sentence didn't stick.
- **The big finding:** Suki reads a transcript, so she can't hear pronunciation. She corrected and praised sounds that text can't show. New requirement: pronunciation feedback comes from the audio itself.
- **Prompt v1** written: review first, at most 5 new items, honesty about what she can't hear, a polite "Grandma version" at the end.
- Details: [Suki log](docs/suki-log.md), [prompt v1](prompts/suki-v1.md).

## 2026-11-24 — Two rules set; Phase 0 week begins
- **Outcome first:** every model and part is chosen by measured results. Phase 1 starts on the best cloud models; a self-hosted model takes over a job only when it meets the same bar.
- **Audio and visual, both:** the glasses have a display and audio. Audio-only is allowed only as an interim prototype.
- **Nico starts his Phase 0 week:** daily sessions with Suki, hiragana, a day-zero video.
- Details: [decisions](docs/decisions.md), [handoff](HANDOFF.md).

## 2026-11-24 — Checked the "Kimi K3 in 8 GB" claim
- **Real, and far too slow for us.** kimi-k3-in-c runs the full 2.8-trillion-parameter model in 8.24 GB of RAM by streaming 1.56 TB of weights from disk, at about 33 seconds per token. A short reply from Suki would take many minutes.
- **Ruled out** as a self-hosted brain for live conversation. It's a text model, so it also leaves the listening-test list.
- **Kept:** the idea behind it. Small open models that fit in 16 GB go into the Phase 1 model test, starting with Kimi-Linear 48B through a streaming engine.
- Details and sources: [research §4](docs/research.md).

## 2026-11-24 — Architecture rule, listening test, brainstorm log
- **Not a wrapper.** Every model (vision, listening, conversation, voice) sits behind an adapter, so cloud and self-hosted models can be swapped. What's ours: the eyes and the sticker map, the self-building deck, the label ladder, Suki's memory and due-word steering, the modes, the topic packs, the measurements and the glasses.
- **Suki test this week** runs in an existing AI voice app with the [Suki prompt](prompts/suki-v0.md). It's a no-build test of whether a beginner can learn from her.
- **Listening test added to Phase 1.** Mitzi must hear beginner Japanese as spoken and handle mixed Japanese and English. Candidates: a copy of the Wispr Faux engine with cleanup off, Qwen3-ASR, and newer compressed full-size models. Wispr Faux itself is not changed.
- **Brainstorm log** written: every idea considered and why this one won ([brainstorm](docs/brainstorm.md)).
- Details: [plan, Phase 1](docs/plan.md), [decisions](docs/decisions.md).

## 2026-11-24 — Phase 0 written; topic packs added
- **Brief and goal:** a 10-minute, mostly-Japanese conversation by 2027-05-24, starting from zero. Speaking and understanding first; kanji optional.
- **Success measures** set before any testing: conversation milestones by month, plus product measures (recall vs. plain Anki, minutes spoken, wrong labels, label delay, days used).
- **Ten assumptions that could sink it,** each with a cheap test. The biggest: object labels teach nouns, and conversation needs verbs. Answer: a top rung on the ladder where each word is used in a phrase, and Suki at the centre of the product.
- **Label ladder:** English and romaji → kana → kana only → say it → use it.
- **Suki:** 26, from Okinawa, a goofy friend who speaks casual everyday Japanese, mixes in English when the learner is stuck and corrects by repeating the sentence the right way. Modes: Friend, Obaachan, Drill, Quiet; Work later.
- **Topic packs:** word sets by interest or industry. "Talking with Grandma" first, lifting second, industry packs in Phase 4. Suki stays one person across packs.
- **Rule:** daily practice never waits for the build. The Suki prompt works today in any AI voice app ([prompt](prompts/suki-v0.md)).
- Details: [phase 0](docs/phase0.md), [decisions](docs/decisions.md).
- Next: a week with Suki, then the Phase 1 spec for the phone prototype.

## 2026-11-24 — Project started
- **The idea:** glasses that label the things around you in the language you're learning, build a flashcard deck from your own objects, and give you a conversation partner who sees what you see.
- **Why:** Nico's wife's grandmother speaks Japanese and her English is limited. He's learning from zero to talk with her in her own language. The project is named after her.
- **How it was chosen:** a wide brainstorm of AR glasses uses (medical, passing on skills, everyday life, global needs). Language immersion won because it's personal, buildable and passes the test for glasses: your eyes and hands stay on the world.
- **Research** ([notes](docs/research.md)): lab studies show AR labels beat flashcards (21% better recall after 4 days in one study); a few prototypes exist; no consumer product found; nothing found combines fading labels, a self-building deck and a conversation partner.
- **Plan** ([plan](docs/plan.md)): five phases with gates. The learning loop is proven on a phone before any hardware is built.
- **Hardware:** own design. An open-source glasses kit was reviewed as a reference and set aside.
