"""
Binary I/O utilities for SEGD format.

This module contains low-level functions for handling binary data,
such as reading and writing Binary-Coded Decimals (BCD),
and managing endianness.
"""
import struct


def read_bcd(data: bytes) -> int:
    """
    Decodes an unsigned integer from a BCD (Binary Coded Decimal) byte string.

    Args:
        data: The byte string to decode.

    Returns:
        The decoded integer.

    Raises:
        ValueError: If the byte string contains invalid BCD characters (nibbles > 9).
    """
    value = 0
    for byte in data:
        high_nibble = byte >> 4
        low_nibble = byte & 0x0F
        if high_nibble > 9 or low_nibble > 9:
            raise ValueError(f"Invalid BCD byte found: {byte:#02x}")
        value = value * 100 + high_nibble * 10 + low_nibble
    return value


def write_bcd(value: int, length: int) -> bytes:
    """
    Encodes an integer into a BCD byte string of a specified length.

    Args:
        value: The integer to encode.
        length: The desired length of the output byte string.

    Returns:
        The BCD-encoded byte string.

    Raises:
        ValueError: If the value is negative or too large for the specified length.
    """
    if value < 0:
        raise ValueError("BCD value cannot be negative.")

    s_value = str(value).zfill(length * 2)
    if len(s_value) > length * 2:
        raise ValueError(f"Value {value} is too large for a BCD of length {length}.")

    bcd_bytes = bytearray()
    for i in range(0, len(s_value), 2):
        high_nibble = int(s_value[i])
        low_nibble = int(s_value[i + 1])
        byte = (high_nibble << 4) | low_nibble
        bcd_bytes.append(byte)

    return bytes(bcd_bytes)
