"""
Example script to create a SEGD file.

This script demonstrates how to use the SegDWriter class to build
a SEGD file from scratch by writing the three mandatory general headers.

Usage:
    python examples/create_segd_file.py <output_path.segd>
"""
import sys
from segd.readers.rev3.writer import SegDWriter
from segd.readers.rev3.definitions import GeneralHeader1, GeneralHeader2, GeneralHeader3

def get_sample_headers():
    """Returns a tuple of sample GeneralHeader dataclass instances."""
    gh1 = GeneralHeader1(
        file_number=1,
        format_code=8058,
        general_constants=[0] * 6,
        year=24,
        num_additional_blocks=2,
        julian_day=250,
        hour=12,
        minute=0,
        second=0,
        manufacturer_code=99,
        manufacturer_serial_number=1,
        base_scan_interval=16,  # 1ms
        polarity_code=0,
        record_type=8, # Normal record
        record_length_in_512ms=20, # ~10 seconds
        scan_types_per_record=1,
        channel_sets_per_scan_type=1,
        skew_blocks=0,
        extended_header_length=0,
        external_header_length=0,
    )
    gh2 = GeneralHeader2(
        extended_file_number=1,
        extended_channel_sets=1,
        seg_d_revision_major=3,
        seg_d_revision_minor=0,
        extended_record_length_ms=10240,
        record_set_number=1,
        extended_num_additional_blocks=2,
        dominant_sampling_interval_us=1000,
    )
    gh3 = GeneralHeader3(
        time_zero_us=1725969600000000,  # Approx. Sep 10 2024
        record_size_bytes=96,
        data_size_bytes=0,
        header_size_bytes=96,
        extended_recording_mode=False,
        relative_time_mode=False
    )
    return gh1, gh2, gh3

def main():
    """
    Main function to create and write a simple SEGD file.
    """
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <output_path.segd>")
        sys.exit(1)

    output_path = sys.argv[1]
    gh1, gh2, gh3 = get_sample_headers()

    try:
        with open(output_path, 'wb') as f:
            writer = SegDWriter(stream=f)

            print(f"Writing sample SEGD headers to '{output_path}'...")
            writer.write_general_header_1(gh1)
            writer.write_general_header_2(gh2)
            writer.write_general_header_3(gh3)
            print("Done.")

    except IOError as e:
        print(f"Error writing to file '{output_path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
