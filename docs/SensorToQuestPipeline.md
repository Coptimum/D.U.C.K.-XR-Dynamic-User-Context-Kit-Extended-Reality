# Sensor → ML Model → Quest 3 Text/State

This document now focuses on the **ML model** that turns multimodal inputs into meaningful, human-readable information. Transport details (how data reaches the server and Quest) are intentionally kept minimal.

## What Feeds Into the Model (very brief)

- **Heart rate:** Time-series values from a wearable or similar device (e.g., beats-per-minute samples over time).
- **Posture:** Time-series values derived from the Arduino posture sensor (e.g., accelerometer/IMU features from sketches like `arduino/posture.ino` and `arduino/accelTest/accelTest.ino`).
- **Sweat / EDA:** Time-series values from a sweat or skin-conductance sensor (stress-related signal over time).
- **Facial data (3rd party):** Outputs from an external facial recognition/emotion system (e.g., its own scores/labels), which are treated as **already-processed features** and fed directly into the model.

All of these are aggregated into short time windows (for example, a few seconds at a time) and converted into numeric feature vectors or tensors for the model.

## ML Objective (to be finalized)

The model’s exact goal should be defined explicitly before implementation. Examples include:

- Predicting a discrete **state label** (e.g., a small set of “user states” relevant to the study).
- Predicting one or more **continuous scores** (e.g., stress, engagement, or posture quality on a scale).
- Producing both: continuous scores plus a summarized text tag or category.

Once you decide the target(s), you can choose loss functions and evaluation metrics aligned with those targets.

## Building the Dataset

1. **Synchronize streams:** Ensure heart rate, posture, sweat/EDA, and facial-feature outputs are timestamped in a shared time base.
2. **Windowing:** Slice the continuous data into fixed windows (e.g., a few seconds) so each training example corresponds to “what was happening” in that interval.
3. **Feature extraction:** For each window:
   - Compute summary statistics or domain-specific features from each sensor (e.g., means, variances, deltas, simple posture features).
   - Include the 3rd-party facial outputs for that same window (e.g., whatever numeric or categorical outputs it provides).
4. **Labels:** Attach labels or target scores to each window according to your experimental design or annotation process (e.g., self-report, experimenter labels, task segments).

The result is a dataset of `(features, labels)` pairs suitable for training.

## Designing the Model

Because the data is time-based and multimodal, the model should handle:

- Multiple input feature groups (heart rate, posture, sweat/EDA, facial features).
- Temporal context over the short windows (even if you only use simple statistics per window).

You can start with a **simple baseline** such as:

- A feed-forward neural network that takes concatenated features from all modalities for one window and predicts the target(s).

If needed, you can later extend this to architectures that model sequence structure across multiple windows (e.g., recurrent or attention-based models), but that is not required for an initial version.

### Inputs and Outputs (per window)

- **Input:** A single structured object containing:
  - Numeric features derived from heart rate.
  - Numeric features derived from posture.
  - Numeric features derived from sweat/EDA.
  - Numeric or categorical encodings derived from 3rd-party facial outputs.
- **Output:** One or more of:
  - Discrete label(s) for user state.
  - Continuous scores (e.g., a stress level scalar).
  - (Optionally) a short summary string generated from the numeric outputs (this can also be done by separate logic outside the model).

## Training and Evaluation

1. **Split the data:** Separate windows into training, validation, and test sets, taking care to avoid leakage across sessions or participants if applicable.
2. **Train the baseline:** Optimize a simple model on the training set and monitor performance on validation.
3. **Evaluate:** Use metrics that match your objective (e.g., accuracy/F1 for classification, MAE/MSE for regression, plus any domain-specific metrics you care about).
4. **Iterate:** If performance is insufficient:
   - Refine features (e.g., more domain-specific statistics, different window sizes).
   - Adjust model capacity and regularization.
   - Consider modeling dependencies across multiple consecutive windows if that is clearly beneficial.

## Serving the Model in the Pipeline

At inference time, the model is used inside the intermediate server as follows:

1. **Live windowing:** Continuously collect incoming sensor and facial-feature data into the same window structure you used during training.
2. **Feature computation:** Compute features for each new window using the same logic as in the dataset builder.
3. **Model inference:** Pass the feature vector/tensor into the trained model and obtain predictions.
4. **Formatting for Quest 3:** Convert the numeric outputs into a compact structure (e.g., JSON) and, if desired, attach a short human-readable summary string that the Quest 3 app will display.

The Quest 3 application only needs the **model outputs** (numbers and/or labels plus optional text), not the raw data or internal details of how the model works.
