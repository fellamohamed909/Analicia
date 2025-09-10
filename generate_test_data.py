import struct
import os

FILENAME = "dummy_tape.bin"
BLOCK_SIZE = 32768
NUM_BLOCKS = 3

print(f"Génération du fichier de test '{FILENAME}'...")

with open(FILENAME, "wb") as f:
    for i in range(NUM_BLOCKS):
        # Créer un en-tête de 32 octets avec des valeurs de test
        file_number = 123 + i
        format_code = 88 # CORRIGÉ: 88 est une valeur valide pour un octet (était 8058)
        year = 24 # for 2024
        # Le jour 254 + 2 = 256, ce qui est valide pour un Unsigned Short (H)
        day_of_year = 254 + i

        # Format string pour un en-tête de 32 octets (Big Endian)
        header = struct.pack(
            '>H B 3x B H 23x',
            file_number,
            format_code,
            year,
            day_of_year
        )

        # Créer un bloc complet avec l'en-tête et du padding de zéros
        padding_size = BLOCK_SIZE - len(header)
        padding = b'\x00' * padding_size
        block = header + padding

        f.write(block)

print(f"Fichier de test '{FILENAME}' créé avec {NUM_BLOCKS} blocs de {BLOCK_SIZE} octets.")
print(f"Taille totale attendue: {NUM_BLOCKS * BLOCK_SIZE} octets.")
