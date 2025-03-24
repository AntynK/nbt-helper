import os
import gzip
import zlib
from enum import Enum
from io import BytesIO
from typing import Optional, Union, BinaryIO

from nbt_convutils.nbt.tags import BinaryHandler, ByteOrder, TagCompound, read_nbt_file

SECTOR_SIZE = 4096
INT_SIZE = 4


class CompressionTypes(Enum):
    UNCOMPRESSED = 0
    GZIP_COMPRESSED = 1
    ZLIB_COMPRESSED = 2


def cords_from_filepath(filepath: str) -> tuple[int, int]:
    filepath = os.path.basename(filepath)
    filepath = filepath.replace("r.", "").replace(".mca", "")
    x, z = map(int, filepath.split("."))
    return x, z


def cords_from_location(location: int) -> tuple[int, int]:
    z, x = divmod(location, 32)
    return x, z


def location_from_cords(x: int, z: int) -> int:
    return x + z * 32


class Chunk:
    def __init__(
        self,
        x: int,
        z: int,
        compression: int,
        data: TagCompound,
        timestamp: int,
    ) -> None:
        self.x, self.z = x, z
        self.data = data
        self.timestamp = timestamp
        self.compression = compression

    def __repr__(self) -> str:
        return f"Chunk(x={self.x}, z={self.z}, compression={self.compression}, timestamp={self.timestamp}, data={self.data})"


class Region:
    def __init__(self, filepath: Optional[str] = None) -> None:
        self._binary_handler = BinaryHandler(ByteOrder.BIG)
        self.chunks: list[Chunk] = []
        if filepath:
            self.load_region_file(filepath)

    def load_region_file(self, filepath: str) -> None:
        if not filepath.endswith(".mca"):
            raise ValueError("Wrong file type")

        file_size = os.path.getsize(filepath)
        if file_size < SECTOR_SIZE * 2:
            raise ValueError(f"File '{filepath}' is too small.")

        self.x, self.z = cords_from_filepath(filepath)

        with open(filepath, "rb") as file:
            for index in range(SECTOR_SIZE // INT_SIZE):
                chunk = self._load_chunk(index, file)
                if chunk:
                    self.chunks.append(chunk)

    def _load_chunk(self, index: int, file: BinaryIO) -> Chunk | None:
        x, z = cords_from_location(index)
        file.seek(index * INT_SIZE)
        location = self._binary_handler.read_int(file, signed=False)
        if location == 0:
            return

        offset = location >> 8

        file.seek(offset * SECTOR_SIZE)
        length = self._binary_handler.read_int(file, signed=False)
        compression = self._binary_handler.read_byte(file, signed=False)
        chunk_data = self._decompress_chunk(file.read(length), compression)
        data = read_nbt_file(chunk_data)

        file.seek(index * INT_SIZE + SECTOR_SIZE)
        timestamp = self._binary_handler.read_int(file, signed=False)
        return Chunk(x, z, compression, data, timestamp)

    def _decompress_chunk(self, chunk_data: bytes, compression: int) -> BytesIO:
        if compression not in CompressionTypes:
            raise ValueError(f"Undefined compression type {compression}")

        compression_type = CompressionTypes(compression)
        if compression_type == CompressionTypes.GZIP_COMPRESSED:
            data = gzip.decompress(chunk_data)
        elif compression_type == CompressionTypes.ZLIB_COMPRESSED:
            data = zlib.decompress(chunk_data)
        elif compression_type == CompressionTypes.UNCOMPRESSED:
            data = chunk_data

        return BytesIO(data)  # type: ignore

    def __repr__(self) -> str:
        return f"Region(x={self.x}, z={self.z}): [{len(self.chunks)} chunks]"
