import os
from .tape_io import TapeReader
from .disk_writer import SegdDiskWriter
from .segd_parser import parse_record_header

def copy_and_list_tape(tape_device_path: str, output_file_path: str):
    """
    Orchestre la copie d'une bande vers un disque et génère un listing.

    Cette fonction est un générateur, elle 'yield' des informations sur chaque
    bloc lu pour un affichage en temps réel.

    Args:
        tape_device_path (str): Chemin vers le périphérique de bande (ou fichier simulé).
        output_file_path (str): Chemin vers le fichier de sortie sur disque.

    Yields:
        dict: Un dictionnaire contenant les métadonnées de chaque bloc.
    """
    print("Démarrage du processus de copie et de listing...")

    try:
        with TapeReader() as tape_reader, SegdDiskWriter() as disk_writer:
            tape_reader.open(tape_device_path)
            disk_writer.open(output_file_path)

            record_count = 0
            total_bytes = 0

            while True:
                block = tape_reader.read_block()
                if not block:
                    print("\nFin de la bande (fichier) atteinte.")
                    break

                # 1. Écrire le bloc sur le disque
                disk_writer.write_record(block)

                # 2. Parser l'en-tête pour le listing
                header_info = parse_record_header(block)

                # 3. Ajouter des infos supplémentaires et céder le résultat
                record_count += 1
                block_size_kb = len(block) / 1024
                total_bytes += len(block)

                listing_entry = {
                    'record_num': record_count,
                    'size_kb': f"{block_size_kb:.2f}",
                }
                listing_entry.update(header_info)

                yield listing_entry

            print(f"Copie terminée. {record_count} enregistrements copiés ({total_bytes / (1024*1024):.2f} Mo au total).")

    except FileNotFoundError:
        print(f"Erreur critique: Le fichier d'entrée '{tape_device_path}' n'existe pas.")
    except IOError as e:
        print(f"Erreur d'E/S: {e}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue: {e}")


if __name__ == '__main__':
    # --- Configuration pour le test ---
    DUMMY_TAPE_PATH = 'dummy_tape.bin'
    OUTPUT_DISK_FILE = 'disk_copy.segd'

    print("--- Début du test du contrôleur ---")

    # On s'assure que le fichier de sortie n'existe pas pour un test propre
    if os.path.exists(OUTPUT_DISK_FILE):
        os.remove(OUTPUT_DISK_FILE)

    if not os.path.exists(DUMMY_TAPE_PATH):
        print(f"\nAVERTISSEMENT: Le fichier de test '{DUMMY_TAPE_PATH}' n'existe pas encore.")
        print("Le script ne peut pas s'exécuter. Il sera testé à la prochaine étape.")
    else:
        print(f"Lecture de la bande simulée: '{DUMMY_TAPE_PATH}'")
        print(f"Écriture vers le fichier disque: '{OUTPUT_DISK_FILE}'")
        print("-" * 70)
        print("Listing en temps réel:")

        for entry in copy_and_list_tape(DUMMY_TAPE_PATH, OUTPUT_DISK_FILE):
            if entry.get('error'):
                print(f"  Enregistrement {entry['record_num']}: ERREUR - {entry['error']}")
            else:
                print(
                    f"  > Enr.{entry['record_num']:<3} | "
                    f"Fichier SEGD #{entry['file_number']:<5} | "
                    f"Date: {entry['year']}-{entry['day_of_year']:03d} | "
                    f"Taille: {entry['size_kb']} Ko"
                )

        print("-" * 70)

    print("--- Test du contrôleur terminé ---")
