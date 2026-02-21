# D.U.C.K – Project Plan

## What it is
D.U.C.K (XR Dynamic User Context Kit) is an MR system that investigates how real-time visualization of personal and interpersonal physiological data, delivered through a Meta Quest 3 headset, affects user behavior in social settings and everyday tasks. It processes biomarker data from multiple sensors and cameras and streams it into the headset to deliver an intuitive, minimally intrusive interface.

## Goals
- Phase 1: Implement and validate each sensor/feature (heart rate, posture, sweat, auditory, facial).
- Phase 2: Integrate all data into a single MR ecosystem and display it cohesively on the Quest 3.
- Phase 3: Run a social/behavior study on how access to this biodata changes user interaction (NeuroSwarm end goal).

## Tech stack
- **Platform:** Meta Quest 3 (mixed reality), Unity for the MR app.
- **MR/VR:** Unity, Meta SDK (OpenXR), Meta Quest 3 as hub.
- **Language:** C# (Unity/Quest app), C++ (Arduino for posture sensor).
- **ML:** CNN for facial expression recognition, RNN for auditory emotion; pre-trained models where possible.
- **Hardware/firmware:** Arduino (e.g. LilyPad) for DIY posture sensor; wrist wearable for heart rate/sweat; Quest 3 built-in camera and gyro; external microphone.

## Features / phases
1. **Phase 1** – Implement each feature: heart rate (watch), posture (Quest gyro + DIY Arduino sensor), sweat sensor, auditory emotion (mic + RNN), facial emotion (Quest camera + CNN). Test components individually.
2. **Phase 2** – Integrate sensors → computer → Quest 3; single MR UI showing heart rate, posture feedback, stress/mood, and (where applicable) other person’s posture/emotion.
3. **Phase 3** – Study how real-time biodata access changes behavior in social settings; data collection and iteration.

## Key references
- Full scope and hardware/software details: `docs/ProjectProposal.md`
- Features and MVP demands: `docs/PlanOverview.md`
- Ideas and literature: `docs/ProjectBrainstorm.md`

## Constraints / non-goals
- User consent and data anonymization are critical; avoid collecting or displaying data without clear ethics.
- Interface must be intuitive and non-overwhelming; prioritize “put on head and it works” for MVP.
