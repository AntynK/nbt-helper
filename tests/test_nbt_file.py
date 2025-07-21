import zlib
import gzip
from pathlib import Path
from io import BytesIO

from nbt_helper.file import NBTFile, FileTypes


FILES_DIRECTORY = Path(__file__).parent.joinpath("data", "files")

FILES = {
    "je_gzip.nbt": FileTypes.JE_GZIP_COMPRESSED,
    "je_uncompressed.nbt": FileTypes.JE_UNCOMPRESSED,
    "je_zlib.nbt": FileTypes.JE_ZLIB_COMPRESSED,
    "pe_uncompressed_with_header.nbt": FileTypes.BE_WITH_HEADER,
    "pe_uncompressed.nbt": FileTypes.BE_UNCOMPRESSED,
}


def compare(buffer: BytesIO, filepath: Path, file_type: FileTypes) -> bool:
    if file_type is FileTypes.JE_GZIP_COMPRESSED:
        return gzip.decompress(buffer.getvalue()) == gzip.decompress(
            filepath.read_bytes()
        )

    if file_type is FileTypes.JE_ZLIB_COMPRESSED:
        return zlib.decompress(buffer.getvalue()) == zlib.decompress(
            filepath.read_bytes()
        )

    return buffer.getvalue() == filepath.read_bytes()


def test_nbt_file() -> None:
    for filename, filetype in FILES.items():
        filepath = FILES_DIRECTORY.joinpath(filename)

        file = NBTFile(filepath=filepath)

        assert filetype is file.get_file_type()

        buffer = BytesIO()
        file.save(buffer=buffer)

        assert compare(buffer, filepath, file.get_file_type()) == True
