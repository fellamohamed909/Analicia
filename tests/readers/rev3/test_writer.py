"""
Tests for the SEGD Rev 3 Writer.

This will include tests for serializing data and a "round-trip" test
where we read a file, write it back, and check for consistency.
"""
import pytest
import io
from segd.readers.rev3.reader import SegDReader
from segd.readers.rev3.writer import SegDWriter
from segd.readers.rev3.definitions import GeneralHeader1, GeneralHeader2, GeneralHeader3

@pytest.fixture
def sample_gh_data():
    """Provides sample GeneralHeader dataclass instances for testing."""
    gh1 = GeneralHeader1(
        file_number=123,
        format_code=8058,
        general_constants=[1, 2, 3, 4, 5, 6],
        year=9,
        num_additional_blocks=2,
        julian_day=150,
        hour=10,
        minute=30,
        second=59,
        manufacturer_code=18,
        manufacturer_serial_number=1234,
        base_scan_interval=32,
        polarity_code=5,
        record_type=8,
        record_length_in_512ms=789,
        scan_types_per_record=1,
        channel_sets_per_scan_type=2,
        skew_blocks=0,
        extended_header_length=0,
        external_header_length=0,
    )
    gh2 = GeneralHeader2(
        extended_file_number=123,
        extended_channel_sets=2,
        extended_header_blocks=0,
        extended_skew_blocks=0,
        seg_d_revision_major=3,
        seg_d_revision_minor=0,
        general_trailer_blocks=0,
        extended_record_length_ms=15000,
        record_set_number=99,
        extended_num_additional_blocks=2,
        dominant_sampling_interval_us=2000,
        external_header_blocks=0
    )
    gh3 = GeneralHeader3(
        time_zero_us=1234567890123,
        record_size_bytes=96,
        data_size_bytes=0,
        header_size_bytes=96,
        extended_recording_mode=True,
        relative_time_mode=False
    )
    return gh1, gh2, gh3


def test_general_headers_round_trip(sample_gh_data):
    """
    Tests that writing and then reading the general headers results in the same data.
    """
    gh1_orig, gh2_orig, gh3_orig = sample_gh_data

    stream = io.BytesIO()

    # Write the headers
    writer = SegDWriter(stream)
    writer.write_general_header_1(gh1_orig)
    writer.write_general_header_2(gh2_orig)
    writer.write_general_header_3(gh3_orig)

    # Rewind the stream and read them back
    stream.seek(0)
    reader = SegDReader(stream)
    gh1_read = reader.read_general_header_1()
    gh2_read = reader.read_general_header_2()
    gh3_read = reader.read_general_header_3()

    # Assert they are identical
    assert gh1_read == gh1_orig
    assert gh2_read == gh2_orig
    assert gh3_read == gh3_orig
