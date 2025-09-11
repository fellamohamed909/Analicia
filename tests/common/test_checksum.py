import io
import pytest

from segd.common.checksum import calculate_checksum

def test_calculate_checksum_sha256():
    """Tests SHA-256 checksum calculation with known data."""
    data = b'hello world'
    expected_hash = 'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
    stream = io.BytesIO(data)

    actual_hash = calculate_checksum(stream, algorithm='sha256')

    assert actual_hash == expected_hash

def test_calculate_checksum_md5():
    """Tests MD5 checksum calculation to verify algorithm parameter."""
    data = b'hello world'
    expected_hash = '5eb63bbbe01eeed093cb22bb8f5acdc3'
    stream = io.BytesIO(data)

    actual_hash = calculate_checksum(stream, algorithm='md5')

    assert actual_hash == expected_hash

def test_calculate_checksum_empty_stream():
    """Tests that an empty stream produces a known empty hash."""
    data = b''
    # SHA-256 hash of an empty string
    expected_hash = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    stream = io.BytesIO(data)

    actual_hash = calculate_checksum(stream)

    assert actual_hash == expected_hash

def test_calculate_checksum_preserves_position():
    """Ensures the stream position is restored after calculation."""
    data = b'some data to test position'
    stream = io.BytesIO(data)

    # Set an initial position
    stream.seek(5)
    calculate_checksum(stream)

    # Check that the position is back to where it was
    assert stream.tell() == 5

def test_calculate_checksum_large_data():
    """Tests checksum on data larger than the chunk size."""
    # Create data larger than 4K chunk size
    data = b'A' * 5000
    stream = io.BytesIO(data)

    # We don't need to check the exact hash, just that it runs without error
    # and produces a hash of the correct length (64 chars for SHA-256).
    actual_hash = calculate_checksum(stream)

    assert isinstance(actual_hash, str)
    assert len(actual_hash) == 64
