"""
SEGD Rev 3 Data Structures.

This module defines the data structures for SEGD headers and trace data
using Python's dataclasses. Each class maps to a specific block or
header in the SEGD standard, making the code clean and readable.

The fields are defined based on the SEG-D Rev 3.0 standard. The parsing
of the raw byte blocks into these dataclasses is handled by the Reader.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class GeneralHeader1:
    """
    Corresponds to General Header Block #1 (Bytes 1-32).
    This block is mandatory.
    """
    file_number: int
    format_code: int
    general_constants: list[int]
    year: int
    num_additional_blocks: int
    julian_day: int
    hour: int
    minute: int
    second: int
    manufacturer_code: int
    manufacturer_serial_number: int
    base_scan_interval: int
    polarity_code: int
    record_type: int
    record_length_in_512ms: int
    scan_types_per_record: int
    channel_sets_per_scan_type: int
    skew_blocks: int
    extended_header_length: int
    external_header_length: int

@dataclass
class GeneralHeader2:
    """
    Corresponds to General Header Block #2.
    This block is mandatory.
    """
    extended_file_number: Optional[int] = None
    extended_channel_sets: Optional[int] = None
    extended_header_blocks: Optional[int] = None
    extended_skew_blocks: Optional[int] = None
    seg_d_revision_major: Optional[int] = None
    seg_d_revision_minor: Optional[int] = None
    general_trailer_blocks: Optional[int] = None
    extended_record_length_ms: Optional[int] = None
    record_set_number: Optional[int] = None
    extended_num_additional_blocks: Optional[int] = None
    dominant_sampling_interval_us: Optional[int] = None
    external_header_blocks: Optional[int] = None

@dataclass
class GeneralHeader3:
    """
    Corresponds to General Header Block #3 (Timestamp and size header).
    This block is mandatory for Rev 3.0.
    """
    time_zero_us: int  # 8-byte SEG-D timestamp (microseconds since GPS epoch)
    record_size_bytes: int
    data_size_bytes: int
    header_size_bytes: int
    extended_recording_mode: bool
    relative_time_mode: bool
