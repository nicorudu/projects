# Use cases — Live Interpreter

Why this project exists, who it's for, and what that means for the build. Started 2026-11-12.

## Where it comes from

Two stories started it:

- **Nico's family.** Nico is from Colombia. Growing up, his parents often couldn't communicate with his teachers, coaches and community leaders, the people with important information for the family. Important things were missed or arrived late.
- **Nico's wife, a teacher.** She sees the same thing from the other side: students arrive from many parts of the world, and when she can't communicate well with them or their families, the students do less well than they could.

Both sides of the same conversation want it to happen. What's missing is a way to have it in real time, in a voice that feels like a person, without either side needing special equipment or an interpreter booked days ahead.

## Who uses it

| Person | Speaks | Wants | Has |
| --- | --- | --- | --- |
| **Parent or family member** | Their home language (Spanish first) | To understand what the school, coach or program needs, and to ask questions back | Any phone. Maybe no smartphone, no app, no account |
| **Teacher** | English | To reach a family quickly about grades, behavior, forms, schedules | School phone or own phone, a laptop in the classroom |
| **Newcomer student** | Their home language | To understand class instructions and be understood | Often a school device |
| **Coach / program leader** | English | To share schedules, costs, permission forms, safety info | Own phone |
| **Community leader** (church, clinic front desk, city program) | English | To explain a process or deadline | Own phone or laptop |

## Scenarios

| # | Scenario | Mode | What has to work |
| --- | --- | --- | --- |
| 1 | Teacher calls a parent about a missing assignment | Phone bridge | Parent answers a normal call and hears the teacher in Spanish; teacher hears the parent in English |
| 2 | Parent-teacher conference in the classroom | Web room via QR code | Parent scans, picks Spanish, listens on their own phone; both see captions |
| 3 | Coach explains tournament travel and costs after practice | In person or QR web room | Numbers, dates and amounts come through exactly |
| 4 | Newcomer student's first day | Web room or in person | Short, simple exchanges; teacher can repeat or rephrase |
| 5 | Parent calls the school with a question (v1) | Phone bridge, inbound | Parent calls one number and is connected with translation |
| 6 | Community event or meeting (later) | Web room, one speaker to many listeners | Each listener picks their language |

## Requirements these drive

1. **The other side needs nothing.** No app, no account, no smartphone required. Phone bridge for any phone; QR web room for in-person meetings.
2. **It must sound human.** A natural voice of the same sex and roughly the same age, with a light accent, so it feels like talking to a person, and the listener can tell the words are being interpreted.
3. **Accuracy beats speed on what matters.** Dates, times, amounts, names and forms must come through exactly. Captions on both sides in v0; "repeat that" and number read-back later.
4. **Fast enough for real back-and-forth.** Under 2 seconds from speaking to hearing on a phone call (target).
5. **Language coverage beyond Spanish.** Launch set: Spanish, Arabic, Chinese, Vietnamese, Portuguese, Russian, Hindi and Filipino. Next wave: Haitian Creole, Hmong, Urdu, Swahili and Somali. Chosen from the most common home languages of US English learners plus Nico's picks; see the spec's "Languages" section.
6. **Privacy by default.** No audio stored. Any recap or transcript is opt-in for both people. A disclosure at the start of every call.
7. **Simple for the person starting it.** Pick a language, enter a number or show a QR code, talk.

## What this is not (for now)

- Not a replacement for a professional interpreter in legal, medical or formal school proceedings.
- Not a school-approved tool. Schools have their own student-privacy rules (in the US, FERPA) and usually contracted interpreter services. v0 is a personal prototype and portfolio project.

## How we'll know it works

- A real 5-minute English ↔ Spanish phone call where neither person has to repeat themselves more than once or twice.
- A mock parent-teacher conference where the "parent" joins by QR in under 30 seconds and leaves knowing the key dates and next steps.
- Feedback from Nico's wife on whether it would help with her students and their families, and what's missing.
