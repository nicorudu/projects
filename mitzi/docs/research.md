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

## 4. Still to research (Phase 1 and 2)
- Which vision, speech and conversation models to use, cloud and self-hosted.
- Small display modules and optics that can be bought in single units.
- Camera, mic and wireless chips used in current smart glasses.
