from typing import Type
from segd.readers.rev3.reader import SegDReader as SegDReaderRev3

# In the future, other readers would be imported here:
# from segd.readers.rev1.reader import SegDReader as SegDReaderRev1
# from segd.readers.rev2.reader import SegDReader as SegDReaderRev2

def get_reader(version: str) -> Type:
    """
    Factory function to get the appropriate SegD reader class for a given version.

    Args:
        version: The SEGD version string (e.g., "3.0", "1.0").

    Returns:
        The reader class corresponding to the version.

    Raises:
        NotImplementedError: If the reader for the given version is not implemented.
    """
    major_version = version.split('.')[0]

    if major_version == '3':
        return SegDReaderRev3
    # In the future, other versions would be handled here:
    # elif major_version == '1':
    #     return SegDReaderRev1
    # elif major_version == '2':
    #     return SegDReaderRev2
    else:
        raise NotImplementedError(f"No SEGD reader implemented for version {version}")
