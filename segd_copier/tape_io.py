import os

class TapeReader:
    """
    Simule la lecture d'un lecteur de bande magnétique en lisant un fichier
    standard par blocs de taille fixe.

    Pour un usage réel sur Linux, les méthodes devraient utiliser des commandes
    comme `os.system('mt ...')` ou des `ioctl` pour contrôler le périphérique /dev/stX.
    """
    def __init__(self, block_size=32768):
        """
        Initialise le lecteur de bande simulé.

        Args:
            block_size (int): La taille de chaque bloc à lire, en octets.
                              Par défaut, 32 Ko.
        """
        self.device_path = None
        self.file = None
        self.block_size = block_size

    def open(self, device_path: str):
        """
        Ouvre le périphérique de bande simulé (un fichier).

        Args:
            device_path (str): Le chemin vers le fichier à lire.
        """
        if self.file:
            self.close()

        self.device_path = device_path
        try:
            # En simulation, on ouvre simplement un fichier.
            self.file = open(self.device_path, 'rb')
            print(f"Périphérique simulé '{self.device_path}' ouvert.")
        except FileNotFoundError:
            print(f"Erreur: Le fichier de simulation '{self.device_path}' n'a pas été trouvé.")
            self.file = None
            raise

    def close(self):
        """Ferme le périphérique de bande simulé."""
        if self.file:
            self.file.close()
            print(f"Périphérique simulé '{self.device_path}' fermé.")
            self.file = None
            self.device_path = None

    def read_block(self) -> bytes:
        """
        Lit un seul bloc de données depuis le périphérique.

        Returns:
            bytes: Les données lues (de taille `block_size`), ou un objet
                   bytes vide si la fin de la bande (fichier) est atteinte.
        """
        if not self.file:
            raise IOError("Aucun périphérique n'est ouvert. Appelez open() d'abord.")

        return self.file.read(self.block_size)

    def rewind(self):
        """Rembobine la bande (revient au début du fichier)."""
        if not self.file:
            raise IOError("Aucun périphérique n'est ouvert. Appelez open() d'abord.")

        self.file.seek(0)
        print("Bande simulée rembobinée.")

    def __enter__(self):
        # Permet d'utiliser l'objet avec 'with'
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Assure que le fichier est fermé, même en cas d'erreur
        self.close()
