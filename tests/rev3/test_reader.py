"""
Tests for the SEGD Rev 3 Reader.
"""
import pytest
import struct
import io
from segd.rev3.reader import SegDReader

@pytest.fixture
def simple_segd_stream():
    """Creates a simple 32-byte SEGD file stream for testing GH1 parsing."""
    content = b'\x00\x01' + b'\x00' * 9 + b'\x20' + b'\x00' * 20
    return io.BytesIO(content)

@pytest.fixture
def full_headers_stream():
    """Creates a 96-byte SEGD file stream with GH1, GH2, and GH3."""
    gh1_content = b'\x00\x01' + b'\x00' * 9 + b'\x20' + b'\x00' * 20
    gh2_content = (
        (12345).to_bytes(3, 'big') +
        struct.pack('>H', 256) +
        (0).to_bytes(3, 'big') +
        struct.pack('>H', 0) +
        struct.pack('>BB', 3, 0) +
        struct.pack('>I', 0) +
        (15000).to_bytes(4, 'big', signed=True) +
        struct.pack('>H', 99) +
        struct.pack('>H', 2) +
        (2000).to_bytes(3, 'big') +
        (0).to_bytes(3, 'big') +
        b'\x00' +
        b'\x02'
    )
    gh3_content = (
        struct.pack('>q', 1234567890) +
        struct.pack('>Q', 96) +
        struct.pack('>Q', 0) +
        struct.pack('>I', 96) +
        b'\x01' +
        b'\x00' +
        b'\x00' +
        b'\x03'
    )
    return io.BytesIO(gh1_content + gh2_content + gh3_content)


@pytest.fixture
def empty_segd_stream():
    """Creates an empty file stream to test error handling."""
    return io.BytesIO(b'')


def test_read_general_header_1_success(simple_segd_stream):
    """
    Tests successful parsing of a valid General Header Block 1.
    """
    reader = SegDReader(simple_segd_stream)
    gh1 = reader.read_general_header_1()
    assert gh1.file_number == 1
    assert gh1.num_additional_blocks == 2

def test_read_all_general_headers(full_headers_stream):
    """Tests reading all three mandatory general headers in sequence."""
    reader = SegDReader(full_headers_stream)

    gh1 = reader.read_general_header_1()
    assert gh1.file_number == 1
    assert gh1.num_additional_blocks == 2

    gh2 = reader.read_general_header_2()
    assert gh2.extended_file_number == 12345
    assert gh2.extended_channel_sets == 256
    assert gh2.seg_d_revision_major == 3
    assert gh2.seg_d_revision_minor == 0
    assert gh2.extended_record_length_ms == 15000
    assert gh2.record_set_number == 99
    assert gh2.extended_num_additional_blocks == 2
    assert gh2.dominant_sampling_interval_us == 2000

    gh3 = reader.read_general_header_3()
    assert gh3.time_zero_us == 1234567890
    assert gh3.record_size_bytes == 96
    assert gh3.data_size_bytes == 0
    assert gh3.header_size_bytes == 96
    assert gh3.extended_recording_mode is True
    assert gh3.relative_time_mode is False


def test_read_general_header_1_file_too_short(empty_segd_stream):
    """
    Tests that reading a file smaller than 32 bytes raises an IOError.
    """
    reader = SegDReader(empty_segd_stream)
    with pytest.raises(IOError, match="Could not read General Header 1"):
        reader.read_general_header_1()

def test_reader_init_with_non_stream():
    """Tests that initializing with a non-stream object raises TypeError."""
    with pytest.raises(TypeError):
        SegDReader("not a stream")
