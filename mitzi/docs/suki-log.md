# Suki test log

Phase 0 test of risk 2: can a total beginner learn from a character like Suki? Sessions run in an existing AI voice app with the prompt in `prompts/`. Newest first. No transcripts or personal details here, only findings.

---

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
