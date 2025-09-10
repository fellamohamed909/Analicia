import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
from .controller import copy_and_list_tape

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
        """Ouvre une boîte de dialogue pour sélectionner le fichier source."""
        if self.source_button['state'] == 'disabled': return
        path = filedialog.askopenfilename(
            title="Sélectionner le fichier source (bande simulée)",
            filetypes=(("Fichiers binaires", "*.bin"), ("Tous les fichiers", "*.*"))
        )
        if path:
            self.source_path.set(path)
            self.status_text.set(f"Fichier source: {path}")

    def _select_dest_file(self):
        """Ouvre une boîte de dialogue pour sélectionner le fichier de destination."""
        if self.dest_button['state'] == 'disabled': return
        path = filedialog.asksaveasfilename(
            title="Choisir le fichier de destination",
            defaultextension=".segd",
            filetypes=(("Fichiers SEGD", "*.segd"), ("Tous les fichiers", "*.*"))
        )
        if path:
            self.dest_path.set(path)
            self.status_text.set(f"Fichier de destination: {path}")

    def _start_copy(self):
        """Valide les chemins et lance le processus de copie dans un thread."""
        source = self.source_path.get()
        dest = self.dest_path.get()

        if not source or not dest:
            messagebox.showerror("Erreur", "Les chemins source et destination doivent être spécifiés.")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        self._set_ui_state("disabled")
        self.status_text.set("Copie en cours...")

        thread = threading.Thread(target=self._copy_worker, args=(source, dest, self.copy_queue))
        thread.daemon = True
        thread.start()

        # Démarrer le polling de la queue
        self.parent.after(100, self._process_queue)

    def _copy_worker(self, source, dest, q):
        """La fonction thread-safe qui appelle le contrôleur et met les résultats dans la queue."""
        try:
            for entry in copy_and_list_tape(source, dest):
                q.put(entry)
        except Exception as e:
            q.put(e)
        finally:
            q.put(None) # Signal de fin

    def _process_queue(self):
        """Traite les messages de la queue pour mettre à jour l'UI."""
        try:
            while True:
                msg = self.copy_queue.get_nowait()

                if msg is None: # Signal de fin
                    self.status_text.set("Copie terminée avec succès !")
                    self._set_ui_state("normal")
                    return # Arrêter le polling
                elif isinstance(msg, Exception):
                    messagebox.showerror("Erreur de copie", f"Une erreur est survenue: {msg}")
                    self.status_text.set(f"Erreur: {msg}")
                    self._set_ui_state("normal")
                    return # Arrêter le polling
                else:
                    # C'est un dictionnaire de listing, on met à jour le tableau
                    self._add_listing_entry(msg)

        except queue.Empty:
            # Si la queue est vide, on continue le polling
            self.parent.after(100, self._process_queue)

    def _add_listing_entry(self, entry: dict):
        """Ajoute une ligne au tableau de listing."""
        values = (
            entry.get('record_num', ''),
            entry.get('file_number', ''),
            entry.get('year', ''),
            entry.get('day_of_year', ''),
            entry.get('size_kb', ''),
            entry.get('error', '')
        )
        self.tree.insert('', 'end', values=values)
        self.tree.yview_moveto(1) # Auto-scroll vers le bas

    def _set_ui_state(self, state):
        """Active ou désactive les widgets interactifs."""
        self.start_button.config(state=state)
        self.source_button.config(state=state)
        self.dest_button.config(state=state)

    def _create_widgets(self):
        """Crée et positionne tous les widgets de l'interface."""
        style = ttk.Style(self)
        style.theme_use("clam")

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        file_frame = ttk.LabelFrame(main_frame, text="Fichiers", padding="10")
        file_frame.pack(fill="x", expand=False, pady=5)
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="Source (bande simulée):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.source_path = tk.StringVar()
        source_entry = ttk.Entry(file_frame, textvariable=self.source_path, width=80)
        source_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.source_button = ttk.Button(file_frame, text="Parcourir...", command=self._select_source_file)
        self.source_button.grid(row=0, column=2, sticky="e", padx=5, pady=2)

        ttk.Label(file_frame, text="Destination (disque):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.dest_path = tk.StringVar()
        dest_entry = ttk.Entry(file_frame, textvariable=self.dest_path, width=80)
        dest_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.dest_button = ttk.Button(file_frame, text="Enregistrer sous...", command=self._select_dest_file)
        self.dest_button.grid(row=1, column=2, sticky="e", padx=5, pady=2)

        listing_frame = ttk.LabelFrame(main_frame, text="Listing des Enregistrements", padding="10")
        listing_frame.pack(fill="both", expand=True, pady=5)
        listing_frame.rowconfigure(0, weight=1)
        listing_frame.columnconfigure(0, weight=1)

        columns = ("#", "file_num", "year", "day", "size_kb", "error")
        self.tree = ttk.Treeview(listing_frame, columns=columns, show="headings")

        self.tree.heading("#", text="# Enr.")
        self.tree.heading("file_num", text="Fichier SEGD #")
        self.tree.heading("year", text="Année")
        self.tree.heading("day", text="Jour")
        self.tree.heading("size_kb", text="Taille (Ko)")
        self.tree.heading("error", text="Erreur")

        self.tree.column("#", width=60, anchor="center")
        self.tree.column("file_num", width=120, anchor="center")
        self.tree.column("year", width=80, anchor="center")
        self.tree.column("day", width=80, anchor="center")
        self.tree.column("size_kb", width=100, anchor="e")
        self.tree.column("error", width=200, anchor="w")

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(listing_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        controls_frame = ttk.Frame(main_frame, padding="5")
        controls_frame.pack(fill="x", expand=False)
        controls_frame.columnconfigure(0, weight=1)

        self.status_text = tk.StringVar(value="Prêt.")
        status_bar = ttk.Label(controls_frame, textvariable=self.status_text, anchor="w")
        status_bar.grid(row=0, column=0, sticky="ew")

        quit_button = ttk.Button(controls_frame, text="Quitter", command=self.parent.destroy)
        quit_button.grid(row=0, column=2, sticky="e", padx=5)

        self.start_button = ttk.Button(controls_frame, text="Démarrer la copie", command=self._start_copy)
        self.start_button.grid(row=0, column=3, sticky="e")


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
