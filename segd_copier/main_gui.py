import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import time
from .controller import transcribe_data, analyze_source

class MainApplication(tk.Frame):
    """
    Classe principale pour l'interface graphique de l'utilitaire de copie SEGD.
    """
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.parent.title("Utilitaire de Copie SEGD")
        self.parent.geometry("850x600")
        self.parent.minsize(700, 450)

        self.copy_queue = queue.Queue()
        self._create_widgets()

    def _select_source_file(self):
        """Opens a dialog to select one or more source files."""
        if self.source_button['state'] == 'disabled': return

        paths = filedialog.askopenfilenames(
            title="Sélectionner un ou plusieurs fichiers source",
            filetypes=(("Fichiers SEGD", "*.segd"), ("Tous les fichiers", "*.*"))
        )
        if paths:
            self.source_path.set(f'"{'" "'.join(paths)}"')
            self.status_text.set(f"{len(paths)} fichier(s) source sélectionné(s).")

    def _select_dest_file(self):
        """Opens a dialog to select a destination file or directory."""
        if self.dest_button['state'] == 'disabled': return

        if self.source_type.get() == 'tape' and self.dest_type.get() == 'file':
            path = filedialog.askdirectory(
                title="Choisir le répertoire de destination pour les fichiers de la bande"
            )
        else:
            path = filedialog.asksaveasfilename(
                title="Choisir le fichier de destination",
                defaultextension=".segd",
                filetypes=(("Fichiers SEGD", "*.segd"), ("Tous les fichiers", "*.*"))
            )

        if path:
            self.dest_path.set(path)
            self.status_text.set(f"Destination: {path}")

    def _start_analysis(self):
        """Starts the source analysis process."""
        source = self.source_path.get()
        if not source:
            messagebox.showerror("Erreur", "Le chemin source doit être spécifié.")
            return

        self._log(f"Analyse de la source : {source}...")
        self.copy_button.config(state="disabled")

        version = analyze_source(source)

        if version:
            self._log(f"Source valide détectée : SEGD Version {version}.")
            self.status_text.set(f"Prêt à copier (SEGD Rev {version}).")
            self.copy_button.config(state="normal")
        else:
            self._log("Erreur: Format de source non reconnu ou fichier invalide.")
            self.status_text.set("Analyse échouée.")
            messagebox.showerror("Analyse échouée", "Le fichier source n'est pas un fichier SEGD valide ou est illisible.")

    def _start_copy(self):
        """Validates paths and starts the transcription process in a thread."""
        source = self.source_path.get()
        dest = self.dest_path.get()

        if not source or not dest:
            messagebox.showerror("Erreur", "Les chemins source et destination doivent être spécifiés.")
            return

        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

        self._log("Démarrage de la transcription...")

        self.progress_var.set(0)
        self.progress_size_text.set("0 MB / 0 MB")
        self.progress_speed_text.set("0 MB/s")
        self.bytes_copied = 0
        self.total_size = 0
        self.start_time = time.time()

        self._set_ui_state("disabled")

        thread = threading.Thread(target=self._copy_worker, args=(source, dest, self.copy_queue))
        thread.daemon = True
        thread.start()

        self.parent.after(100, self._process_queue)

    def _copy_worker(self, source, dest, q):
        """The thread-safe function that calls the controller and puts results in the queue."""
        try:
            for entry in transcribe_data(source, dest):
                q.put(entry)
        except Exception as e:
            q.put(e)
        finally:
            q.put(None)

    def _log(self, message):
        """Appends a message to the log widget."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state="disabled")
        self.log_text.yview(tk.END)

    def _process_queue(self):
        """Processes messages from the queue to update the UI."""
        try:
            while True:
                msg = self.copy_queue.get_nowait()

                if msg is None:
                    self._set_ui_state("normal")
                    return
                elif isinstance(msg, Exception):
                    error_msg = f"Erreur de Transcription: {msg}"
                    messagebox.showerror("Erreur", error_msg)
                    self._log(error_msg)
                    self.status_text.set("Erreur.")
                    self._set_ui_state("normal")
                    return

                if 'error' in msg:
                    self._log(f"Erreur: {msg['error']}")
                    self.status_text.set("Erreur.")
                elif 'status' in msg:
                    self._log(msg['status'])
                elif 'total_size' in msg:
                    self.total_size = msg['total_size']
                    self.bytes_copied = 0
                    if self.total_size <= 0:
                        self.progressbar.config(mode='indeterminate')
                        self.progressbar.start()
                        self._log("Taille totale inconnue (source de type bande).")
                    else:
                        self.progressbar.config(mode='determinate')
                        self._log(f"Taille totale de la source : {self.total_size/1e6:.2f} MB.")
                elif 'checksum_ok' in msg:
                    self.progressbar.stop()
                    self.progress_var.set(100)
                    if msg['checksum_ok'] is True:
                        self.status_text.set("Transcription terminée. Checksum OK !")
                        self._log("Vérification du Checksum : OK. La copie est identique.")
                    elif msg['checksum_ok'] is False:
                        self.status_text.set("ERREUR: La vérification du Checksum a échoué !")
                        self._log("ERREUR: Le checksum de la destination ne correspond pas à la source !")
                    else: # 'n/a' case
                        self.status_text.set("Transcription multi-fichiers terminée.")
                        self._log("Validation par checksum non applicable pour le mode multi-fichiers.")
                else:
                    if hasattr(self, 'total_size'):
                        record_size_bytes = float(msg.get('size_kb', 0)) * 1024
                        self.bytes_copied += record_size_bytes

                        if self.total_size > 0:
                            progress = (self.bytes_copied / self.total_size) * 100
                            self.progress_var.set(progress)
                            self.progress_size_text.set(f"{self.bytes_copied/1e6:.1f} MB / {self.total_size/1e6:.1f} MB")
                        else:
                            self.progress_size_text.set(f"{self.bytes_copied/1e6:.1f} MB copiés")

                        elapsed_time = time.time() - self.start_time
                        if elapsed_time > 0:
                            speed = self.bytes_copied / elapsed_time / 1e6
                            self.progress_speed_text.set(f"{speed:.2f} MB/s")

        except queue.Empty:
            self.parent.after(100, self._process_queue)

    def _set_ui_state(self, state):
        """Enables or disables interactive widgets."""
        if state == "disabled":
            self.analyze_button.config(state="disabled")
            self.copy_button.config(state="disabled")
        else:
            self.analyze_button.config(state="normal")

        self._update_widget_states()

    def _update_widget_states(self):
        """Enable/disable widgets based on radio button selections."""
        if self.analyze_button['state'] == 'disabled':
            return

        if self.source_type.get() == "tape":
            self.source_button.config(state="disabled")
        else:
            self.source_button.config(state="normal")

        if self.dest_type.get() == "tape":
            self.dest_button.config(state="disabled")
        else:
            self.dest_button.config(state="normal")

    def _create_widgets(self):
        """Crée et positionne tous les widgets de l'interface."""
        style = ttk.Style(self)
        style.theme_use("clam")

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        config_panel = ttk.Frame(main_frame)
        config_panel.pack(fill="x", expand=False, pady=5)
        config_panel.columnconfigure(0, weight=1)
        config_panel.columnconfigure(1, weight=1)

        source_frame = ttk.LabelFrame(config_panel, text="Source", padding="10")
        source_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        source_frame.columnconfigure(1, weight=1)

        self.source_type = tk.StringVar(value="file")
        ttk.Radiobutton(source_frame, text="Fichier(s)", variable=self.source_type, value="file", command=self._update_widget_states).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(source_frame, text="Bande Magnétique", variable=self.source_type, value="tape", command=self._update_widget_states).grid(row=0, column=1, sticky="w")

        self.source_path = tk.StringVar()
        source_entry = ttk.Entry(source_frame, textvariable=self.source_path, width=40)
        source_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        self.source_button = ttk.Button(source_frame, text="Parcourir Fichiers...", command=self._select_source_file)
        self.source_button.grid(row=2, column=0, columnspan=2, sticky="e", pady=5)

        dest_frame = ttk.LabelFrame(config_panel, text="Destination", padding="10")
        dest_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        dest_frame.columnconfigure(1, weight=1)

        self.dest_type = tk.StringVar(value="file")
        ttk.Radiobutton(dest_frame, text="Fichier/Répertoire", variable=self.dest_type, value="file", command=self._update_widget_states).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(dest_frame, text="Bande Magnétique", variable=self.dest_type, value="tape", command=self._update_widget_states).grid(row=0, column=1, sticky="w")

        self.dest_path = tk.StringVar()
        dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_path, width=40)
        dest_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        self.dest_button = ttk.Button(dest_frame, text="Parcourir...", command=self._select_dest_file)
        self.dest_button.grid(row=2, column=0, columnspan=2, sticky="e", pady=5)

        progress_frame = ttk.LabelFrame(main_frame, text="Progression", padding="10")
        progress_frame.pack(fill="x", expand=False, pady=5)
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progressbar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)

        self.progress_size_text = tk.StringVar(value="0 MB / 0 MB")
        ttk.Label(progress_frame, textvariable=self.progress_size_text).grid(row=1, column=0, sticky="w")

        self.progress_speed_text = tk.StringVar(value="0 MB/s")
        ttk.Label(progress_frame, textvariable=self.progress_speed_text, anchor="e").grid(row=1, column=1, sticky="e")

        log_frame = ttk.LabelFrame(main_frame, text="Journal d'Événements", padding="10")
        log_frame.pack(fill="both", expand=True, pady=5)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=10, state="disabled", wrap="word")
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.grid(row=0, column=1, sticky="ns")

        controls_frame = ttk.Frame(main_frame, padding="5")
        controls_frame.pack(fill="x", expand=False)
        controls_frame.columnconfigure(0, weight=1)

        self.status_text = tk.StringVar(value="Prêt.")
        status_bar = ttk.Label(controls_frame, textvariable=self.status_text, anchor="w")
        status_bar.grid(row=0, column=0, sticky="ew")

        quit_button = ttk.Button(controls_frame, text="Quitter", command=self.parent.destroy)
        quit_button.grid(row=0, column=1, sticky="e", padx=5)

        self.analyze_button = ttk.Button(controls_frame, text="Analyser Source", command=self._start_analysis)
        self.analyze_button.grid(row=0, column=2, sticky="e", padx=5)

        self.copy_button = ttk.Button(controls_frame, text="Démarrer Transcription", command=self._start_copy, state="disabled")
        self.copy_button.grid(row=0, column=3, sticky="e")


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
