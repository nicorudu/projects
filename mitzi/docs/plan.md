# Plan — Mitzi

Five phases, each with a gate that must pass before the next one starts. Written 2026-11-24.

## The idea in one paragraph
Glasses that act as a language tutor living in your world. They label the objects around you in the language you're learning, and the labels fade as you learn the words. Every object you meet becomes a flashcard that schedules itself. A conversation partner, Suki, sees what you see and works the words you're due to review into natural conversation. First language: Japanese. First learner: Nico, starting from zero.

**Mission:** get people to actually speak another language, because language brings cultures closer.
**Promise:** "The tutor that gets you speaking."

## The rule that protects the goal
The learning does not wait for the build. Japanese practice happens every day from day 1 with whatever tools exist that day. The build makes the practice better over time; it never gates it.

---

## Phase 0 — Define and de-risk (2–3 weeks)
Decide exactly what we're building and what could sink it, before spending on parts. Full write-up: [phase0.md](phase0.md).

**Deliverables**
1. One-page brief.
2. Success measures, set before any testing.
3. Riskiest assumptions, each with a cheap test.
4. The label ladder (how a label changes as a word is learned).
5. Suki's profile and a test prompt.
6. Repo folder, README, handoff, content plan.

**Gate to Phase 1:** Suki tested in an AI voice app for a week, kana under way, first real hello planned.

---

## Phase 1 — Prove the learning loop on a phone (4–6 weeks)
Software only. The phone stands in for the glasses: its camera sees, earbuds speak.

**Build**
- **See:** phone camera → object recognition → a label at the word's current ladder rung, plus spoken audio.
- **Keep:** every new object becomes a card automatically, using the photo of *your* object. Scheduling with FSRS. An evening review screen, like Anki.
- **Pin:** confirm an object once and its label is fixed (a "sticker map" of the home), so labels stay consistent.
- **Recall:** when a due word's object is in view, quiz on the spot. Answer out loud; speech-to-text checks the answer.
- **Use:** a voice conversation with Suki, who sees the camera view, speaks slowly and works due words into the chat.
- **Modes:** Friend, Obaachan, Drill, Quiet.
- **First topic pack:** "Talking with Grandma" (family, food, simple talk about work and home, questions about her life).
- **Japanese extras:** counters, taught on real objects in view.
- **Log everything:** labels shown, wrong labels, reviews, recall, minutes spoken.
- **Model test:** the same 50 photos and one 5-minute chat through a cloud model and through a self-hosted open model on the Mac mini. Compare accuracy and delay. Models are chosen at the start of this phase.

**Self-experiment (2–4 weeks):** split a word list in half. Learn one half through labels and Suki, the other half through plain Anki. Test recall at 4 days and at 2 weeks.

**Gate to Phase 3:** label-and-Suki words are recalled better than Anki-only words, and Nico still wants to use it after 2 weeks. If not, fix the loop before building hardware.

---

## Phase 2 — Hardware research (alongside Phase 1)
Understand how smart glasses are built and choose an architecture. No final parts yet.

**Study**
- Existing smart glasses and open designs: weight, battery, display size, where each part sits. [OpenSource-Ai-Glasses](https://github.com/Iam5tillLearning/OpenSource-Ai-Glasses) is a useful reference (43 g, 180 mAh battery, 640×480 one-eye display); we are not building on that kit.
- Optics basics: how a small display reaches the eye (beam splitter, birdbath, prism, waveguide) and which are realistic to build. Waveguides are not a home build; plan to buy a small display module or use a simple beam splitter.

**Starting architecture: split brain.** The glasses see, hear, speak and show (camera, mic, speaker, small display, wireless chip, battery). The phone does the AI. This keeps the glasses light, cheap and cool.

**Bench tests**
- Display: kana readable at a glance, indoors and in daylight. Kana have simpler shapes than kanji, which lowers the bar.
- Camera: frames good enough for recognition through the phone.
- Audio: Suki is clear to the wearer and quiet to people nearby.
- Wireless: delay from camera frame to label on the display.

**Fallback:** audio-first glasses that whisper the word, if the display proves too hard.

**Targets to set:** weight, battery life (a 1–2 hour session), brightness limits, battery protection, nothing hot against the face. No prescription lenses in v1.

**Gate to Phase 3:** architecture chosen; display, camera and audio each pass a bench test.

---

## Phase 3 — Build the glasses
- **P1, the ugly rig:** parts on a headband or an existing frame, wired, connected to the Phase 1 app. Goal: it works on a head.
- **P2, printed frame:** a 3D-printed frame holding all the parts; wireless; first real wear test.
- **P3, daily wearable:** comfortable enough for a 2-week trial at home and in public. Repeat the Phase 1 measurements on the glasses.
- **Later:** custom circuit board (outsourced), better optics, a charging case.

**Public rules from the first wear test:** a visible light whenever the camera is on, quiet mode, no saving of images of other people.

**Gate to Phase 4:** worn most days for 2 weeks, and the learning results hold up.

---

## Phase 4 — Validate, share, expand
- **Small study:** 3–5 other beginners, the same split-word design, written up like a science fair paper.
- **Open-source release:** code, 3D files, parts list, build guide.
- **Second language** to prove the method generalizes.
- **Topic packs:** word sets by interest or industry (business, engineering, lifting, cooking, travel). Suki stays one person and gets curious about your world; a **work mode** lets her play a coworker or client for rehearsing, with the formal speech work needs. Packs also change which objects get labeled first, and can switch by location.
- **Family version:** a shared sticker map of a home, for families keeping a heritage language alive.

---

## Content plan (for new builders, inventors and AI fans)
- **Series hook:** "I'm learning Japanese from zero with glasses I'm building myself."
- **One episode per gate:** the idea and research, day zero, Suki's first week, the phone prototype, the first recall results, the first display test, the ugly rig, the printed frame, the first full conversation.
- **Recurring segment:** a Japanese check-in every 2 weeks, so viewers watch the progress.
- **Privacy:** family members appear only if they want to.
