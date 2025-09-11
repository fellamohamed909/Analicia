"""
SEGD Format Analyzer.

This module provides functions to analyze a stream of data to determine
if it conforms to a known SEGD (Society of Exploration Geophysicists Data)
format, and to identify its revision number.
"""
from typing import IO, Optional

def analyze_stream(stream: IO[bytes]) -> Optional[str]:
    """
    Analyzes the given stream to detect the SEGD format and version.

    This function reads the necessary header blocks from the stream to
    identify the SEGD revision number. It is designed to be non-intrusive
    and resets the stream's position after reading.

    Args:
        stream: A file-like object opened in binary mode with read() and
                seek() methods.

    Returns:
        A string representing the SEGD revision (e.g., "3.0", "1.0") if
        the format is recognized, otherwise None.
    """
    original_position = stream.tell()
    try:
        # The version information is in the second 32-byte header block.
        stream.seek(32)
        header_block_2 = stream.read(32)

        if len(header_block_2) < 32:
            return None  # File is too short to be a valid SEGD file.

        # According to the SEGD specification, bytes 10 and 11 of the
        # second general header block hold the major and minor revision numbers.
        major_rev = header_block_2[10]
        minor_rev = header_block_2[11]

        # Check for known major revision numbers.
        # SEGD Rev 0 does not have a version number in this location.
        if major_rev in [1, 2, 3]:
            # For Rev 1, the minor number is a binary fraction, but for
            # simplicity, we'll represent it as a decimal.
            # e.g., 1.00 is stored as major=1, minor=0
            return f"{major_rev}.{minor_rev}"
        else:
            # If the major revision is not a known value (e.g., 0),
            # we cannot confirm the format from this field.
            return None

    except (IOError, IndexError):
        # An error during reading or accessing bytes also means we can't
        # determine the version.
        return None
    finally:
        # Ensure the stream is reset to its original position.
        stream.seek(original_position)
