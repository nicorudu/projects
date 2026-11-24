# Build log — Mitzi

Newest first. Each entry covers what changed, why, and links to its docs.

---

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
