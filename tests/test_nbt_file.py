from pathlib import Path
from hashlib import sha256
from io import BytesIO

import pytest

from nbt_helper.file import NBTFile

FILES_DIRECTORY = Path(__file__).parent / "data"


def compare_hash(buffer: BytesIO, filepath: Path) -> bool:
    with open(filepath, "rb") as file:
        file_hash = sha256(file.read())
    return sha256(buffer.getvalue()).hexdigest() == file_hash.hexdigest()


def test_nbt_file() -> None:
    for filepath in FILES_DIRECTORY.iterdir():
        file = NBTFile(filepath=filepath)
        buffer = BytesIO()
        file.save(buffer)

        assert compare_hash(buffer, filepath) == True
