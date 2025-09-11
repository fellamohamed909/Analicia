import struct
import os

FILENAME = "dummy_tape.bin"
BLOCK_SIZE = 32768
NUM_RECORDS = 3
HEADER_SIZE = 96  # 3 General Header blocks

print(f"Generating test file '{FILENAME}'...")

with open(FILENAME, "wb") as f:
    # --- Create a valid SEGD Rev 3.0 Header ---

    # General Header 1 (32 bytes)
    gh1 = bytearray(32)

    # General Header 2 (32 bytes) - with version number
    gh2 = bytearray(32)
    gh2[10] = 3  # Major Revision 3
    gh2[11] = 0  # Minor Revision 0

    # General Header 3 (32 bytes)
    gh3 = bytearray(32)

    f.write(gh1)
    f.write(gh2)
    f.write(gh3)

    # --- Create Data Records ---
    for i in range(NUM_RECORDS):
        # Create a record header (32 bytes) with some dummy info
        record_header = bytearray(32)
        struct.pack_into('>H', record_header, 0, 123 + i) # File number

        # Create a full block with the header and padding
        data_size = BLOCK_SIZE - len(record_header)
        data_padding = b'\x01' * data_size # Use non-zero data
        block = record_header + data_padding

        f.write(block)

total_size = HEADER_SIZE + (NUM_RECORDS * BLOCK_SIZE)
print(f"Test file '{FILENAME}' created with {NUM_RECORDS} records.")
print(f"Total expected size: {total_size} bytes.")
