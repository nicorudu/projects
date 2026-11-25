# Suki test log

Phase 0 test of risk 2: can a total beginner learn from a character like Suki? Sessions run in an existing AI voice app with the prompt in `prompts/`. Newest first. No transcripts or personal details here, only findings.

---

## Session 2 — 2026-11-25 (prompt v1, same chat)

**What happened.** Suki opened with the Okinawan hello and a four-word review of session 1, then built one new verb around what Nico was doing (writing code): the plain form, the negative, and a question. She closed with a polite "Grandma version."

**What worked**
- **Prompt v1 held.** Review first, four new items listed at the end (the cap is five), his wife called by her name, an Okinawan word for the week, a polite version at the close.
- **All four review words came back a day later:** one clean, two with a slip in one sound (as transcribed), one after a first-syllable hint.
- **First grammar by contrast.** One verb in two forms, *kaku* (write) and *kakanai* (don't write). He produced the negative correctly in a sentence, then picked the wrong one of the two for himself and fixed it after one prompt. He is choosing between forms, which is the "Use it" rung again.
- **She pulled him back to Japanese** each time he answered in English, without stopping the chat.
- **She reported what she received** ("I got …") and asked once, as v1 asks.
- **No Japanese errors found** on review. A native-speaker check is still to come.

**What didn't**
1. **The transcript mangles his Japanese.** Words arrived in English-looking spellings, split or joined in the wrong places (two words fused, one word split, a greeting turned into English words). The opening greeting took three turns for this reason.
2. **Length is invisible, and she confirmed it anyway.** Three corrections turned on a long vowel or a doubled consonant (*dorobō*, *ippai*, *iie*). When his retry still came through short, she accepted it as right. Short *ie* is a different word ("house"). A transcript can't settle this, so she shouldn't call it right.
3. **"No" was taught as *iie* only.** It is correct, and right for polite speech, but between friends the usual word is *uun*. A casual partner should give both.
4. **A little over the limits.** One question ran to five words (the limit is four). Counting both verb forms and the polite form, new material was closer to six items than four.
5. **Not recorded:** which voice language setting was used, and Nico's four notes.

**What this changes**
- **Prompt v1.1** (three lines, in [prompts/suki-v1.md](../prompts/suki-v1.md)): for words that differ only in length, say it slowly once and move on without judging; give the casual and the polite word when they differ; hold new sentences to four words, questions included.
- **Evidence for the Phase 1 listening test:** a recognizer that expects English turns beginner Japanese into English-looking fragments. The test must compare recognizers on exactly this, and on Japanese and English mixed in one turn.
- **For the native-speaker check:** *iie* vs. *uun*, and *kōdo o kaku* for "write code."

**Score so far on risk 2:** promising after two sessions. He is producing short sentences and switching verb forms. The weak link is the hearing, not the teaching.

## Session 1 — 2026-11-24 (about 10 minutes, parked car, prompt v0)

**What happened.** Starting from one object (the car), Nico built and said full sentences within ten minutes: "my car is blue," "her car is blue too," "lots of cars," and "I'm going to pick up my wife." Thirteen new items in total.

**What worked**
- **Objects led to sentences on day one.** One noun (*kuruma*, car) grew into possession (の), a topic (は), "also" (も), a color and a verb phrase. This is the "Use it" rung working, and early evidence against the biggest risk (that labels only teach nouns).
- **Her questions came from his surroundings:** the car, the parking lot, where he was going next.
- **A running joke carried the repetition.** One silly word came back five times without feeling like a drill.
- **The Spanish bridge landed:** *pero* for the r, Spanish vowels for *aoi* and *mukae*.
- **No Japanese errors found** in her lines on review. A native-speaker check is still to come.
- **She ended the session when he was about to drive.**

**What didn't**
1. **Too much new material.** Thirteen items against a rule of one at a time. The last sentence (*tsuma o mukae ni iku*) was too long for a first day and didn't stick.
2. **She can't hear him; she reads a transcript.** His speech reached her as text ("zuma," "kamseki," "mm"). She then corrected sounds, and once praised a pause before a doubled consonant, none of which text can show. A wrong sound and a wrong transcription look the same to her. **Pronunciation feedback from a transcript can't be trusted.**
3. **No review loop yet.** Nothing brings today's words back tomorrow unless the same chat is reused.
4. **Small slips:** one repeated praise line; no Okinawan greeting (the prompt never asked for it).
5. **Family register.** She taught *tsuma* ("my wife"), which is right in general. Talking to his wife's own grandmother, he'd use his wife's name.

**What this changes**
- **New product requirement:** pronunciation feedback must come from the audio itself (a model that hears sound, or a scoring step on the recording), never from a transcript. This goes into the Phase 1 spec and widens the listening test.
- **Prompt v1** ([prompts/suki-v1.md](../prompts/suki-v1.md)): a review at the start, at most five new items, honesty about what she can't hear, a polite "Grandma version" of the day's best sentence, the Okinawan greeting.
- **To record next time:** which voice language setting was used, and how the session felt (the pass mark is "I look forward to it").

**Score so far on risk 2:** promising. She understood most of his Japanese and he was forming sentences. One session is not a week.
