# Making a Customized ML Model for D.U.C.K

This document helps decide **which model type** to use for your multimodal data (heart rate, posture, sweat/EDA, 3rd‑party facial outputs), and outlines how to implement it in practice.

## Which type of model?

Given the current setup:

- You have **time-series signals** (heart rate, posture, sweat/EDA).
- You have **already-processed facial outputs** from a third-party system (not raw images).
- You care about **short-term state** over a recent window (e.g., the last few seconds), not long video or audio sequences.

Under these conditions:

- **CNNs on images** are **not** necessary, because you are not training directly on raw images.
- **Heavy RNNs/transformers** across long sequences are likely overkill for an initial version.

**Recommended starting point:**  
Use a **windowed, feature-based model** with a **feed-forward neural network (MLP)**:

- Slice the sensor data into short windows (e.g., a few seconds).
- Compute summary features per modality within each window.
- Concatenate them into a single feature vector.
- Train an MLP to predict your target labels/scores for that window.

You can always upgrade later (e.g., to an RNN or transformer over multiple windows) if you find strong temporal dependencies that the simple model cannot capture.

## Model 1: Windowed Feature MLP (recommended baseline)

### Inputs

For each time window:

- **Heart rate features** (examples):
  - Mean, min, max, standard deviation of HR in the window.
  - Simple trend features (e.g., last value minus first).
- **Posture features** (from Arduino/IMU):
  - Mean and variance of relevant axes (e.g., pitch/roll angles).
  - Counts or proportions of “slouching” vs “upright” samples if you have a rule.
- **Sweat / EDA features**:
  - Mean, variance, and simple slope over the window.
  - Number of rapid rises above threshold (if relevant).
- **Facial features (3rd party)**:
  - Whatever numeric outputs you get (e.g., emotion probabilities, valence/arousal scores).
  - Optionally, one‑hot encodings for categorical labels.

Concatenate all features into one numeric vector (e.g., length 50–200 depending on how many you define).

### Outputs

Decide what the model predicts per window, such as:

- One or more **categorical labels** (e.g., user state classes).
- One or more **continuous scores** (e.g., stress or engagement level).

The same MLP can output multiple heads (e.g., one for classification, one for regression) if you need both.

### Architecture (conceptual)

An example MLP for a single window:

- Input layer: size = number of features.
- Hidden layers: 2–4 dense layers with nonlinearities (e.g., ReLU or GELU).
- Output layer(s):
  - Classification: softmax or sigmoid outputs.
  - Regression: linear outputs.

Any mainstream framework (PyTorch, TensorFlow/Keras, etc.) can implement this with simple dense layers.

### Training steps

1. **Prepare dataset:**
   - Build a function that:
     - Takes synchronized streams and labels.
     - Slices them into windows.
     - Computes the feature vector for each window.
     - Returns `(features, labels)` pairs.
2. **Split data:**
   - Train / validation / test, ensuring no leakage between sessions/participants if relevant.
3. **Train baseline:**
   - Use a standard optimizer (e.g., Adam).
   - Choose an appropriate loss:
     - Cross-entropy for classification.
     - MSE/MAE for regression.
     - Combined loss if you have multiple outputs.
4. **Evaluate and iterate:**
   - Check performance on validation/test.
   - Adjust:
     - Number of features and their design.
     - Network depth/width and regularization (dropout, weight decay).
     - Window length and stride.

## When to consider RNNs or transformers

If later you find that:

- Short windows are not enough, and
- The user state depends strongly on **longer sequences** (e.g., tens of seconds or minutes),

then you can extend the approach:

- Treat each window as a timestep in a sequence.
- Feed a sequence of window features into:
  - An **RNN** (e.g., LSTM/GRU), or
  - A **transformer encoder**.
- Use the final hidden state (or attention-pooled representation) to predict the same kinds of outputs.

This adds complexity but can capture richer temporal patterns beyond what a per-window MLP can.

## Serving the trained model

Once an MLP (or later RNN/transformer) is trained:

1. **Export the model** in your chosen framework’s saved format.
2. **Embed it in the intermediate server**:
   - The server performs the same windowing and feature computation on live data.
   - It passes each feature vector (or sequence of vectors) through the model.
   - It obtains predictions and converts them to:
     - Machine-readable fields (JSON).
     - Optional short text summaries.
3. **Send predictions to Quest 3**:
   - Only send the final outputs (labels/scores/text), not raw data.
   - The Quest app simply displays them in MR.

This approach gives you a practical, extensible path: start simple with a windowed MLP, verify it works, then only move to sequence models if there is clear evidence they are needed.

