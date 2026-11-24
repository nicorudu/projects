# Decision log

One line per decision: what, why, and what it replaced. Newest first.

| Date | Decision | Why | Replaces |
|---|---|---|---|
| 2026-11-24 | The full Kimi K3 is ruled out as Suki's self-hosted brain; test small open models that fit in 16 GB instead | It runs in 8 GB only by streaming 1.56 TB from disk, at about 33 seconds per token; a short reply would take many minutes. It is also a text model, so it was never a candidate for speech recognition | Running the full compressed model on the Mac mini |
| 2026-11-24 | Mitzi's speech recognition is picked by a listening test in Phase 1; the Wispr Faux app stays untouched (any reuse works from a copy) | A tutor must hear beginner speech as spoken and handle mixed languages, the opposite of dictation cleanup; a bigger model costs speed, and speed matters most in conversation | Upgrading Wispr Faux to a larger model for the prototype |
| 2026-11-24 | Every model sits behind an adapter; cloud and self-hosted are interchangeable | Mitzi is not a wrapper around one chat app. The model is a replaceable part; the eyes, deck, ladder, Suki's memory, modes and measurements are the product | One fixed AI provider |
| 2026-11-24 | The Phase 0 Suki test runs in an existing AI voice app | A no-build way to learn whether a beginner can learn from a character like Suki; it is a test, not the product | Building the voice loop first |
| 2026-11-24 | Topic packs: word sets by interest or industry. First pack "Talking with Grandma," then lifting; industry packs in Phase 4 | People stick with a language when they can talk about what they care about; the first learner's goal is family conversation | One general word list |
| 2026-11-24 | Suki stays one person across topic packs; a separate work mode handles job role-play | A character who changes jobs per learner stops feeling real; work also needs formal speech | Suki takes on the learner's industry |
| 2026-11-24 | Public project, with family privacy: the README story only; no names, ages, places, photos or recordings of family | The story is the reason for the project, and family members didn't sign up to be public | — |
| 2026-11-24 | Names: Mitzi (glasses and project), Suki (conversation partner) | The project is named after the grandmother it's for; the partner gets her own name | One name for both |
| 2026-11-24 | Suki teaches standard everyday Japanese, light on current slang, plus a few Okinawan words | The Japanese has to work with every generation; the Okinawan words are part of her character | — |
| 2026-11-24 | Obaachan mode: Suki plays a grandmother for rehearsal | Speech toward elders is more polite than speech between friends; the learner must understand casual and speak polite | Friend mode only |
| 2026-11-24 | Casual speech first; polite family phrases from week 2 | Sounding natural matters more than sounding like a textbook; elders still get polite speech | Polite speech first |
| 2026-11-24 | Mixed-language help is allowed when the learner is stuck | It's how bilingual people really help each other (Spanglish) | Japanese only, or English only |
| 2026-11-24 | Speaking and understanding first; kanji optional and off by default | The goal is conversation, not reading | Ladder ending in kanji only |
| 2026-11-24 | The label ladder ends at "say it" and "use it" (a phrase with a verb) | Nouns alone don't make conversation | Ladder of English → kana → kanji |
| 2026-11-24 | Daily practice never waits for the build | The goal has a deadline; the build is slower than the learning | Learn once the glasses exist |
| 2026-11-24 | Prove the learning loop on a phone before building hardware | Cheap test of the method; avoids building glasses around a method that doesn't teach | Hardware first |
| 2026-11-24 | Phone prototype on iPhone | It's the phone in hand | — |
| 2026-11-24 | Split brain: glasses see, hear, speak, show; phone does the AI | Keeps the glasses light, cheap and cool | AI on the glasses |
| 2026-11-24 | Cloud AI is acceptable; a self-hosted open model on the Mac mini is tested in Phase 1 | Cloud is fastest to start; self-hosting is a goal if it's good and fast enough | — |
| 2026-11-24 | Audio-first glasses are the fallback if the display proves too hard | The partner and the review loop work without a display | Display required |
| 2026-11-24 | Own glasses design, not the OpenSource-Ai-Glasses kit | The point is to learn to design and build the hardware; that kit has no board files | Building on the kit |
| 2026-11-24 | No prescription lenses in v1 | The first learner doesn't need them day to day | — |
| 2026-11-24 | Scheduling with FSRS | Open source, and what modern Anki uses | Writing our own scheduler |
| 2026-11-24 | First language Japanese; first learner Nico, from zero | The founding reason for the project | — |
| 2026-11-24 | Idea chosen: language-immersion glasses | Picked from a wide brainstorm of AR glasses uses (medical, skills, everyday, global) | — |
