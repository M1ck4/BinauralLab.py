import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from scipy.io.wavfile import write
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os

class BinauralApp:
    PRESETS_FILE = "binaural_presets.json"
    DEFAULT_PRESETS = {
        # ─── Delta Waves (0.5–4 Hz) ───────────────────────────────
        "Delta Sleep":      {"carrier": 120.0, "beat": 3.5,  "desc": "Delta rhythm for restful, deep sleep."},
        "Delta Healing":    {"carrier": 100.0, "beat": 2.5,  "desc": "Deep delta for physical healing and regeneration."},
        "Delta Renewal":    {"carrier": 100.0, "beat": 1.0,  "desc": "Ultra-low delta for cellular repair."},
        "Deep Sleep":       {"carrier": 100.0, "beat": 1.5,  "desc": "Sub-delta drift: ideal for deep sleep and hypnosis."},
        "Float State":      {"carrier":  80.0, "beat": 0.5,  "desc": "Delta flotation state for deep introspection."},
        "Astral Hum":       {"carrier":  30.0, "beat": 0.7,  "desc": "Sub-delta hum to ease into astral travel."},
        "Focus 3":          {"carrier": 200.0, "beat": 3.0,  "desc": "Monroe Institute Focus 3 pre-hypnagogic state."},

        # ─── Theta Waves (4–8 Hz) ────────────────────────────────
        "Theta Relax":       {"carrier": 200.0, "beat": 6.0,  "desc": "Gentle theta for relaxation and stress reduction."},
        "Theta Meditation":  {"carrier": 250.0, "beat": 5.0,  "desc": "Theta rhythm for deep meditation."},
        "Theta Insight":     {"carrier": 220.0, "beat": 7.0,  "desc": "Theta for creative insights and intuition."},
        "Gateway Voyage":    {"carrier": 100.0, "beat": 4.0,  "desc": "Access deeper mind states, OBEs."},
        "Lucid Entry":       {"carrier": 140.0, "beat": 6.0,  "desc": "High-theta for lucid dreaming."},
        "Deep Theta OBE":    {"carrier": 180.0, "beat": 5.5,  "desc": "Theta tuned for out-of-body induction."},
        "Astra Journey":     {"carrier": 210.0, "beat": 7.5,  "desc": "Theta blend for guided astral exploration."},
        "OBE Induction":     {"carrier": 130.0, "beat": 4.5,  "desc": "Hemi-Sync out-of-body induction pattern."},
        "Patterning":        {"carrier": 110.0, "beat": 7.0,  "desc": "Hemi-Sync patterning for visualization."},
        "Stargate Schumann": {"carrier": 100.0, "beat": 7.83, "desc": "Schumann resonance for clarity."},
        "Stargate Protocol I":{"carrier":  90.0, "beat": 6.5,  "desc": "Project Stargate training pattern I."},

        # ─── Alpha Waves (8–12 Hz) ───────────────────────────────
        "Alpha Relax":       {"carrier": 300.0, "beat":10.0,  "desc": "Alpha for calm and stress relief."},
        "Alpha Creativity":  {"carrier": 270.0, "beat": 8.0,  "desc": "Alpha to boost creative thinking."},
        "Alpha Focus":       {"carrier": 260.0, "beat":12.0,  "desc": "Upper alpha for improved concentration."},
        "Alpha Memory":      {"carrier": 240.0, "beat": 9.0,  "desc": "Alpha to enhance memory retention."},
        "Mind Mirror":       {"carrier": 150.0, "beat": 8.0,  "desc": "Alpha/SMR blend for clarity."},
        "Light Journey":     {"carrier": 200.0, "beat":10.0,  "desc": "Alpha exploration for awareness."},
        "Focus 10":          {"carrier": 100.0, "beat":10.0,  "desc": "Mind awake, body asleep state."},
        "Focus 12":          {"carrier": 100.0, "beat":12.0,  "desc": "Expanded awareness state."},
        "Stargate Protocol II":{"carrier":  90.0, "beat": 9.5,  "desc": "Project Stargate pattern II."},

        # ─── Beta Waves (13–30 Hz) ──────────────────────────────
        "Beta Focus":       {"carrier": 210.0, "beat":14.0, "desc": "Low beta for focused attention."},
        "Beta Cognition":   {"carrier": 200.0, "beat":16.0, "desc": "Mid beta for analytical thinking."},
        "Beta Alertness":   {"carrier": 160.0, "beat":18.0, "desc": "High beta for alertness."},
        "Beta Energy":      {"carrier": 150.0, "beat":20.0, "desc": "High beta for motivation."},
        "Beta Performance": {"carrier": 180.0, "beat":22.0, "desc": "Peak beta for performance."},
        "Peak Focus":       {"carrier": 250.0, "beat":14.0, "desc": "Low-beta concentration boost."},
        "Brain Spark":      {"carrier": 200.0, "beat":25.0, "desc": "High-beta spark for alertness."},
        "Focus 15":         {"carrier": 200.0, "beat":15.0, "desc": "Focus 15: no-time awareness."},
        "Focus 21":         {"carrier": 150.0, "beat":21.0, "desc": "Focus 21: astral time travel."},
        "Focus 27":         {"carrier": 150.0, "beat":27.0, "desc": "Focus 27: exploration."},

        # ─── Gamma Waves (30–50 Hz) ─────────────────────────────
        "Gamma Integration":   {"carrier": 400.0, "beat":30.0, "desc": "Gamma for information integration."},
        "Gamma Learning":      {"carrier": 360.0, "beat":35.0, "desc": "Gamma for accelerated learning."},
        "Gamma Cognition":     {"carrier": 420.0, "beat":40.0, "desc": "High gamma for cognition."},
        "Gamma Consciousness": {"carrier": 300.0, "beat":45.0, "desc": "Gamma for expanded awareness."},
    }
    CATEGORIES = {
        "Delta Waves (0.5–4 Hz)": list(DEFAULT_PRESETS.keys())[:7],
        "Theta Waves (4–8 Hz)":   list(DEFAULT_PRESETS.keys())[7:18],
        "Alpha Waves (8–12 Hz)":  list(DEFAULT_PRESETS.keys())[18:27],
        "Beta Waves (13–30 Hz)":  list(DEFAULT_PRESETS.keys())[27:37],
        "Gamma Waves (30–50 Hz)": list(DEFAULT_PRESETS.keys())[37:41],
    }
    SAMPLE_RATE = 44100
    BLOCKSIZE = 1024

    def __init__(self, master):
        self.master = master
        master.title("Binaural Beat Lab")
        master.geometry('900x780')  # taller for full graph

        self.left_phase = 0.0
        self.right_phase = 0.0
        self.stream = None
        self.selected_preset = None

        self.carrier_var = tk.DoubleVar(value=100.0)
        self.beat_var    = tk.DoubleVar(value=4.0)
        self.volume_var  = tk.DoubleVar(value=0.5)

        self._load_presets()
        self._build_ui()
        self.tree.tag_configure('highlight', background='lightyellow')
        self._init_plot()
        self._refresh_ui()
        self.master.after(100, self._update_plot)

        self.carrier_var.trace_add('write', lambda *a: self._refresh_ui())
        self.beat_var.trace_add('write',    lambda *a: self._refresh_ui())

    def _load_presets(self):
        if not os.path.exists(self.PRESETS_FILE):
            with open(self.PRESETS_FILE, 'w') as f:
                json.dump(self.DEFAULT_PRESETS, f, indent=4)
        with open(self.PRESETS_FILE, 'r') as f:
            self.presets = json.load(f)

    def _save_presets(self):
        with open(self.PRESETS_FILE, 'w') as f:
            json.dump(self.presets, f, indent=4)

    def _build_ui(self):
        pad = {'padx': 5, 'pady': 5}
        main = ttk.Frame(self.master, padding=10)
        main.pack(fill='both', expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(8, weight=1)
        main.rowconfigure(9, weight=2)

        # Header
        self.preset_label = ttk.Label(main, text='Preset: None', font=('Arial', 12, 'bold'))
        self.preset_label.grid(row=0, column=0, columnspan=4, **pad)
        self.status = ttk.Label(main, text='', font=('Arial', 11))
        self.status.grid(row=1, column=0, columnspan=4, **pad)

        # Carrier
        ttk.Label(main, text='Carrier (Hz)').grid(row=2, column=0, sticky='w', **pad)
        ttk.Scale(main, from_=0.001, to=200, variable=self.carrier_var,
                  orient='horizontal').grid(row=2, column=1, sticky='ew', **pad)
        ttk.Entry(main, textvariable=self.carrier_var, width=8).grid(row=2, column=2, sticky='e', **pad)

        # Beat
        ttk.Label(main, text='Beat Δf (Hz)').grid(row=3, column=0, sticky='w', **pad)
        ttk.Scale(main, from_=0.001, to=50, variable=self.beat_var,
                  orient='horizontal').grid(row=3, column=1, sticky='ew', **pad)
        ttk.Entry(main, textvariable=self.beat_var, width=8).grid(row=3, column=2, sticky='e', **pad)

        # Volume
        ttk.Label(main, text='Volume').grid(row=4, column=0, sticky='w', **pad)
        ttk.Scale(main, from_=0, to=1, variable=self.volume_var,
                  orient='horizontal').grid(row=4, column=1, columnspan=2, sticky='ew', **pad)

        # Playback
        pf = ttk.Frame(main)
        pf.grid(row=5, column=0, columnspan=4, **pad)
        ttk.Button(pf, text='▶ Start', command=self.start_audio).pack(side='left', **pad)
        ttk.Button(pf, text='■ Stop',  command=self.stop_audio).pack(side='left', **pad)

        # Preset actions
        ttk.Label(main, text='Preset Name').grid(row=6, column=0, sticky='w', **pad)
        self.preset_entry = ttk.Entry(main)
        self.preset_entry.grid(row=6, column=1, columnspan=2, sticky='ew', **pad)
        af = ttk.Frame(main)
        af.grid(row=7, column=0, columnspan=4, **pad)
        ttk.Button(af, text='💾 Save',   command=self.save_preset).pack(side='left', **pad)
        ttk.Button(af, text='🗑️ Delete', command=self.delete_preset).pack(side='left', **pad)
        ttk.Button(af, text='⬇ Export',  command=self.export_audio).pack(side='left', **pad)

        # Load presets with scrollbar
        ttk.Label(main, text='Load Preset').grid(row=8, column=0, sticky='nw', **pad)
        tree_frame = ttk.Frame(main)
        tree_frame.grid(row=8, column=1, columnspan=3, sticky='nsew', **pad)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(tree_frame, columns=('Desc',), show='tree headings', selectmode='browse')
        self.tree.heading('#0', text='Preset')
        self.tree.heading('Desc', text='Description')
        self.tree.column('#0', width=200)
        self.tree.column('Desc', width=400)
        vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        self.tree.bind('<<TreeviewSelect>>', self.load_preset)

        # Visualization
        self.viz_frame = ttk.Frame(main)
        self.viz_frame.grid(row=9, column=0, columnspan=4, sticky='nsew', **pad)

        # Footer reminder
        footer = ttk.Label(main,
            text="Binaural beats work best with stereo headphones.",
            font=('Arial', 9, 'italic'), foreground='gray')
        footer.grid(row=10, column=0, columnspan=4, pady=(2,0))

    def _init_plot(self):
        self.fig = Figure(figsize=(6, 2.5), dpi=100)
        self.fig.subplots_adjust(left=0.12, right=0.98, top=0.92, bottom=0.10, hspace=0.4)

        self.ax1 = self.fig.add_subplot(211)
        self.line1, = self.ax1.plot([], [], lw=1, label='Left')
        self.line2, = self.ax1.plot([], [], lw=1, label='Right')
        self.ax1.set_ylabel('Amplitude', labelpad=10)
        self.ax1.set_ylim(-1, 1)
        self.ax1.legend(loc='upper right', fontsize='small')

        self.ax2 = self.fig.add_subplot(212)
        self.env_line, = self.ax2.plot([], [], lw=1)
        self.ax2.set_xlabel('Time (s)')
        self.ax2.set_ylabel('Envelope', labelpad=10)
        self.ax2.set_ylim(0, 1)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def _update_plot(self):
        b = self.beat_var.get() or 1.0
        window = min(0.5, max(0.05, 2.0 / b))
        t = np.linspace(0, window, int(self.SAMPLE_RATE * window), endpoint=False)
        c = self.carrier_var.get()
        y1 = np.sin(2 * np.pi * c * t)
        y2 = np.sin(2 * np.pi * (c + b) * t)
        env = np.abs(y1 - y2) / 2

        self.line1.set_data(t, y1)
        self.line2.set_data(t, y2)
        self.env_line.set_data(t, env)
        self.ax1.set_xlim(0, window)
        self.ax2.set_xlim(0, window)

        self.canvas.draw()
        self.master.after(100, self._update_plot)

    def _refresh_ui(self):
        # update header
        name = self.selected_preset or 'None'
        self.preset_label.config(text=f'Preset: {name}')
        self.status.config(text=f'Carrier: {self.carrier_var.get():.3f} Hz | Beat: {self.beat_var.get():.3f} Hz')

        # rebuild tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        for cat, names in self.CATEGORIES.items():
            parent = self.tree.insert('', 'end', text=cat, open=True)
            for n in names:
                if n in self.presets:
                    desc = self.presets[n].get('desc', '')
                    tags = ('highlight',) if n == self.selected_preset else ()
                    self.tree.insert(parent, 'end', text=n, values=(desc,), tags=tags)

        custom = [n for n in self.presets if n not in self.DEFAULT_PRESETS]
        if custom:
            parent = self.tree.insert('', 'end', text='Custom Sounds', open=True)
            for n in custom:
                desc = self.presets[n].get('desc', '')
                tags = ('highlight',) if n == self.selected_preset else ()
                self.tree.insert(parent, 'end', text=n, values=(desc,), tags=tags)

    def start_audio(self):
        if self.stream:
            self.stop_audio()
        self.stream = sd.OutputStream(
            samplerate=self.SAMPLE_RATE,
            channels=2,
            blocksize=self.BLOCKSIZE,
            callback=self._audio_callback
        )
        self.stream.start()

    def stop_audio(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def _audio_callback(self, outdata, frames, time, status):
        c, b = self.carrier_var.get(), self.beat_var.get()
        v    = self.volume_var.get()
        d1 = 2 * np.pi * c / self.SAMPLE_RATE
        d2 = 2 * np.pi * (c + b) / self.SAMPLE_RATE
        idx = np.arange(frames)
        p1  = self.left_phase + d1 * idx
        p2  = self.right_phase + d2 * idx

        chunk = np.stack([np.sin(p1), np.sin(p2)], axis=-1).astype(np.float32) * v
        outdata[:] = chunk

        self.left_phase  = (p1[-1] + d1) % (2 * np.pi)
        self.right_phase = (p2[-1] + d2) % (2 * np.pi)

    def save_preset(self):
        name = self.preset_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter preset name.")
            return
        desc = simpledialog.askstring("Description", "Brief usage notes:") or ''
        self.presets[name] = {
            'carrier': self.carrier_var.get(),
            'beat':    self.beat_var.get(),
            'desc':    desc
        }
        self.selected_preset = name
        self._save_presets()
        self._refresh_ui()
        messagebox.showinfo("Saved", f"Preset '{name}' saved.")

    def delete_preset(self):
        name = self.selected_preset
        if not name:
            messagebox.showwarning("No Selection", "Please load a preset to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
            return
        self.presets.pop(name, None)
        self.selected_preset = None
        self.preset_entry.delete(0, tk.END)
        self._save_presets()
        self._refresh_ui()
        messagebox.showinfo("Deleted", f"Preset '{name}' deleted.")

    def load_preset(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        parent = self.tree.parent(item)
        if not parent:
            return
        name = self.tree.item(item, 'text')
        prefs = self.presets.get(name)
        if not prefs:
            return
        self.selected_preset = name
        self.preset_entry.delete(0, tk.END)
        self.preset_entry.insert(0, name)
        self.carrier_var.set(prefs['carrier'])
        self.beat_var.set(prefs['beat'])
        self._refresh_ui()

    def export_audio(self):
        dur = simpledialog.askfloat("Export", "Length (sec):", initialvalue=5.0)
        if not dur or dur <= 0:
            return
        fs = self.SAMPLE_RATE
        t  = np.linspace(0, dur, int(fs * dur), endpoint=False)
        c, b = self.carrier_var.get(), self.beat_var.get()
        left  = np.sin(2 * np.pi * c * t)
        right = np.sin(2 * np.pi * (c + b) * t)
        data  = np.int16(
            np.stack([left, right], axis=-1) /
            np.max(np.abs(np.stack([left, right], axis=-1))) * 32767
        )
        fn = filedialog.asksaveasfilename(defaultextension='.wav', filetypes=[('WAV','*.wav')])
        if fn:
            write(fn, fs, data)
            messagebox.showinfo("Exported", f"Saved to {fn}")

if __name__ == '__main__':
    root = tk.Tk()
    BinauralApp(root)
    root.mainloop()
