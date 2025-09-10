class SegdDiskWriter:
    """
    Écrit des enregistrements de données brutes (blocs) dans un fichier sur disque.
    """
    def __init__(self):
        self.output_path = None
        self.file = None

    def open(self, output_path: str):
        """
        Ouvre le fichier de sortie en mode écriture binaire.

        Args:
            output_path (str): Le chemin vers le fichier à créer/écraser.
        """
        if self.file:
            self.close()

        self.output_path = output_path
        try:
            self.file = open(self.output_path, 'wb')
            print(f"Fichier de sortie '{self.output_path}' ouvert pour écriture.")
        except IOError as e:
            print(f"Erreur à l'ouverture du fichier '{self.output_path}': {e}")
            self.file = None
            raise

    def close(self):
        """Ferme le fichier de sortie."""
        if self.file:
            self.file.close()
            print(f"Fichier de sortie '{self.output_path}' fermé.")
            self.file = None
            self.output_path = None

    def write_record(self, data: bytes):
        """
        Écrit un enregistrement (un bloc de données) dans le fichier.

        Args:
            data (bytes): Les données brutes à écrire.
        """
        if not self.file:
            raise IOError("Aucun fichier de sortie n'est ouvert. Appelez open() d'abord.")

        self.file.write(data)

    def __enter__(self):
        # Permet d'utiliser l'objet avec 'with'
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Assure que le fichier est fermé, même en cas d'erreur
        self.close()
