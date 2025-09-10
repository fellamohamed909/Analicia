import pytest
from segd.common.binary_utils import read_bcd, write_bcd

# Test cases for read_bcd
@pytest.mark.parametrize("bcd_bytes, expected_int", [
    (b'\x12\x34', 1234),
    (b'\x01\x02', 102),
    (b'\x00\x05', 5),
    (b'\x99\x99\x99', 999999),
    (b'', 0),
])
def test_read_bcd_valid(bcd_bytes, expected_int):
    """Tests decoding of valid BCD byte strings."""
    assert read_bcd(bcd_bytes) == expected_int

def test_read_bcd_invalid():
    """Tests that an invalid BCD byte raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid BCD byte found: 0x1a"):
        read_bcd(b'\x01\x1a')

# Test cases for write_bcd
@pytest.mark.parametrize("value, length, expected_bytes", [
    (1234, 2, b'\x12\x34'),
    (102, 2, b'\x01\x02'),
    (5, 2, b'\x00\x05'),
    (999999, 3, b'\x99\x99\x99'),
    (0, 1, b'\x00'),
])
def test_write_bcd_valid(value, length, expected_bytes):
    """Tests encoding of integers to BCD byte strings."""
    assert write_bcd(value, length) == expected_bytes

def test_write_bcd_raises_value_too_large():
    """Tests that a value too large for the length raises a ValueError."""
    with pytest.raises(ValueError, match="too large for a BCD of length 2"):
        write_bcd(12345, 2)

def test_write_bcd_raises_negative_value():
    """Tests that a negative value raises a ValueError."""
    with pytest.raises(ValueError, match="BCD value cannot be negative"):
        write_bcd(-1, 1)

# Round-trip tests
@pytest.mark.parametrize("value, length", [
    (123456, 3),
    (987, 2),
    (0, 1),
    (42, 1),
])
def test_bcd_round_trip(value, length):
    """Tests that writing and then reading a value returns the original value."""
    bcd_bytes = write_bcd(value, length)
    assert read_bcd(bcd_bytes) == value
