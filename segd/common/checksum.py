import hashlib
from typing import IO

def calculate_checksum(stream: IO[bytes], algorithm: str = 'sha256') -> str:
    """
    Calculates the checksum of a binary stream using the specified algorithm.

    Reads the stream in chunks to be memory-efficient. The stream position
    is reset to its original location after reading.

    Args:
        stream: A file-like object opened in binary mode with read() and
                seek() methods.
        algorithm: The hashing algorithm to use (e.g., 'sha256', 'md5').
                   Defaults to 'sha256'.

    Returns:
        A hexadecimal string representing the calculated hash.
    """
    original_position = stream.tell()
    stream.seek(0)

    hash_obj = hashlib.new(algorithm)

    # Read in 4K chunks
    chunk_size = 4096
    while chunk := stream.read(chunk_size):
        hash_obj.update(chunk)

    # Reset stream position to where it was
    stream.seek(original_position)

    return hash_obj.hexdigest()
