import os
from typing import Optional

from segd.analyzer import analyze_stream
from segd.common.checksum import calculate_checksum
from segd.readers.factory import get_reader
from .disk_writer import SegdDiskWriter
# from .segd_parser import parse_record_header # No longer needed for simple copy

def analyze_source(source_path: str) -> Optional[str]:
    """
    Analyzes the source file to determine its SEGD version.

    Args:
        source_path: The path to the source file to analyze.

    Returns:
        The SEGD version string if recognized, otherwise None.
    """
    try:
        with open(source_path, 'rb') as stream:
            return analyze_stream(stream)
    except FileNotFoundError:
        print(f"Error: Source file not found at {source_path}")
        return None
    except IOError as e:
        print(f"Error reading source file: {e}")
        return None


def transcribe_data(source_path: str, destination_path: str):
    """
    Orchestrates the copy from a source to a destination, yielding
    real-time progress and performing a checksum validation at the end.
    This version dynamically selects the reader based on the SEGD format.

    Args:
        source_path (str): Path to the source device (or file).
        destination_path (str): Path to the destination file.

    Yields:
        dict: A dictionary containing metadata for each block or a final
              validation result.
    """
    print("Starting transcription process...")

    try:
        # Step 1: Analyze the source to get the version
        version = analyze_source(source_path)
        if version is None:
            yield {'error': "Format not recognized or file is invalid."}
            return

        yield {'status': f"SEGD Version {version} detected. Starting copy..."}

        # Yield total size for progress bar if source is a file
        try:
            total_size = os.path.getsize(source_path)
            yield {'total_size': total_size}
        except OSError:
            # Not a regular file (e.g., tape device), so we can't get total size
            yield {'total_size': -1}

        # Step 2: Get the appropriate reader and perform the copy
        ReaderClass = get_reader(version)

        # Multi-file output mode (Tape -> Directory)
        if os.path.isdir(destination_path):
            yield {'status': "Mode multi-fichiers activé (Bande vers Répertoire)."}
            with open(source_path, 'rb') as source_stream:
                # Read the header once to reuse it for each new file
                source_stream.seek(0)
                header_data = source_stream.read(96)

                reader = ReaderClass(source_stream)
                record_count = 0
                for block in reader.read_records():
                    record_count += 1
                    filename = f"record_{record_count:03d}.segd"
                    output_path = os.path.join(destination_path, filename)

                    with SegdDiskWriter() as disk_writer:
                        disk_writer.open(output_path)
                        disk_writer.write_record(header_data) # Write header
                        disk_writer.write_record(block)     # Write data block

                    yield {
                        'record_num': record_count,
                        'size_kb': f"{(len(block) + len(header_data))/1024:.2f}",
                        'status': f"Écrit dans {filename}"
                    }
            yield {'status': "Copie multi-fichiers terminée. Validation par checksum non supportée dans ce mode."}
            yield {'checksum_ok': 'n/a'} # Special value for this mode
            return

        # Single-file output mode (default)
        with open(source_path, 'rb') as source_stream, SegdDiskWriter() as disk_writer:
            reader = ReaderClass(source_stream)
            disk_writer.open(destination_path)

            # Manually copy the header first to ensure an identical file
            source_stream.seek(0)
            header_data = source_stream.read(96)
            disk_writer.write_record(header_data)

            record_count = 0
            total_bytes = len(header_data)

            # The reader itself is now the iterator for data records
            for block in reader.read_records():
                disk_writer.write_record(block)
                record_count += 1
                block_size_kb = len(block) / 1024
                total_bytes += len(block)
                listing_entry = {
                    'record_num': record_count,
                    'size_kb': f"{block_size_kb:.2f}",
                }
                yield listing_entry

        print(f"Copy finished. {record_count} records copied ({total_bytes / (1024 * 1024):.2f} MB total).")

        # Step 3: Perform checksum validation
        yield {'status': 'verifying_checksum'}
        print("Performing checksum validation...")

        with open(source_path, 'rb') as source_stream, open(destination_path, 'rb') as dest_stream:
            source_hash = calculate_checksum(source_stream)
            dest_hash = calculate_checksum(dest_stream)

        print(f"Source SHA256: {source_hash}")
        print(f"Destination SHA256: {dest_hash}")

        yield {'checksum_ok': source_hash == dest_hash}

    except FileNotFoundError:
        print(f"Critical error: Input file '{source_path}' not found.")
        yield {'error': f"File not found: {source_path}"}
    except NotImplementedError as e:
        print(f"Unsupported format: {e}")
        yield {'error': str(e)}
    except IOError as e:
        print(f"I/O error: {e}")
        yield {'error': f"I/O error: {e}"}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        yield {'error': f"Unexpected error: {e}"}


if __name__ == '__main__':
    # --- Configuration pour le test ---
    DUMMY_TAPE_PATH = 'dummy_tape.bin'
    OUTPUT_DISK_FILE = 'disk_copy.segd'

    print("--- Controller Test ---")

    # Ensure the output file does not exist for a clean test
    if os.path.exists(OUTPUT_DISK_FILE):
        os.remove(OUTPUT_DISK_FILE)

    if not os.path.exists(DUMMY_TAPE_PATH):
        print(f"\nWARNING: Test file '{DUMMY_TAPE_PATH}' does not exist yet.")
        print("Script cannot run. Will be tested in the next step.")
    else:
        print(f"Reading from source: '{DUMMY_TAPE_PATH}'")
        print(f"Writing to destination: '{OUTPUT_DISK_FILE}'")
        print("-" * 70)
        print("Real-time listing:")

        for entry in transcribe_data(DUMMY_TAPE_PATH, OUTPUT_DISK_FILE):
            if 'error' in entry:
                print(f"  ERROR: {entry['error']}")
            elif 'status' in entry:
                print(f"  STATUS: {entry['status']}")
            elif 'checksum_ok' in entry:
                print(f"  VALIDATION: Checksum OK = {entry['checksum_ok']}")
            elif 'record_num' in entry:
                print(f"  > Copied Record #{entry['record_num']} ({entry['size_kb']} KB)")

        print("-" * 70)

    print("--- Controller Test Finished ---")
