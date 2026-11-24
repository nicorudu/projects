# Phase 0 — Define and de-risk

Written 2026-11-24. What we're building, how we'll know it works, what could sink it, and the two designs that everything else hangs on: the label ladder and Suki.

---

## 1. One-page brief

**Why this exists.** My wife's grandmother speaks Japanese, and her English is limited. I want to hold a real conversation with her in her own language, and then be ready to visit Japan. I'm starting from zero.

**The product.** Glasses with a tutor inside. They label the things around you in Japanese, turn each one into a flashcard that schedules itself, and give you a friend to talk to who can see what you see and steers the chat toward the words you need to practise.

**The promise.** "The tutor that gets you speaking." Speaking and understanding come first. Reading and writing are optional extras.

**First learner.** Nico: native in Spanish and English, zero Japanese, wants casual, natural speech.

**North-star goal.** By **2027-05-24** (6 months): a sustained casual conversation with her, about 10 minutes, on familiar topics (family, food, her life, mine), mostly in Japanese, with no interpreter.

**The core loop.**
1. **See:** look at an object, get its word (text and sound).
2. **Keep:** the object becomes a card with a photo of *your* object. A scheduler decides when it comes back.
3. **Recall:** when a word is due and you look at that object, the glasses ask you for it. You answer out loud.
4. **Use:** Suki asks about what you're doing, using your due words in real sentences.
5. **Rehearse:** Obaachan mode lets you practise the conversations you want to have.

**What makes it new.** Research prototypes label objects. None found combines fading labels, a self-building review deck and a conversation partner who uses your due words, all aimed at speaking. See [research](research.md).

**In scope for v1.** Japanese only. One learner. Home first, then public in quiet mode. The phone does the AI; the glasses see, hear, speak and show.

**Out of scope for v1.** Kanji and writing practice, other languages, other learners, a custom circuit board, AI running on the glasses themselves.

**The rule that protects the goal.** The learning does not wait for the build. Japanese practice happens every day from day 1, with whatever tools exist that day.

---

## 2. Names

- **Mitzi:** the glasses and the project, named after my wife's grandmother.
- **Suki:** the conversation partner. 好き (*suki*) means "like" or "love," a good first word to learn.

---

## 3. How success is measured (set before any testing)

### The goal: a real conversation
| When | Target |
|---|---|
| Week 2–3 | Greet her and introduce myself in Japanese (about 30 seconds) |
| Month 1 | 2 minutes: greetings, how are you, food, a few questions. Kana learned. About 150 words |
| Month 2 | 3–5 minutes with Suki on daily life. About 400 words |
| Month 3 | 5 minutes with her on family and food, with some help. About 700 words |
| Month 6 | 10+ minutes with her, mostly Japanese. About 1,500 words |

Word counts are starting targets, to be adjusted after the first 2 weeks of real data.

**Monthly check.** One real conversation each month. Measure minutes sustained in Japanese and how many times English was needed.

### The product: does the loop help?
| Measure | Target |
|---|---|
| Recall after 4 days and 2 weeks: words learned through labels and Suki vs. words learned through plain Anki | Labels and Suki win |
| Minutes of spoken Japanese per day | 15+ in month 1, 30+ by month 3 |
| Share of Suki's speech that is Japanese | About 30% in month 1, rising to about 90% by month 6 |
| Wrong or inconsistent labels at home | Fewer than 1 in 20 |
| Delay from looking at an object to seeing its label | About 1 second |
| Days used per week | 5 or more |

---

## 4. Assumptions that could sink it, and a cheap test for each

| # | Assumption | Why it matters | Cheap test | Pass mark |
|---|---|---|---|---|
| 1 | Object words lead to conversation | Labels teach nouns. Conversation needs verbs and sentence patterns. The biggest risk | The "Use it" rung (section 5) and Suki. At week 4, describe 10 objects in full sentences | 7 of 10 correct |
| 2 | An AI partner works for a total beginner | She may overwhelm, or speech recognition may not understand beginner Japanese | Needs no build: paste the [Suki prompt](../prompts/suki-v0.md) into an AI voice app, 10 minutes a day for a week | I look forward to it, and she understands me most of the time |
| 3 | The AI teaches correct, natural casual Japanese | Mistakes or stiff phrasing would be learned as truth | A native speaker spot-checks 30 phrases and one transcript | Fewer than 2 problems in 30 |
| 4 | Friend-style Japanese transfers to an elderly speaker | Older speakers may use older words, regional words and a different pace | An early real hello (week 2–3); tune Obaachan mode to what I hear | I catch the gist of simple questions by month 2 |
| 5 | Labels help before I know kana | A zero-level learner can't read the labels | Week 1: labels with romaji and sound, plus a kana sprint in parallel | Hiragana in 1 week, katakana in 2 |
| 6 | Recognition is accurate and consistent at home | A wrong label teaches a wrong word | Walk the house with the phone: 100 objects, count errors. Fix: confirm an object once and pin its label | Under 5 wrong before pinning, 0 after |
| 7 | A self-hosted model is good and fast enough | Decides cloud vs. home computer | Same 50 photos and one 5-minute chat through both. Compare accuracy and delay | Local within reach of cloud on both |
| 8 | A home-built display can show the labels clearly | Optics are the hardest hardware part | Bench test with kana only. The display is required: if a home-built one falls short, buy a module. An audio-only rig is only an interim step | Kana readable at a glance indoors |
| 9 | I'll wear them daily, including in public | Comfort, battery, other people's reactions | Phase 3 wear trial, with the public rules below | 5+ days a week for 2 weeks |
| 10 | The build won't eat the learning time | Building is more fun than studying | The daily-practice rule. Log practice minutes and build hours | Practice never skipped for building |

**Rules for public use:** a visible light whenever the camera is on, a quiet mode (labels and whispered audio, no talking), and no saving of images of other people.

---

## 5. The label ladder

Built for speaking. Each word climbs on its own, based on how well it's recalled.

| Rung | What you get | Example |
|---|---|---|
| 0. Meet | English, romaji and sound | cup · *koppu* 🔊 |
| 1. Kana | Kana, small romaji, sound | コップ *koppu* 🔊 |
| 2. Kana only | Kana; sound on request | コップ |
| 3. Say it | No label. The glasses ask, you answer aloud | 「これ、何？」 (*Kore, nani?* "What's this?") |
| 4. Use it | A short phrase with a verb; then Suki asks about it and you answer in a sentence | コーヒーを飲む (*kōhī o nomu*, "drink coffee") |
| Optional | Kanji with small reading hints, off by default | 水 (みず, water) |

**How words move.** Up after correct recalls spaced further apart; down a rung after a miss. Scheduling uses FSRS, the open-source scheduler that modern Anki uses.

**Design notes**
- **The Spanish advantage.** Japanese vowels (a, i, u, e, o) sound almost like Spanish vowels, and the Japanese "r" is close to the soft Spanish r in *pero*. Pronunciation hints lean on Spanish sounds, not English ones.
- **Easy early wins.** Many household words came from English and are written in katakana: テレビ (*terebi*, TV), テーブル (*tēburu*, table), ドア (*doa*, door), ベッド (*beddo*, bed), スプーン (*supūn*, spoon). The house starts with these.
- **Length matters.** Long vowels and doubled consonants change meaning. おばさん (*obasan*) is "aunt"; おばあさん (*obaasan*) is "grandmother." Suki corrects length from day 1.
- **Counters come at rung 4.** Counting uses different words for long things, flat things and small things, shown on real objects in view.

---

## 6. The conversation partner: Suki

**Who she is.** 26, from Naha, Okinawa. Helps at her family's small soba shop and has picked up English from customers. Loves food, karaoke and the beach. Very close to her own grandmother (her *obaa*), which gives her natural reasons to talk about family and about speaking with elders.

**Personality.** Goofy, warm, a little teasing, quick to laugh at herself. A friend, not a teacher. Relaxed island attitude; her motto is the Okinawan saying *nankurunaisa* ("it'll work out"). She greets you with *haitai*, the Okinawan hello that women use, and teaches a few Okinawan words along the way.

**How she talks**
- Standard, casual, everyday Japanese. Short sentences. Slow at first, faster as the learner improves. Light on current slang, so the Japanese works with every generation.
- **When the learner is stuck:** say it in Japanese, say it slower, swap the key word to English, explain in English, return to Japanese. Mixing languages is allowed, the way Spanglish works.
- Spanish for pronunciation tips when it helps.
- One new thing at a time.

**How she corrects.** She never says "wrong." She repeats the sentence back the right way, as a friend would, and moves on. After the same miss three times, she stops for a 20-second explanation.

**What she remembers.** Due words, past chats, the learner's day and goal, and the things they want to be able to say.

**She stays one person.** Topic packs change what she talks about, not who she is. She doesn't become an engineer for one learner and a nurse for another; she gets curious about the learner's world and supplies the missing words.

**Her modes**
| Mode | What it does |
|---|---|
| Friend (default) | Casual chat about whatever the learner is doing or looking at |
| Obaachan | She plays a grandmother for rehearsing real conversations: slower, older-style speech from her, warm polite speech from the learner. Includes call-style practice |
| Drill | Quick spoken quizzes on due words |
| Quiet | For public: labels and whispered audio only |
| Work (later) | She plays a coworker or client, with the formal speech work needs |

**Why Obaachan mode matters.** Japanese changes with who you're talking to. Friends use casual speech. Toward an elder in-law, warm polite speech (the です/ます style) is the usual choice, and the elder will often answer casually. So the learner needs to **understand casual** and **speak polite to elders**. Plan: casual core from day 1, family phrases in polite form from week 2. Each family knows what feels right for them.

**Sample**
> **Suki:** ニコ、おはよう！コーヒー飲んでる？ (*Niko, ohayō! Kōhī nonderu?* "Morning, Nico! Having coffee?")
> **Nico:** はい… コーヒー… 飲む。 (*Hai… kōhī… nomu.*)
> **Suki:** いいね！コーヒー飲んでるんだ。 *Nonderu* means you're drinking it right now. もう一回？ (*Mō ikkai?* "One more time?")

---

## 7. Topic packs

Word sets built around what the learner cares about.

- **First pack: "Talking with Grandma."** Family, food, simple talk about work and home, where I grew up, questions about her life.
- **Second pack: lifting,** since that's what I'd talk about with a friend.
- **Later (Phase 4):** packs by interest or industry, such as business or AI engineering. Many tech and business words in Japanese are borrowed from English, like ミーティング (*mītingu*, meeting) and ループ (*rūpu*, loop), so those packs start with quick wins. Packs also decide which objects get labeled first, and can switch by location.

---

## 8. Phase 0 to-do list

- [ ] Start hiragana; katakana the week after.
- [ ] Run the Suki prompt 10 minutes a day for 7 days. Note what works and what annoys.
- [ ] Find a native speaker to spot-check Suki's Japanese.
- [ ] Plan the first hello (week 2–3).
- [ ] Record a "day zero" video for the content series.
- [x] Project folder, README and handoff in the repo.

**Gate to Phase 1:** Suki tested for a week, kana under way, first hello planned.
