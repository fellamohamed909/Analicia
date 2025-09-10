"""
SEGD Rev 3 File Writer.

This module provides the SegDWriter class, which is responsible for
writing data into a valid SEGD Rev 3 file. It takes structured data
(from definitions.py) and serializes it into the correct binary format.
"""
import struct
from typing import IO
from segd.common.binary_utils import write_bcd
from segd.rev3.definitions import GeneralHeader1, GeneralHeader2, GeneralHeader3

class SegDWriter:
    """
    A writer for SEG-D Rev 3.0 files that operates on a file-like stream.

    The caller is responsible for opening and closing the stream.

    Example:
        with open('path/to/new_file.segd', 'wb') as f:
            writer = SegDWriter(f)
            # gh1 is a GeneralHeader1 object
            writer.write_general_header_1(gh1)
    """

    def __init__(self, stream: IO[bytes]):
        if not hasattr(stream, 'write'):
            raise TypeError("Stream must be a file-like object with a write() method.")
        self.stream = stream

    def write_general_header_1(self, header: GeneralHeader1):
        """Serializes and writes the General Header Block #1."""
        block = bytearray(32)

        block[0:2] = write_bcd(header.file_number, 2)
        block[2:4] = write_bcd(header.format_code, 2)

        constants_bytes = b"".join([write_bcd(c, 1) for c in header.general_constants])
        block[4:10] = constants_bytes

        block[10:11] = write_bcd(header.year, 1)

        dy1 = header.julian_day // 100
        dy23 = header.julian_day % 100
        block[11] = (header.num_additional_blocks << 4) | dy1
        block[12:13] = write_bcd(dy23, 1)

        block[13:14] = write_bcd(header.hour, 1)
        block[14:15] = write_bcd(header.minute, 1)
        block[15:16] = write_bcd(header.second, 1)
        block[16:17] = write_bcd(header.manufacturer_code, 1)
        block[17:19] = write_bcd(header.manufacturer_serial_number, 2)

        block[22] = header.base_scan_interval

        val = header.record_length_in_512ms
        d1 = val // 100
        d2 = (val % 100) // 10
        d3 = val % 10

        block[23] = (header.polarity_code << 4) | d1
        block[24] = (header.record_type << 4) | d2
        block[25] = (d3 << 4)

        block[27:28] = write_bcd(header.scan_types_per_record, 1)
        block[28:29] = write_bcd(header.channel_sets_per_scan_type, 1)
        block[29:30] = write_bcd(header.skew_blocks, 1)
        block[30:31] = write_bcd(header.extended_header_length, 1)
        block[31:32] = write_bcd(header.external_header_length, 1)

        self.stream.write(block)

    def write_general_header_2(self, header: GeneralHeader2):
        """Serializes and writes the General Header Block #2."""
        block = bytearray(32)
        block[0:3] = (header.extended_file_number or 0).to_bytes(3, 'big')
        block[3:5] = struct.pack('>H', header.extended_channel_sets or 0)
        block[5:8] = (header.extended_header_blocks or 0).to_bytes(3, 'big')
        block[8:10] = struct.pack('>H', header.extended_skew_blocks or 0)
        block[10:12] = struct.pack('>BB', header.seg_d_revision_major or 0, header.seg_d_revision_minor or 0)
        block[12:16] = struct.pack('>I', header.general_trailer_blocks or 0)
        block[16:20] = (header.extended_record_length_ms or 0).to_bytes(4, 'big', signed=True)
        block[20:22] = struct.pack('>H', header.record_set_number or 0)
        block[22:24] = struct.pack('>H', header.extended_num_additional_blocks or 0)
        block[24:27] = (header.dominant_sampling_interval_us or 0).to_bytes(3, 'big')
        block[27:30] = (header.external_header_blocks or 0).to_bytes(3, 'big')
        block[31] = 0x02

        self.stream.write(block)

    def write_general_header_3(self, header: GeneralHeader3):
        """Serializes and writes the General Header Block #3."""
        block = bytearray(32)
        block[0:24] = struct.pack('>qQQ', header.time_zero_us, header.record_size_bytes, header.data_size_bytes)
        block[24:28] = struct.pack('>I', header.header_size_bytes)
        block[28] = int(header.extended_recording_mode)
        block[29] = int(header.relative_time_mode)
        block[31] = 0x03

        self.stream.write(block)
