import os, json, uuid
from pathlib import Path
from datetime import datetime

import numpy as np
import sounddevice as sd
import soundfile as sf
import pyttsx3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog

# ── configuration ─────────────────────────────────────────────
A_DIR   = Path("affirmations")
META    = A_DIR / "affirmations.json"
SRATE   = 44_100
BLOCK   = 1_024

DEFAULT_TEXT = (
    "I am more than my physical body. Because I am more than physical matter, "
    "I can perceive that which is greater than the physical world. Therefore, "
    "I deeply desire to expand, to experience, to know, to understand, to use "
    "such greater energies and energy systems as may be beneficial and "
    "constructive to me and to those around me."
)

# ── app class ─────────────────────────────────────────────────
class AffirmationApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Affirmations")
        master.geometry("1000x400")  # width x height in pixels
        master.resizable(False, False)

        # runtime state
        self.affirmations: list[dict] = []
        self.selected_id: str | None  = None
        self.mode          = tk.StringVar(value="tts")
        self.record_length = tk.DoubleVar(value=30.0)
        self.volume_db     = tk.DoubleVar(value=-15.0)
        self.loop_min      = tk.DoubleVar(value=0.0)
        self.recording     = False
        self.record_stream = None
        self.record_buf    = []
        self.audio_data: np.ndarray | None = None
        self.buf_len = 0
        self.play_ptr = 0
        self.play_stream = None
        self.is_playing  = False
        self.title_text  = ""

        first = self._load_meta()
        self._build_ui()
        self._refresh_tree()
        if first:
            self._select_by_id(first)
        else:
            self._on_add()

    # ── metadata ----------------------------------------------------------
    def _load_meta(self):
        A_DIR.mkdir(exist_ok=True)
        if META.exists():
            try:
                self.affirmations = json.load(META.open())
            except:
                self.affirmations = []
        for r in self.affirmations:
            r.setdefault("title", r.get("text","")[:30] or r.get("file",""))
            r.setdefault("db", -15.0)
            r.setdefault("loop_min", 0.0)
            r.setdefault("created", datetime.now().isoformat())
        self._save_meta()
        return str(self.affirmations[0]["id"]) if self.affirmations else None

    def _save_meta(self):
        json.dump(self.affirmations, META.open("w"), indent=2)

    # ── ui ----------------------------------------------------------------
    def _build_ui(self):
        paned = ttk.PanedWindow(self.master, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)

        # library pane
        left = ttk.Frame(paned, width=400)
        paned.add(left, weight=1)
        ttk.Label(left, text="Affirmation Library",
                font=("Arial",11,)).pack(anchor="w", padx=5, pady=(0,5))

        self.tree = ttk.Treeview(
            left,
            columns=("Date","Vol"),
            show="tree headings",
            selectmode="browse",
            height=15
        )
        self.tree.heading("#0",  text="Title");    self.tree.column("#0", width=200)
        self.tree.heading("Date", text="Date");     self.tree.column("Date", width=80, anchor="center")
        self.tree.heading("Vol",  text="Vol (dB)"); self.tree.column("Vol", width=80, anchor="center")
        self.tree.tag_configure("highlight", background="lightyellow")
        self.tree.pack(fill="x", expand=False, padx=5, pady=(0,2))
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        lb_btn = ttk.Frame(left)
        lb_btn.pack(fill="x", padx=5, pady=(2,5))
        ttk.Button(lb_btn, text="Add New",   command=self._on_add).pack(side="left", padx=2)
        ttk.Button(lb_btn, text="▶ Preview", command=self._toggle_play).pack(side="left", padx=2)
        ttk.Button(lb_btn, text="Delete",    command=self._on_delete).pack(side="left", padx=2)
        ttk.Button(lb_btn, text="💾 Save",    command=self._save).pack(side="left", padx=2)

        # editor pane
        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        # Title display
        title_frame = ttk.Frame(right)
        title_frame.pack(fill="x", padx=5, pady=(5,0))
        ttk.Label(title_frame, text="Title:", font=("Arial",11,)).pack(side="left")
        self.title_lbl = ttk.Label(title_frame, text="", font=("Arial",11))
        self.title_lbl.pack(side="left", fill="x", expand=True, padx=(5,0))

        # Affirmation text section
        text_frame = ttk.LabelFrame(right, text="Affirmation Text")
        text_frame.pack(fill="x", padx=5, pady=5)
        self.text = scrolledtext.ScrolledText(
            text_frame, wrap="word", height=6, font=("Arial",10))
        self.text.pack(fill="x", padx=5, pady=5)

        # Audio source & recording section
        audio_frame = ttk.LabelFrame(right, text="Audio Source & Recording")
        audio_frame.pack(fill="x", padx=5, pady=5)
        src = ttk.Frame(audio_frame)
        src.pack(fill="x", pady=(5,0))
        ttk.Radiobutton(src, text="Text‑to‑Speech", variable=self.mode, value="tts").pack(side="left", padx=5)
        ttk.Radiobutton(src, text="Record Voice",   variable=self.mode, value="rec").pack(side="left", padx=5)
        rec_controls = ttk.Frame(audio_frame)
        rec_controls.pack(fill="x", pady=(5,5))
        ttk.Label(rec_controls, text="Record (s):").pack(side="left", padx=(0,5))
        ttk.Entry(rec_controls, textvariable=self.record_length, width=6).pack(side="left")
        self.rec_btn = ttk.Button(rec_controls, text="⏺ Record", command=self._toggle_record)
        self.rec_btn.pack(side="left", padx=5)

        # Settings section
        settings_frame = ttk.LabelFrame(right, text="Settings")
        settings_frame.pack(fill="x", padx=5, pady=5)
        vol_frame = ttk.Frame(settings_frame)
        vol_frame.pack(fill="x", pady=5)
        ttk.Label(vol_frame, text="Volume (dB):").pack(side="left", padx=(0,5))
        ttk.Scale(vol_frame, from_=-30, to=12, variable=self.volume_db,
                orient="horizontal", length=200).pack(side="left")
        ttk.Label(vol_frame, textvariable=self.volume_db, width=5).pack(side="left", padx=(5,0))
        loop_frame = ttk.Frame(settings_frame)
        loop_frame.pack(fill="x", pady=(0,5))
        ttk.Label(loop_frame, text="Loop length (min, 0=∞):").pack(side="left", padx=(0,5))
        ttk.Entry(loop_frame, textvariable=self.loop_min, width=6).pack(side="left")

        # Status bar
        self.status = ttk.Label(right, text="", foreground="green", font=("Arial", 11))
        self.status.pack(fill="x", padx=5, pady=(0,5))

    # ── tree helpers ------------------------------------------------------
    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for r in self.affirmations:
            tag = ("highlight",) if str(r["id"]) == self.selected_id else ()
            self.tree.insert("", "end", iid=str(r["id"]), text=r["title"],
                            values=(r["created"].split("T")[0], f"{r['db']}"), tags=tag)

    def _on_select(self, _=None):
        sel = self.tree.selection()
        if sel:
            self.selected_id = sel[0]
            self._load_editor()
            self._refresh_tree()

    def _select_by_id(self, rid: str):
        if self.tree.exists(rid):
            self.tree.selection_set(rid); self.tree.see(rid); self._on_select()

    # ── editor helpers ----------------------------------------------------
    def _set_title(self, txt: str):
        self.title_text = txt
        self.title_lbl.config(text=txt)

    def _on_add(self):
        self.selected_id = None
        self._set_title("(unsaved)")
        self.text.delete("1.0", "end")
        self.audio_data = None
        self.volume_db.set(-15.0)
        self.loop_min.set(0.0)
        self.status.config(text="Ready")
        self._refresh_tree()

    def _on_delete(self):
        if not self.selected_id:
            return
        rec = next((r for r in self.affirmations if str(r["id"]) == self.selected_id), None)
        if rec and messagebox.askyesno("Delete", f"Delete '{rec['title']}'?"):
            wav = A_DIR / rec["file"]
            if wav.exists():
                wav.unlink()
            self.affirmations.remove(rec)
            self._save_meta()
            self._refresh_tree()
            self._on_add()

    def _load_editor(self):
        rec = next((r for r in self.affirmations if str(r["id"]) == self.selected_id), None)
        if not rec:
            return
        self._set_title(rec["title"])
        self.text.delete("1.0", "end")
        self.text.insert("1.0", rec["text"])
        self.volume_db.set(rec.get("db", -15.0))
        self.loop_min.set(rec.get("loop_min", 0.0))
        wav = A_DIR / rec["file"]
        if wav.exists():
            data, sr = sf.read(str(wav), always_2d=False)
            if sr != SRATE:
                data = np.interp(
                    np.linspace(0, len(data), int(len(data) * SRATE / sr), False),
                    np.arange(len(data)),
                    data
                )
            self.audio_data = data.astype("float32")
        else:
            self.audio_data = None
        self.status.config(text=f"Loaded '{rec['title']}'")

    # ── recording ---------------------------------------------------------
    def _toggle_record(self):
        if not self.recording:
            if self.mode.get() != "rec":
                messagebox.showinfo("Mode", "Switch to 'Record Voice' first.")
                return
            self.record_buf = []
            self.record_stream = sd.InputStream(
                samplerate=SRATE, channels=1, blocksize=BLOCK,
                callback=lambda ind, *_: self.record_buf.append(ind.copy())
            )
            self.record_stream.start()
            self.recording = True
            self.rec_btn.config(text="■ Stop")
            self.status.config(text="Recording…")
        else:
            self._stop_record()

    def _stop_record(self):
        if not self.recording:
            return
        self.record_stream.stop()
        self.record_stream.close()
        self.recording = False
        self.rec_btn.config(text="⏺ Record")
        data = np.concatenate(self.record_buf, axis=0)
        self.audio_data = data.astype("float32")
        self.buf_len = len(data)
        # prompt for title and save automatically
        title = simpledialog.askstring(
            "New Recording Title",
            "Enter a title for your new recording:",
            parent=self.master
        )
        if title:
            new_id = str(uuid.uuid4())
            fname = f"{new_id}.wav"
            sf.write(str(A_DIR / fname), self.audio_data, SRATE)
            rec = {
                "id": new_id,
                "file": fname,
                "text": self.text.get("1.0", "end").strip(),
                "title": title,
                "db": self.volume_db.get(),
                "loop_min": self.loop_min.get(),
                "created": datetime.now().isoformat()
            }
            self.affirmations.insert(0, rec)
            self._save_meta()
            self.selected_id = new_id
            self._refresh_tree()
            self._select_by_id(new_id)
            self.status.config(text="Recording saved.")
        else:
            self.status.config(text="Recording discarded.")

    # ── playback ----------------------------------------------------------
    def _toggle_play(self):
        if not self.is_playing:
            if self.mode.get() == "tts":
                text = self.text.get("1.0", "end").strip()
                engine = pyttsx3.init()
                engine.save_to_file(text, "tmp.wav")
                engine.runAndWait()
                data, sr = sf.read("tmp.wav", always_2d=False)
                os.remove("tmp.wav")
                if sr != SRATE:
                    data = np.interp(
                        np.linspace(0, len(data), int(len(data) * SRATE / sr), False),
                        np.arange(len(data)),
                        data
                    )
                self.audio_data = data.astype("float32")
            if self.audio_data is None:
                messagebox.showwarning("No audio", "Nothing to play.")
                return
            factor = 10 ** (self.volume_db.get() / 20)
            self.audio_data *= factor
            self.play_ptr = 0
            self.buf_len = len(self.audio_data)
            self.play_stream = sd.OutputStream(
                samplerate=SRATE, channels=1, blocksize=BLOCK,
                callback=self._play_callback
            )
            self.play_stream.start()
            self.is_playing = True
            self.rec_btn.config(text="■ Stop")
            self.status.config(text="Playing…")
        else:
            self._stop_play()

    def _play_callback(self, out, frames, time, status):
        if status:
            print(status)
        end = self.play_ptr + frames
        chunk = self.audio_data[self.play_ptr:end]
        if len(chunk) < frames:
            chunk = np.pad(chunk, (0, frames - len(chunk)))
            self._stop_play()
        out[:] = chunk.reshape(-1, 1)
        self.play_ptr = end

    def _stop_play(self):
        if not self.is_playing:
            return
        self.play_stream.stop()
        self.play_stream.close()
        self.is_playing = False
        self.status.config(text="")

    # ── save --------------------------------------------------------------
    def _save(self):
        text = self.text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("No text", "Affirmation text is empty.")
            return
        title = simpledialog.askstring(
            "Title",
            "Enter a title for this affirmation:",
            initialvalue=self.title_text or text[:30],
            parent=self.master
        )
        if not title:
            return
        new_id = self.selected_id or str(uuid.uuid4())
        fname = f"{new_id}.wav"
        sf.write(str(A_DIR / fname), self.audio_data, SRATE)
        rec = {
            "id": new_id,
            "file": fname,
            "text": text,
            "title": title,
            "db": self.volume_db.get(),
            "loop_min": self.loop_min.get(),
            "created": datetime.now().isoformat()
        }
        if self.selected_id:
            self.affirmations = [
                r if str(r["id"]) != new_id else rec for r in self.affirmations
            ]
        else:
            self.affirmations.insert(0, rec)
            self.selected_id = new_id
        self._save_meta()
        self._refresh_tree()
        self._select_by_id(new_id)
        self._set_title(title)
        messagebox.showinfo("Saved", "Affirmation saved.")
        self.status.config(text="")

    # ── run ---------------------------------------------------------------
    def run(self):
        self.master.mainloop()

# ── entry ---------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    AffirmationApp(root).run()
