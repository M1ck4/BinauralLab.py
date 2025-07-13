# Binaural Beat Lab

*Real-time binaural-beat generator with live sliders, preset library, and WAV export—offline & open-source.*

---

## Why use it?

* **Instant feedback.** Hear changes the moment you move a slider.
* **Rich preset library.** Forty hand-tuned programs span Delta, Theta, Alpha, Beta, and Gamma ranges.
* **Visual learning.** A live oscilloscope + envelope plot shows exactly how the two tones interact.
* **Custom workflow.** Save, edit, and delete your own combinations; everything lives in a simple JSON file next to the script.
* **Portable audio.** Render any session to a high-quality 44.1 kHz stereo WAV for phone playback or DAW import.

---

## Screenshot

```
Place holder
```

---

## Installation

### Prerequisites

* **Python 3.9+** (CPython or Anaconda)
* **Headphones** (binaural beats do not work over mono speakers)

### Dependencies

```bash
pip install numpy sounddevice scipy matplotlib
```

`tkinter` ships with the standard Python installer on Windows and most Linux distros; on some minimal Linux images you may need to install it separately:

```bash
# Debian / Ubuntu
sudo apt-get install python3-tk
```

---

## Running the Lab

```bash
python BinauralLab.py
```

1. **Pick a preset** from the tree or dial in your own values.
2. Hit **Start** to begin playback; **Stop** halts it.
3. Tweak sliders in real time audio and plot stay in sync.
4. Click **Save** to store the current settings, or **Delete** to remove a saved program.
5. Click **Export** to write a stereo WAV (you’ll be asked for duration and save path).

---

## Preset families

| Band *(Hz)*         | Typical effect                     | Included programmes                                 |
| ------------------- | ---------------------------------- | --------------------------------------------------- |
| **Delta (0.5 – 4)** | Deep sleep, healing, astral drift  | *Delta Sleep*, *Float State*, *Astral Hum*          |
| **Theta (4 – 8)**   | Meditation, creative insight, OBE  | *Theta Meditation*, *Gateway Voyage*, *Lucid Entry* |
| **Alpha (8 – 12)**  | Calm focus, memory, light trance   | *Alpha Creativity*, *Mind Mirror*, *Focus 10*       |
| **Beta (13 – 30)**  | Alertness, problem-solving, energy | *Beta Cognition*, *Peak Focus*, *Focus 21*          |
| **Gamma (30 – 50)** | Integration, heightened awareness  | *Gamma Integration*, *Gamma Consciousness*          |

*(See `binaural_presets.json` for all definitions or browse them in-app.)*

---

## File layout

```
BinauralBeatLab/
├─ BinauralLab.py          → main application script
├─ binaural_presets.json   → auto-generated on first run
├─ requirements.txt        → optional, pin versions for CI
└─ docs/
   └─ screenshot.png       → optional images for README
```

`binaural_presets.json` is regenerated with default content the first time you launch the program, then updated whenever you add or delete a preset. Commit this file if you want to share your custom tones.

---

## Building a one-click `.exe` (optional, Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole BinauralLab.py
# Your standalone binary lives in dist/BinauralLab.exe
```

Ship the EXE by itself; it will create a fresh `binaural_presets.json` on first launch.

---

## Safety notice

Binaural audio is generally considered safe, but **never** drive, operate machinery, or use at high volume while listening. If you have epilepsy, pacemakers, or other medical concerns, consult a professional first.

---

## Contributing

Pull requests are welcome! Feel free to:

* Improve the UI or DSP engine
* Add scientifically backed presets (include references)
* Tackle open issues in the tracker

Please run `flake8` on any new code and update this README if behaviour changes.

---

## License

**MIT** — do whatever you like, just keep the copyright notice and attribution.

---

## Acknowledgements

* Heinrich Wilhelm Dove and the researchers who pioneered auditory beat stimulation
* The open-source community behind **NumPy**, **SciPy**, **Matplotlib**, and **SoundDevice** — this project stands on your shoulders.

Happy tuning, and may your brainwaves find their perfect resonance! 🧠🎧
