# D.U.C.K — ML path (dual-model)

This document expands the **machine learning and inference strategy** summarized in [`FinalStretchDoc.md`](FinalStretchDoc.md). It is a **companion spec** for ML design; if anything here conflicts with `FinalStretchDoc.md`, **prefer `FinalStretchDoc.md`** and update this file.

---

## Why two models

Running a single heavy model for **every tick** of multimodal biodata risks **latency** on the path to the headset. The headset should feel like a **real-time helper**, not a laggy dashboard.

We split inference into:

1. **Fast path — Random Forest** — Trained on **tabular features** from sensors and perception outputs (e.g. MorphCast-derived numbers, not raw pixels). Produces **quick, frequent** decisions so the user gets timely cues.
2. **Interval path — separate ML model** — Runs on **time ranges** (interval length **TBD**, e.g. roughly **5 s to 30 s** or longer). Consumes **aggregated** information over each interval to give a **richer read of the situation** (e.g. brief episodes vs sustained states). Exact outputs and copy are **not** fixed; examples in conversation are illustrative only.

**Compute placement:** **All training and inference run on the host PC for now.** The **Quest 3 only displays** results (labels, short text, scores as defined). That keeps thermal and compute load off the headset and matches the “thin client” MR app.

---

## Fast path: Random Forest

### What it is

A **Random Forest** is an ensemble of **decision trees** trained on random data/feature subsets; predictions combine **votes** (classification) or **averages** (regression). It is a standard **supervised** learner for **structured features**.

### Why it fits the fast layer

- **Inference** on modest feature vectors is typically **very fast** on a PC (often milliseconds), which supports responsive updates.
- Works well with **mixed modalities** once they are turned into **numbers**: HR stats, posture indicators, MorphCast outputs, etc.
- Does **not** consume raw video inside the forest; **MorphCast** (or similar) supplies **expression-related features** upstream.

### Role in the pipeline

- **Input:** Current (or very recent) **feature vector** built from live biodata and perception outputs.
- **Output (current plan):** **Discrete labels** (e.g. buckets for engagement, discomfort, neutral—exact schema TBD with data and ethics).
- **Future (not committed):** A **continuous** arousal/stress-style score may be added later (e.g. regression head, calibration, or a parallel model). Parked until there is need and labels/proxies.

---

## Interval path: contextual model

### Purpose

Summarize **what happened over a window of time** rather than a single moment: e.g. short dips vs recovery, sustained patterns—**wording and targets remain TBD** and should follow study design and labeling.

### Design stance (current)

- **Prefer simpler models first** on **aggregated interval features** (means, mins, maxes, slopes, counts of fast-path states, etc.). Candidates include **tree ensembles**, **gradient boosting**, or similar **tabular** methods—**exact choice TBD** once data exists.
- **Neural or sequence models** (e.g. over multiple consecutive intervals) are **not assumed** for v1; revisit if simpler models fail to capture temporal stories you care about.

### Timing

- **Interval length:** **TBD** (could be anywhere in a rough **5 s–30 s** band or adjusted with experimentation). May differ by modality or task.
- Runs **less often** than the fast path; outputs can be **richer** (short summaries, discrete situation labels, etc.—TBD).

---

## How the two models relate

- **Fast RF** drives **immediate** UI affordances (icons, colors, short discrete states).
- **Interval model** drives **reflective** or **narrative** layers (what the last N seconds “looked like” as a whole).
- They may **disagree**; product rules (which signal wins, debouncing, copy) are **UX/TBD**, not assumed here.

---

## Training and data (high level)

- Both models need **defined targets** (labels for classification; optional regression targets later).
- **Synchronized timestamps** across HR, posture, and perception streams are required for honest features and labels.
- **Train/validate/test** splits should respect **sessions/participants** where applicable to avoid leakage.

---

## Out of scope (unchanged)

- **Voice / microphone emotion** as an active ML path — not part of this plan unless `FinalStretchDoc.md` changes.

---

## Open decisions

- **Interval length(s)** and whether they are fixed or adaptive.
- **Exact taxonomy** of discrete labels for fast and interval outputs.
- **Interval model algorithm** (tree-based vs neural vs hybrid) after data and baselines.
- **MorphCast integration shape** on PC (API, latency, what exactly is fed into feature builders).
- **Continuous arousal/stress** — if/when to add, and how to validate.

---

*Update this document when the ML architecture or label schema changes.*
