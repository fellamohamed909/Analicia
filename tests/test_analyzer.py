import io
import pytest

from segd.analyzer import analyze_stream

def test_analyze_stream_with_rev3_file():
    """Tests that a mock SEGD Rev 3.0 header is correctly identified."""
    # Create a 64-byte mock header. We only care about bytes 42 and 43.
    mock_header = bytearray(64)
    mock_header[42] = 3  # Major revision 3
    mock_header[43] = 0  # Minor revision 0
    stream = io.BytesIO(mock_header)

    version = analyze_stream(stream)
    assert version == "3.0"
    # Check that the stream position is reset
    assert stream.tell() == 0

def test_analyze_stream_with_rev1_file():
    """Tests that a mock SEGD Rev 1.0 header is correctly identified."""
    mock_header = bytearray(64)
    mock_header[42] = 1  # Major revision 1
    mock_header[43] = 0  # Minor revision 0
    stream = io.BytesIO(mock_header)

    version = analyze_stream(stream)
    assert version == "1.0"
    assert stream.tell() == 0

def test_analyze_stream_with_unsupported_version():
    """Tests that an unknown SEGD revision returns None."""
    mock_header = bytearray(64)
    mock_header[42] = 0  # Invalid major revision
    mock_header[43] = 0
    stream = io.BytesIO(mock_header)

    version = analyze_stream(stream)
    assert version is None
    assert stream.tell() == 0

def test_analyze_stream_with_non_segd_file():
    """Tests that a file without a valid version field returns None."""
    mock_header = bytearray(64)
    mock_header[42] = 99 # Some other non-SEGD value
    stream = io.BytesIO(mock_header)

    version = analyze_stream(stream)
    assert version is None
    assert stream.tell() == 0

def test_analyze_stream_with_short_file():
    """Tests that a file too short to contain the version info returns None."""
    short_stream = io.BytesIO(b'\x00' * 32)
    version = analyze_stream(short_stream)
    assert version is None

def test_analyze_stream_with_empty_file():
    """Tests that an empty file returns None."""
    empty_stream = io.BytesIO(b'')
    version = analyze_stream(empty_stream)
    assert version is None

def test_analyze_stream_preserves_position_on_analysis():
    """Ensures the stream position is restored after analysis."""
    mock_header = bytearray(64)
    mock_header[42] = 3
    stream = io.BytesIO(mock_header)

    # Set an initial position
    stream.seek(10)
    analyze_stream(stream)

    # Check that the position is back to where it was
    assert stream.tell() == 10
