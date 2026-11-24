# Handoff — Mitzi

**Read this first when picking the project back up** (new chat, after a context reset, or switching computers). It holds the current state, the next step, and the rules. It is updated and pushed after every step.

Last updated: 2026-11-24 · by Claude (cloud session)

---

## 1. Where we are right now
- **Done:** idea chosen, prior work checked, five-phase plan, Phase 0 write-up (brief, success measures, 10 risks with tests, label ladder, Suki's profile, topic packs), Suki test prompt, decision log. Project folder on branch `mitzi-kickoff`, PR #13 to `main`.
- **No code and no hardware yet.**
- **We are in Phase 0.** What's left is Nico's side (section 6): a week of talking with Suki in an AI voice app, starting kana, and planning the first real hello.
- **Next step for Claude: the Phase 1 spec** (`docs/phase1-spec.md`): the phone prototype's screens, data model, model choices (cloud and self-hosted) with sources, milestones and tests. Write it once Nico has a few days of Suki notes, so the spec uses what he learned.

## 2. Phases

| # | What | Needs | State |
|---|---|---|---|
| 0 | Define and de-risk: brief, measures, risks, ladder, Suki | Nico's week with Suki | **in progress** |
| 1 | Learning loop on an iPhone: see, keep, pin, recall, use; modes; first topic pack; self-experiment vs. plain Anki; cloud vs. self-hosted model test | Phase 0 gate | planned |
| 2 | Hardware research alongside Phase 1: optics, display, camera, audio and wireless bench tests; architecture | — | planned |
| 3 | Build: ugly rig → printed frame → daily wearable | Phase 1 and 2 gates | planned |
| 4 | Validate with 3–5 learners, open-source release, second language, industry topic packs, family version | Phase 3 gate | after v1 |

Gates and details: [plan](docs/plan.md).

## 3. Standing rules (from Nico)
1. **Document everything in GitHub after every step**, and update this handoff, so nothing is lost when the chat compacts.
2. **Website (nicorudu.com):** don't edit it. Write the exact changes for Nico to hand to his website Claude assistant.
3. **Git:** branch first, never commit to `main`. Commit author `nicorudu <nicorudu@users.noreply.github.com>`. Never put Nico's personal email in commits or external requests.
4. **Family privacy.** This repo is public. The story is told in the README's "Why I'm building this" and nowhere in more detail. Never add a family member's name, age, origin, home, history, photo or recording to the repo, the website or posts. Family details live in Nico's private notes.
5. **No camera captures, audio, transcripts or keys in the repo**, ever (`.gitignore` covers them). Photos of the home and practice recordings stay local.
6. **Parts lists** give exact products, exact specifications and exact quantities. Nico orders exactly what is written.
7. **The learning never waits for the build.** Daily Japanese practice comes first; no step of the plan may block it.
8. **Public use:** a visible light whenever the camera is on, quiet mode, no saving of images of other people.
9. Nico works on builds from an **HP OmniBook X Flip (Windows)** and also has an **M4 Mac mini (16 GB)**. The phone is an **iPhone**.
10. **After planning each build step, plan its content too** (for new builders, inventors and AI fans).

## 4. Design in one paragraph
Mitzi is a pair of glasses that only sees, hears, speaks and shows; a phone does the AI. The camera's view goes to a vision model that names the object in front of the learner. Each object becomes a card with the learner's own photo, scheduled with FSRS. A label for the object appears at that word's current rung of a ladder: English and romaji, then kana, then no label and a spoken quiz, then use in a phrase. Confirmed objects are pinned so their labels stay consistent. Suki, a voice conversation partner with a fixed character, sees the same view and knows which words are due, and works them into casual conversation, mixing in English when the learner is stuck and correcting by repeating the sentence the right way. Modes change the situation: Friend, Obaachan (rehearsing talk with an elder), Drill, Quiet (public) and later Work. Topic packs choose the words. Everything is logged so the method can be compared against plain flashcards.

Full detail: [plan](docs/plan.md) · [phase 0](docs/phase0.md) · [research](docs/research.md) · [decisions](docs/decisions.md) · [build log](BUILDLOG.md).

## 5. Key facts (so they don't need re-researching)
Checked 2026-11-24. Sources are in [research.md](docs/research.md).
- **AR labels beat flashcards** in the ARbis Pictus lab study (52 people): 7% better recall the same day, 21% better after 4 days.
- **Closest prior work:** EARLL (grab an object, see its word; AR glasses prototype), ARLang (phone AR, outdoors), Things (hobby smart-glasses app with Japanese). No consumer product found.
- **Known hard problem:** consistent object recognition. Our answer: pin labels after one confirmation.
- **Reference hardware** (not our base): OpenSource-Ai-Glasses, 43 g, 180 mAh, one-eye 640×480 display, about 3 hours with the display on, Apache 2.0, 3D frame files but no board files found.
- **Goal date:** 2027-05-24, a 10-minute, mostly-Japanese conversation.
- **Learner:** native Spanish and English, zero Japanese. Spanish vowels and the soft r carry over to Japanese.
- **Models are not chosen yet.** Pick vision, speech and conversation models at the start of Phase 1, with a fresh check of what's current. Test a self-hosted open model on the Mac mini (16 GB) against a cloud model.
- **Workflow quirks in cloud sessions** (same repo as the other projects):
  - Open PRs with `gh api repos/nicorudu/projects/pulls -X POST …` if the GitHub tool returns 404 for this repo.
  - After pushing a new branch, run `git config --add remote.origin.fetch '+refs/heads/<b>:refs/remotes/origin/<b>'`, then fetch and `git branch -u`.

## 6. What Nico needs to do
- **Merge the kickoff PR (#13).**
- **Talk with Suki 10 minutes a day for 7 days.** Paste [prompts/suki-v0.md](prompts/suki-v0.md) into an AI voice app. After each session, note: did she understand you, was the pace right, one thing that worked, one thing that annoyed you.
- **Start hiragana now,** katakana the week after.
- **Plan the first hello** for week 2–3: a greeting and a short self-introduction.
- **Find a native speaker** who can spot-check Suki's Japanese (30 phrases and one transcript).
- **Record a "day zero" video** before any Japanese is learned.
- **Website:** give your website chat this: "Add Mitzi to the Lab section. Use `mitzi/showcase.json` in github.com/nicorudu/projects for the title, tagline, status text and timeline. Status text: Planning: idea, research and Phase 0 done; phone prototype next. Use the story exactly as written in showcase.json and don't add family details."

## 7. Open questions
- Which AI voice app works best for the Suki test (decide after trying one).
- Cloud vs. self-hosted models (decided by the Phase 1 test).
- Display type for the glasses (decided by the Phase 2 bench tests).
- Whether family members want to appear in any content.

## 8. Step log (newest first)
- **2026-11-24:** Project started. Brainstorm → idea → research → plan → Phase 0 write-up → repo folder and kickoff PR.
