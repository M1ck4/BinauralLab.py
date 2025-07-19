"""
consciousness_resonator.py
──────────────────────────
A standalone “Hum Tuner” that helps users discover and save multiple personal
resonant frequencies.

Key features
────────────
• Adjustable sine-tone playback (60 – 400 Hz) with volume control
• Fine-tune buttons and live Hz read-out
• ⭐ Mark Tone  → appends {"hz", "timestamp"} to user_resonance.json
• 🎙️  Import Hum Sample (wav / mp3 / ogg / flac) → FFT analysis, suggested Hz
• 🎤  Record & Suggest (3 s mic grab)           → same analysis routine
• Breathing blue ring + solid white core graphic
  – ring radius pulses and scales with the current frequency
Launch from Binaural Beat Lab’s ✨ button or run directly:
    python consciousness_resonator.py
"""

import json
import os
from datetime import datetime

import numpy as np
import sounddevice as sd
import soundfile as sf
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ───── Configuration ────────────────────────────────────────────────────────
SAMPLE_RATE        = 44_100                # Hz
BLOCKSIZE          = 1_024
JSON_FILE          = "user_resonance.json" # saved tones list

FREQ_MIN           = 60.0                  # Hz
FREQ_MAX           = 400.0                 # Hz
DEFAULT_FREQ       = 128.0                 # Hz
DEFAULT_VOL        = 0.30                  # 0-1

FFT_SECONDS        = 3.0                   # analysed duration
PEAK_THRESHOLD_DB  = 10                    # min dB above noise floor

# ───── Application ──────────────────────────────────────────────────────────
class ResonatorApp:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("Consciousness Resonator")
        master.geometry("520x560")

        # State
        self.freq_var = tk.DoubleVar(value=DEFAULT_FREQ)
        self.vol_var  = tk.DoubleVar(value=DEFAULT_VOL)
        self.stream   = None
        self.phase    = 0.0

        # Build UI & start animation
        self._build_ui()
        self._animate()

    # ─── UI construction ────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 8}

        # Frequency slider
        ttk.Label(self.master, text="Frequency (Hz)",
                font=("Arial", 12, "bold")).pack(**pad)
        self.freq_slider = ttk.Scale(
            self.master, from_=FREQ_MIN, to=FREQ_MAX,
            orient="horizontal", variable=self.freq_var,
            command=lambda _=None: self._update_readout())
        self.freq_slider.pack(fill="x", **pad)

        # Fine-tune buttons + read-out
        fine = ttk.Frame(self.master); fine.pack(**pad)
        ttk.Button(fine, text="▼ 0.1",
                command=lambda: self._nudge(-0.1)).pack(side="left", padx=4)
        self.readout = ttk.Label(fine, text=f"{DEFAULT_FREQ:.2f} Hz",
                                font=("Arial", 12, "bold"))
        self.readout.pack(side="left", padx=12)
        ttk.Button(fine, text="▲ 0.1",
                command=lambda: self._nudge(0.1)).pack(side="left", padx=4)

        # Volume slider
        ttk.Label(self.master, text="Volume",
                font=("Arial", 12, "bold")).pack(**pad)
        ttk.Scale(self.master, from_=0, to=1,
                orient="horizontal", variable=self.vol_var
                 ).pack(fill="x", **pad)

        # Tone controls
        ctrl = ttk.Frame(self.master); ctrl.pack(**pad)
        self.start_btn = ttk.Button(ctrl, text="▶ Start Tone", width=14,
                                    command=self.toggle_tone)
        self.start_btn.pack(side="left", padx=6)
        ttk.Button(ctrl, text="⭐ Mark Tone", width=14,
                command=self.save_tone).pack(side="left", padx=6)

        # Import / Record controls
        io = ttk.Frame(self.master); io.pack(**pad)
        ttk.Button(io, text="🎙️  Import Hum Sample",
                command=self.import_sample).pack(side="left", padx=6)
        ttk.Button(io, text="🎤 Record & Suggest (3 s)",
                command=self.record_sample).pack(side="left", padx=6)

        # Suggestion label
        self.suggest = ttk.Label(self.master, text="",
                                foreground="#15803d",  # emerald
                                font=("Arial", 11, "bold"))
        self.suggest.pack()

        # Breathing graphic canvas
        self.canvas = tk.Canvas(self.master, width=380, height=180,
                                highlightthickness=0)
        self.canvas.pack(pady=(24, 8))
        self.ring = self.canvas.create_oval(0, 0, 0, 0,
                                            fill="#2563eb", outline="")
        self.core = self.canvas.create_oval(0, 0, 0, 0,
                                            fill="white",  outline="")
        self.anim_phase = 0.0  # for breathing

        # Footer
        ttk.Label(self.master,
                text="Hum along and slide until the tone feels one with you.",
                font=("Arial", 9, "italic")).pack(pady=(4, 8))

    # ─── Tone playback ──────────────────────────────────────────────────────
    def toggle_tone(self) -> None:
        if self.stream:
            self._stop_stream(); self.start_btn.config(text="▶ Start Tone")
        else:
            self._start_stream(); self.start_btn.config(text="■ Stop Tone")

    def _start_stream(self) -> None:
        self.stream = sd.OutputStream(samplerate=SAMPLE_RATE, channels=1,
                                    blocksize=BLOCKSIZE,
                                    callback=self._audio_callback)
        self.stream.start()

    def _stop_stream(self) -> None:
        if self.stream:
            self.stream.stop(); self.stream.close()
        self.stream = None; self.phase = 0.0

    def _audio_callback(self, out, frames, *_):
        f   = self.freq_var.get()
        vol = self.vol_var.get()
        omega = 2*np.pi*f / SAMPLE_RATE
        idx   = np.arange(frames)
        ph    = self.phase + omega*idx
        out[:, 0] = (np.sin(ph) * vol).astype(np.float32)
        self.phase = (ph[-1] + omega) % (2*np.pi)

    # ─── Breathing / frequency-responsive animation ────────────────────────
    def _animate(self) -> None:
        # Breathing phase
        self.anim_phase = (self.anim_phase + 0.04) % (2*np.pi)
        breath_offset   = 6 * np.sin(self.anim_phase)      # ±6 px

        # Base radius scales with frequency
        frac  = (self.freq_var.get() - FREQ_MIN) / (FREQ_MAX - FREQ_MIN)
        base  = 40 + 35 * frac                             # 40 – 75 px
        r_out = base + breath_offset
        r_in  = r_out * 0.35                               # white core

        # Update canvas coords
        cx, cy = 190, 115
        self.canvas.coords(self.ring, cx-r_out, cy-r_out, cx+r_out, cy+r_out)
        self.canvas.coords(self.core, cx-r_in,  cy-r_in,  cx+r_in,  cy+r_in)

        self.master.after(30, self._animate)

    # ─── UI helpers ─────────────────────────────────────────────────────────
    def _nudge(self, delta: float) -> None:
        new = np.clip(self.freq_var.get() + delta, FREQ_MIN, FREQ_MAX)
        self.freq_var.set(round(new, 2)); self._update_readout()

    def _update_readout(self) -> None:
        self.readout.config(text=f"{self.freq_var.get():.2f} Hz")
        self.suggest.config(text="")  # clear suggestion once user changes slider

    # ─── Save personal resonance ────────────────────────────────────────────
    def save_tone(self) -> None:
        entry = {"hz": round(self.freq_var.get(), 2),
                "timestamp": datetime.now().isoformat()}

        # Append to list (create file if missing)
        data: list[dict] = []
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, "r") as f:
                    data = json.load(f)
                if isinstance(data, dict):            # legacy single object
                    data = [data]
            except Exception:
                data = []
        data.append(entry)

        try:
            with open(JSON_FILE, "w") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Saved",
                f"Resonance {entry['hz']} Hz added."
                f"\nTotal saved tones: {len(data)}")
        except IOError as e:
            messagebox.showerror("Error", str(e))

    # ─── FFT analysis helpers ───────────────────────────────────────────────
    def _analyse(self, sig: np.ndarray) -> float | None:
        """Return dominant hum in Hz or None."""
        if sig.ndim > 1:
            sig = sig.mean(axis=1)
        sig = sig[: int(FFT_SECONDS*SAMPLE_RATE)]
        sig = np.pad(sig, (0, max(0, int(FFT_SECONDS*SAMPLE_RATE) - len(sig))))
        sig *= np.hanning(len(sig))

        spec  = np.fft.rfft(sig)
        freqs = np.fft.rfftfreq(len(sig), 1/SAMPLE_RATE)
        mags  = 20*np.log10(np.abs(spec) + 1e-8)

        band = (freqs >= FREQ_MIN) & (freqs <= FREQ_MAX)
        if not band.any():
            return None

        pk_i   = np.argmax(mags[band])
        pk_f   = freqs[band][pk_i]
        pk_db  = mags[band][pk_i]
        noise  = np.median(mags[band])

        if pk_db - noise < PEAK_THRESHOLD_DB:
            return None
        return float(pk_f)

    # ─── Import saved hum sample ────────────────────────────────────────────
    def import_sample(self) -> None:
        fname = filedialog.askopenfilename(
            title="Select hum recording",
            filetypes=[("Audio files", "*.wav *.flac *.ogg *.mp3"),
                    ("All files",   "*.*")]
        )
        if not fname:
            return
        try:
            sig, sr = sf.read(fname, always_2d=False)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Resample to 44.1 k if needed (quick & dirty)
        if sr != SAMPLE_RATE:
            ratio   = SAMPLE_RATE / sr
            indices = np.round(np.arange(0, len(sig) * ratio) / ratio).astype(int)
            indices = np.clip(indices, 0, len(sig) - 1)
            sig     = sig[indices]

        peak = self._analyse(sig)
        if peak is None:
            messagebox.showinfo("Analysis", "No clear hum found in that file.")
            return

        self.freq_var.set(round(peak, 2)); self._update_readout()
        self.suggest.config(text=f"Suggested ≈ {peak:.2f} Hz")

    # ─── Record live hum sample ─────────────────────────────────────────────
    def record_sample(self) -> None:
        was_playing = self.stream is not None
        if was_playing:
            self._stop_stream()

        self.suggest.config(text="Recording…")
        self.master.update_idletasks()

        try:
            sig = sd.rec(int(FFT_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                        channels=1, dtype='float32')
            sd.wait()
            sig = sig.flatten()
        except Exception as e:
            messagebox.showerror("Mic error", str(e))
            self.suggest.config(text="")
            return

        peak = self._analyse(sig)
        if peak is None:
            self.suggest.config(text="")
            messagebox.showinfo("Analysis",
                "No clear hum detected. Try again in a quieter space.")
        else:
            self.freq_var.set(round(peak, 2)); self._update_readout()
            self.suggest.config(text=f"Suggested ≈ {peak:.2f} Hz")

        if was_playing:
            self._start_stream()

    # ─── Clean-up ───────────────────────────────────────────────────────────
    def on_close(self) -> None:
        self._stop_stream()
        self.master.destroy()

# ───── Main entry ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = ResonatorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
