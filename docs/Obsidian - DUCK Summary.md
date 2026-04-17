# D.U.C.K – What We're Attempting

**XR Dynamic User Context Kit** — MR system on Meta Quest 3 that shows real-time personal and interpersonal biomarkers (heart rate, posture, sweat, voice, face) to study how that affects behavior.

## In one line
Put on the headset → see your (and optionally others’) biodata in MR → understand how that changes how you act (end goal: **NeuroSwarm**).

## Phases
1. **Phase 1** – Build and validate each sensor/feature (HR, posture, sweat, auditory, facial).
2. **Phase 2** – Pipe everything into one MR experience on Quest 3.
3. **Phase 3** – Run a study on how access to this biodata changes social interaction.

## Stack
- **MR:** Unity, C#, Meta SDK / OpenXR, Quest 3.
- **Posture:** Arduino (e.g. LilyPad), C++; code in `arduino/`.
- **ML:** CNN (face), RNN (voice); pre-trained where possible.
- **Flow:** Sensors → computer → Quest 3 for display.

## Principles
- UI minimal; “put on head and it works” for MVP.
- Ethics first: consent and anonymization for any collected data.

---
*From D.U.C.K project docs. See `PROJECT.md`, `ProjectProposal.md`, `PlanOverview.md` for full detail.*
