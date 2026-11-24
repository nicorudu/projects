# Research — what exists already

Checked 2026-11-24. Short notes with sources, so nothing here needs researching twice.

## 1. Labels on real objects for learning words

| Work | What it is | What it found or showed |
|---|---|---|
| **ARbis Pictus** (UC Santa Barbara, 2017) | A lab study with 52 people. Words were learned from AR labels on real objects, and from flashcards | AR labels won: 7% better recall the same day and 21% better 4 days later. Most people also enjoyed it more. [Paper](https://arxiv.org/abs/1711.11243) |
| **A later paper on automatic labeling** | A system that recognizes objects and labels them automatically | Names the hard part: recognizing objects at scale and keeping their labels consistent. [Paper](https://par.nsf.gov/servlets/purl/10112530) |
| **EARLL** (University of Washington, UIST 2024) | A prototype for AR glasses that watches for the wearer grabbing an object, then shows the foreign word, with optional audio | A demo, with open challenges listed. [Project page](https://makeabilitylab.cs.washington.edu/project/EARLL) |
| **ARLang** (2024) | A phone AR app with bilingual text and sound labels on objects outdoors, for Portuguese; study with 44 people | People preferred the labels over flashcards. [Paper](https://arxiv.org/abs/2411.05211) |
| **Things** (2022) | A hobby app for Android smart glasses: look at an object, see and hear its name. French, Italian, German and Japanese | Working demo, shown at VRTO 2022. [Repo](https://github.com/thisisvaze/things) |

## 2. What that means for Mitzi

- **The base idea is proven and not new.** Labels on real objects help people remember words.
- **No product found** that a learner can buy and wear.
- **The gap:** nothing found combines
  1. labels that fade as each word is learned,
  2. a review deck that builds itself from your own objects,
  3. a conversation partner who sees what you see and uses your due words,
  4. teaching aimed at speaking (and, for Japanese, counters taught on real objects).
- **The known hard problem** is consistent recognition. Mitzi's answer: confirm an object once and pin its label, a "sticker map" of the home.
- **Method to copy:** the ARbis Pictus study design (same learner, AR words vs. flashcard words, recall the same day and days later). Using it makes our results comparable.

## 3. Hardware reference

- **[OpenSource-Ai-Glasses](https://github.com/Iam5tillLearning/OpenSource-Ai-Glasses)** (Apache 2.0): Linux smart glasses on a small single-core chip. Optional one-eye 640×480 display with a 30° view, 1080p camera with live streaming, mic and speaker, motion sensor, Wi-Fi and Bluetooth, 43 g, 180 mAh battery (about 3 hours with the display on). Includes 3D models of the frame. No circuit board files found. **We are not building on this kit;** it is a reference for weight, battery and layout.

## 4. Local models (checked 2026-11-24)

The question: can a huge open model run on the Mac mini (16 GB) and be Suki's brain?

- **Kimi K3** (Moonshot AI, open weights since late July 2026): 2.8 trillion parameters, about 1.56 TB of files, built to be served from GPU clusters.
- **kimi-k3-in-c** ([repo](https://github.com/FareedKhan-dev/kimi-k3-in-c), Apache 2.0) runs the full model on one CPU with a peak of 8.24 GB of RAM by keeping the weights on disk and streaming in only what each token needs. The output is identical to a big-memory run. **The cost is speed: about 33 seconds per token in 8 GB,** and about 10.7 seconds per token with roughly 128 GB. Its own README calls it slow. It is a proof of engineering, not something to talk to.
- **What that means for Mitzi:** a 30-token reply would take about 16 minutes. Ruled out for live conversation. It is also a text model, so it was never a candidate for the listening test.
- **The realistic route:** models small enough to work at speaking pace. One to test: **Kimi-Linear 48B**, reported at about 9 tokens per second with an 8 GB memory budget from a 19 GB file, using the [WASTE](https://github.com/sqliteai/waste) streaming engine ([report](https://huggingface.co/moonshotai/Kimi-K3/discussions/148)). That figure is someone else's machine; measure it on the Mac mini.
- **Our bar for a self-hosted brain:** first words within a second or two, then faster than talking pace.

## 5. Still to research (Phase 1 and 2)
- Which vision, speech and conversation models to use, cloud and self-hosted.
- Small display modules and optics that can be bought in single units.
- Camera, mic and wireless chips used in current smart glasses.
