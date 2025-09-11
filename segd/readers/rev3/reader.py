"""
SEGD Rev 3 File Reader.

This module provides the SegDReader class, which is responsible for
parsing SEGD files. It handles reading headers, trace data, and
interpreting the file structure according to the SEGD Rev 3 standard.
"""
import struct
from typing import Optional, IO

from segd.common.binary_utils import read_bcd
from .definitions import GeneralHeader1, GeneralHeader2, GeneralHeader3

class SegDReader:
    """
    A reader for SEG-D Rev 3.0 files that operates on a file-like stream.

    The caller is responsible for opening and closing the stream.

    Example:
        with open('path/to/file.segd', 'rb') as f:
            reader = SegDReader(f)
            header1 = reader.read_general_header_1()
            print(header1)
    """

    def __init__(self, stream: IO[bytes]):
        if not hasattr(stream, 'read') or not hasattr(stream, 'seek'):
            raise TypeError("Stream must be a file-like object with read() and seek() methods.")
        self.stream = stream

    def _read_block(self, size: int = 32) -> bytes:
        """Reads a block of the given size from the stream."""
        return self.stream.read(size)

    def read_general_header_1(self) -> GeneralHeader1:
        """
        Reads and parses the 32-byte General Header Block #1.
        Assumes the stream is positioned at the beginning of the block.
        """
        self.stream.seek(0)
        block = self._read_block()
        if len(block) < 32:
            raise IOError("Could not read General Header 1: file is too short.")

        # ... (parsing logic remains the same)
        file_number = read_bcd(block[0:2])
        format_code = read_bcd(block[2:4])
        general_constants = [read_bcd(block[i:i+1]) for i in range(4, 10)]
        year = read_bcd(block[10:11])

        dy1 = (block[11] & 0x0F)
        dy23 = read_bcd(block[12:13])
        julian_day = dy1 * 100 + dy23

        hour = read_bcd(block[13:14])
        minute = read_bcd(block[14:15])
        second = read_bcd(block[15:16])
        manufacturer_code = read_bcd(block[16:17])
        manufacturer_serial = read_bcd(block[17:19])

        scan_types_per_record = read_bcd(block[27:28])
        chan_sets_per_scan_type = read_bcd(block[28:29])
        skew_blocks = read_bcd(block[29:30])
        extended_header_len = read_bcd(block[30:31])
        external_header_len = read_bcd(block[31:32])

        num_additional_blocks = (block[11] >> 4) & 0x0F
        polarity_code = (block[23] >> 4) & 0x0F
        record_type = (block[24] >> 4) & 0x0F
        base_scan_interval = block[22]

        d1 = block[23] & 0x0F
        d2 = block[24] & 0x0F
        d3 = (block[25] >> 4) & 0x0F
        record_length_val = d1 * 100 + d2 * 10 + d3

        return GeneralHeader1(
            file_number=file_number, format_code=format_code,
            general_constants=general_constants, year=year,
            num_additional_blocks=num_additional_blocks, julian_day=julian_day,
            hour=hour, minute=minute, second=second,
            manufacturer_code=manufacturer_code, manufacturer_serial_number=manufacturer_serial,
            base_scan_interval=base_scan_interval, polarity_code=polarity_code,
            record_type=record_type, record_length_in_512ms=record_length_val,
            scan_types_per_record=scan_types_per_record,
            channel_sets_per_scan_type=chan_sets_per_scan_type,
            skew_blocks=skew_blocks, extended_header_length=extended_header_len,
            external_header_length=external_header_len
        )

    def read_general_header_2(self) -> GeneralHeader2:
        """Reads and parses the 32-byte General Header Block #2."""
        block = self._read_block()
        if len(block) < 32:
            raise IOError("Could not read General Header 2: file is too short.")

        efn = int.from_bytes(block[0:3], 'big')
        en = struct.unpack('>H', block[3:5])[0]
        ecx = int.from_bytes(block[5:8], 'big')
        esk = struct.unpack('>H', block[8:10])[0]
        rmj, rmn = struct.unpack('>BB', block[10:12])
        gt = struct.unpack('>I', block[12:16])[0]
        erl = int.from_bytes(block[16:20], 'big', signed=True)
        sn = struct.unpack('>H', block[20:22])[0]
        egh = struct.unpack('>H', block[22:24])[0]
        bsi = int.from_bytes(block[24:27], 'big')
        eh = int.from_bytes(block[27:30], 'big')

        return GeneralHeader2(
            extended_file_number=efn, extended_channel_sets=en,
            extended_header_blocks=ecx, extended_skew_blocks=esk,
            seg_d_revision_major=rmj, seg_d_revision_minor=rmn,
            general_trailer_blocks=gt, extended_record_length_ms=erl,
            record_set_number=sn, extended_num_additional_blocks=egh,
            dominant_sampling_interval_us=bsi, external_header_blocks=eh
        )

    def read_general_header_3(self) -> GeneralHeader3:
        """Reads and parses the 32-byte General Header Block #3."""
        block = self._read_block()
        if len(block) < 32:
            raise IOError("Could not read General Header 3: file is too short.")

        tz, rs, ds = struct.unpack('>qQQ', block[0:24])
        hs = struct.unpack('>I', block[24:28])[0]
        erm = bool(block[28])
        rtm = bool(block[29])

        return GeneralHeader3(
            time_zero_us=tz, record_size_bytes=rs,
            data_size_bytes=ds, header_size_bytes=hs,
            extended_recording_mode=erm, relative_time_mode=rtm
        )

    def read_records(self, block_size=32768):
        """
        A generator that reads the data portion of the SEGD file.

        This is a simplified implementation that assumes the data records
        follow immediately after the first 96 bytes of general headers.
        It reads the rest of the stream in fixed-size blocks.

        Args:
            block_size: The size of chunks to read from the stream.

        Yields:
            A block of bytes for each record.
        """
        # Assume headers have been read or skipped. Data starts after GH1, GH2, GH3.
        self.stream.seek(96)
        while chunk := self.stream.read(block_size):
            yield chunk
