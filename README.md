# Binaural Lab Suite

*An experimental, real-time audio consciousness toolkit, featuring binaural beats, personal resonance mapping, and looping affirmations. This software is designed for researchers, seekers, creatives, and the simply curious, and should be used with openness and discernment. It is not a therapeutic product, but a tool for inner exploration and sonic self-inquiry.*

---

## Overview

### Interface Previews

#### 🧠 Binaural Beat Lab

![Binaural Beat Lab](https://github.com/M1ck4/BinauralLab.py/blob/main/docs/binaural_lab.png)
*Design and audition custom binaural beat configurations with real-time waveform visualization and preset management.*

#### 🔁 Affirmation Loop

![Affirmation Loop](https://github.com/M1ck4/BinauralLab.py/blob/main/docs/affirmations.png)
*Create, save, and loop voice-recorded or text-to-speech affirmations. Fine-tune volume, duration, and playback style in a clean library-based UI.*

#### 🌀 Consciousness Resonator

![Consciousness Resonator](https://github.com/M1ck4/BinauralLab.py/blob/main/docs/consciousness_resonator.png)

*Find your personal resonant tone through tuning, humming, or importing samples. Visual feedback and real-time frequency output help guide internal alignment.*

---

**Binaural Lab** began as a tool for exploring the cognitive effects of auditory beat frequencies, now, it’s grown into a modular sound exploration suite. This project enables:

* Crafting binaural beat presets in real time
* Discovering your body's personal resonant frequencies
* Looping spoken affirmations in your own voice or with text-to-speech

Everything you generate, whether tones or affirmations, can be rendered as WAV audio for use offline, meditation sessions, sound design, or experimental research.

Each feature was designed with a specific goal:

* **Real-time sliders** exist to give you immediate auditory feedback, enabling exploration by intuition.
* **Preset saving** allows repeatable experiments, personalized rituals, or iterative refinement.
* **Visual plotting** turns sound into something you can *see*, which helps you understand beat interaction and wave interference.
* **Exporting** transforms inner work into practical media for daily life, study, or sharing.

---

## What's Included

| Module                      | Purpose                                                                                                                                                                                           |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Binaural Beat Lab**       | The core UI. Generate two-tone binaural beats with live sliders, visualise them via oscilloscope/envelope graphs, save/load presets, and export sessions to WAV.                                  |
| **Consciousness Resonator** | A standalone tuner that helps you locate your *personal resonance* frequency — the one you feel in your body. Can import hum samples or record new ones. Saved tones integrate back into the Lab. |
| **Affirmation Loop**        | Record or synthesize your own affirmations, select loop time and volume, and use them in tandem with your tones. Simple WAV output for external use.                                              |

These modules are interconnected. Your discovered resonances appear automatically as presets in the Lab, and affirmations run independently while tones play.

---

## Why Use This?

* **Self-exploration through sound.** Test altered states, enhance focus, dream consciously, or simply relax.
* **Scientific curiosity.** Binaural beats are used in cognitive, neurological, and psychological research. This suite offers precision tools for controlled testing.
* **Creative freedom.** Use exported WAVs in DAWs, meditation apps, art projects, or anything else. No DRM. No dependencies. All offline.
* **Open and ethical.** Fully open-source, MIT licensed, built with transparency. We claim no miracle cures — just tools for your own exploration.

---

## Installation

### Requirements

* **Python 3.9+**
* **Stereo headphones** (not mono speakers)

### Dependencies

Install dependencies with pip:

```bash
pip install numpy scipy matplotlib sounddevice soundfile pyttsx3
```

On Linux, you may need to install extra system libraries:

```bash
sudo apt-get install python3-tk libportaudio2
```

---

## Launch the Suite

From the terminal:

```bash
python BinauralLab.py
```

### Inside the Lab Interface — Detailed Guide

1. **Preset Selection**

   * Choose a category (Delta, Theta, Alpha, etc.) from the left-hand tree view.
   * Click a program to load its settings (carrier, beat frequency, and description).
   * Custom and saved presets appear under “Custom Sounds.”

2. **Carrier Frequency Slider**

   * This sets the base frequency for both ears, typically between 100–400 Hz.
   * A low carrier may produce a deeper body resonance, while higher carriers feel lighter.

3. **Beat Frequency Slider (Δf)**

   * This sets the frequency difference between the left and right ears, which creates the actual brainwave beat.
   * For example, a carrier of 200 Hz and a beat of 5 Hz produces 200 Hz in one ear and 205 Hz in the other.

4. **Volume Control**

   * Adjust overall loudness. It’s capped to 1.0 (100%) to avoid clipping.
   * Tip: low volume with closed eyes is often more effective for internal work.

5. **Live Plotting**

   * The upper graph shows the left and right waveforms.
   * The lower graph shows the envelope of their interference, this is what the brain entrains to.

6. **Start / Stop**

   * Starts or halts real-time playback.
   * Playback uses `sounddevice` and is precise to the sample block.

7. **Consciousness Resonator**

   * The Consciousness Resonator is a harmonic alignment tool, a tuner designed to help you discover your **personal resonance frequency**. This is the frequency that your body, breath, and awareness naturally sync with, a tone that feels like home.

   * **Instructions:**
     Begin by humming naturally into the microphone. The Resonator will record your sample and analyze its spectral content to estimate the dominant frequency range. Once playback begins, hum again while adjusting the slider. Your goal is to *match the tone* being played — not just with your ears, but with your body.

     You'll know you’ve found it when the tone seems to disappear *into* your voice, or when you feel it vibrate through your chest, head, or throat. It should feel grounding, like you’ve hit a note that *belongs* to you.

     A powerful method: hum a **high note**, then slowly glide it downward until it *clicks* with the played tone. This mimics overtone resonance, helping you intuitively locate your harmonic base. Once this frequency is locked in, use the slider to fine-tune until it feels emotionally and physically “right.”

   * **Why this matters:**
     Current research in **bioacoustics**, **psychoacoustics**, and **sound-based self-regulation** supports the idea that each person resonates with unique frequency bands, influenced by body structure, vagal tone, and nervous system response. Finding your personal resonance can:

     * Improve the felt effect of binaural beats
     * Support **entrainment** and reduce internal “resistance” to sound
     * Increase **coherence** in breathing, mood, and heart rate
     * Deepen meditation, intention setting, and relaxation

   * **Technical note:**
     The recorded tone is an estimate, microphones and ambient noise can distort precision. This is not about mathematical exactness, but about discovering a *felt sense of alignment*. Trust your body’s feedback over numerical values.

   * Once you've found a satisfying tone, press **⭐ Mark Tone** to save it. The frequency is stored and will appear in the Binaural Lab as a preset titled **“Personal Resonance #...”** so you can use it as the base carrier for any session.

   This tool is a fusion of **somatic exploration**, **frequency attunement**, and **DIY neuroacoustics**, helping you bridge mind and body through a tone uniquely yours.

8. **Affirmation Loop**

   * Opens a window to enter affirmations via voice or text.
   * Plays them in a loop alongside your tones.
   * You can adjust the loop duration, volume gain, and review past affirmations.
   * **Primary Purpose:** The Affirmation Loop is not merely for repetition,  it is a tool for grounding *intention*. When used before or during a meditative session, affirmations serve as cognitive anchors, priming your awareness toward a desired mental, emotional, or spiritual state.
   * **Why it matters:** Neuroscience and psychology research show that spoken affirmations activate brain areas involved in self-processing and valuation (e.g., the medial prefrontal cortex). Studies in positive psychology suggest that affirmations can reduce stress, enhance goal-alignment, and modulate default-mode brain activity when practiced with attention. In the context of this suite, affirmations are meant to establish *internal narrative coherence*, a kind of psychological scaffolding that the brain can align with while entraining to the rhythmic pulse of binaural beats.
   * **Best practices:** Users may wish to speak or type affirmations like “I am ready to release,” “Clarity flows through me,” or “Tonight I dream lucidly.” When played softly in tandem with tones, the audio forms a feedback loop between intention and state. This can deepen entry into theta, reinforce purpose, and enhance post-session integration.

9. **Save / Delete Presets**

   * Save the current settings with a name and description.
   * Delete removes it from both the list and the underlying JSON file.

10. **Export to WAV**

* Choose a duration (e.g., 300 seconds).
* Saves a stereo `.wav` file of the current tone configuration for offline playback or editing.

---

## Binaural Presets

Over 40 presets are included, spanning these major bands:

| Band      | Frequency Range | Uses                                      |
| --------- | --------------- | ----------------------------------------- |
| **Delta** | 0.5–4 Hz        | Sleep, deep healing, astral drift         |
| **Theta** | 4–8 Hz          | Meditation, creativity, OBE states        |
| **Alpha** | 8–12 Hz         | Focus, relaxation, light trance           |
| **Beta**  | 13–30 Hz        | Problem solving, cognition, alertness     |
| **Gamma** | 30–50 Hz        | Learning, integration, expanded awareness |

Presets are editable. You can add new ones, delete old ones, and annotate them with descriptions.

---

## Build as an EXE (Windows only)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole BinauralLab.py
```

Copy the `.exe` and all required `.py` files into one folder. The app creates needed JSONs on first run.

---

## Safety Notice

Binaural beats influence brainwave patterns. While generally safe:

* **Never use while driving or operating machinery**
* **Avoid very loud playback**
* **Consult your doctor** if you have epilepsy, pacemakers, or psychiatric conditions

This suite is intended for light experimentation and personal use. It is *not* a medical or therapeutic tool.

---

## Contributing

Contributions are welcome:

* Submit new presets
* Improve interface usability
* Suggest features or report bugs

Use `flake8` to lint code and please document any new features clearly.

---

## License

**MIT License** — use freely, remix generously, credit kindly.

---

## Acknowledgements

* Heinrich Wilhelm Dove, originator of auditory beats
* The Monroe Institute, pioneers in consciousness audio research
* Dr. Jeffrey Thompson and pioneers of neuroacoustic therapy
* Researchers in vibroacoustic and somatic resonance therapies
* Open-source contributors to NumPy, SciPy, Matplotlib, SoundDevice, and SoundFile
* Paul Devereux and acoustic archaeology advocates exploring sonic cognition in sacred sites
* Alan Watts, whose teachings echo in the sound-mind relationship
* Engineers and dreamers who explore sound as language, medicine, and mirror

> “The world is sound.” — Ancient Vedic teaching

Stay curious. Tune deeply. 🎧🧠
