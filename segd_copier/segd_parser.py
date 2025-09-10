import struct

def parse_record_header(data: bytes) -> dict:
    """
    Parse les informations de base de l'en-tête général SEGD (bloc #1).

    Args:
        data (bytes): Un bloc de données brutes (doit faire au moins 32 octets).

    Returns:
        dict: Un dictionnaire contenant les informations parsées,
              ou des valeurs par défaut en cas d'erreur.
    """
    header_info = {
        'file_number': -1,
        'format_code': -1,
        'year': -1,
        'day_of_year': -1,
        'error': None
    }

    # L'en-tête général #1 fait 32 octets.
    if len(data) < 32:
        header_info['error'] = "Données insuffisantes pour l'en-tête (moins de 32 octets)."
        return header_info

    try:
        # Le format SEGD est Big Endian (>).
        # On ne parse que quelques champs pour ce listing simple.

        # Numéro de fichier (File Number): octets 1-2 (unsigned short)
        file_number = struct.unpack('>H', data[0:2])[0]

        # Code Format: octet 3 (unsigned char)
        format_code = struct.unpack('>B', data[2:3])[0]

        # Année: octet 7 (unsigned char)
        year = struct.unpack('>B', data[6:7])[0]

        # Jour de l'année: octets 8-9 (unsigned short)
        day_of_year = struct.unpack('>H', data[7:9])[0]

        header_info.update({
            'file_number': file_number,
            'format_code': format_code,
            'year': year + 2000 if year < 100 else year, # Heuristique simple pour l'année
            'day_of_year': day_of_year,
        })

    except struct.error as e:
        header_info['error'] = f"Erreur de parsing (struct): {e}"
    except Exception as e:
        header_info['error'] = f"Erreur inattendue: {e}"

    return header_info
