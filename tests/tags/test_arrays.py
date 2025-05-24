from typing import Type, Any
from io import BytesIO

import pytest

from nbt_helper.tags import (
    BaseTag,
    BinaryHandler,
    ByteOrder,
    TagIntArray,
    TagByteArray,
    TagLongArray,
)


def tag_as_bytes(tag: BaseTag) -> bytes:
    buffer = BytesIO()
    tag.write_to_buffer(buffer)
    return buffer.getvalue()


@pytest.mark.parametrize(
    ["tag_type", "value", "expected_bytes"],
    [
        (
            TagIntArray,
            [2147483647, -2147483648],
            b"\x00\x00\x00\x02\x7f\xff\xff\xff\x80\x00\x00\x00",
        ),
        (
            TagLongArray,
            [9223372036854775807, -9223372036854775808],
            b"\x00\x00\x00\x02\x7f\xff\xff\xff\xff\xff\xff\xff\x80\x00\x00\x00\x00\x00\x00\x00",
        ),
        (
            TagByteArray,
            bytearray((255, 0)),
            b"\x00\x00\x00\x02\xff\x00",
        ),
    ],
)
def test_io(tag_type: Type[BaseTag], value: Any, expected_bytes: bytes) -> None:
    binary_handler = BinaryHandler(ByteOrder.BIG)
    tag = tag_type(binary_handler, value=value)
    new_tag = tag_type(binary_handler, buffer=BytesIO(expected_bytes))

    assert tag_as_bytes(tag) == expected_bytes
    assert tag == new_tag
    assert tag.value == new_tag.value
