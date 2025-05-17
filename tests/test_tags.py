from io import BytesIO
from typing import Type, Union

import pytest

from nbt_helper.tags import (
    BaseTag,
    ByteOrder,
    BinaryHandler,
    TagByte,
    TagShort,
    TagInt,
    TagLong,
    TagFloat,
    TagDouble,
    TagString,
)


def get_bytes(tag_cls: Type[BaseTag], byte_roder: ByteOrder, value) -> bytes:
    tag = tag_cls(BinaryHandler(byte_roder), value=value)
    buffer = BytesIO()
    tag.write_to_buffer(buffer)
    return buffer.getvalue()


@pytest.mark.parametrize(
    ["tag_cls", "value", "expected_value"],
    [
        (TagByte, 127, b"\x7f"),
        (TagByte, -128, b"\x80"),
        (TagShort, 32767, b"\x7f\xff"),
        (TagShort, -32768, b"\x80\x00"),
        (TagInt, 2147483647, b"\x7f\xff\xff\xff"),
        (TagInt, -2147483648, b"\x80\x00\x00\x00"),
        (TagLong, 9223372036854775807, b"\x7f\xff\xff\xff\xff\xff\xff\xff"),
        (TagLong, -9223372036854775808, b"\x80\x00\x00\x00\x00\x00\x00\x00"),
        (TagFloat, 3.1456122398376465, b"@IQ\xb6"),
        (TagFloat, -3.1456122398376465, b"\xc0IQ\xb6"),
        (TagDouble, 3.1456122398376465, b"@\t*6\xc0\x00\x00\x00"),
        (TagDouble, -3.1456122398376465, b"\xc0\t*6\xc0\x00\x00\x00"),
    ],
)
def test_number_tags(
    tag_cls: Type[BaseTag],
    value: Union[int, float],
    expected_value: bytes,
) -> None:
    big_endian_bytes = get_bytes(tag_cls, ByteOrder.BIG, value)
    little_endian_bytes = get_bytes(tag_cls, ByteOrder.LITTLE, value)
    assert big_endian_bytes == expected_value
    assert little_endian_bytes == expected_value[::-1]

    big_endian_tag = tag_cls(
        BinaryHandler(ByteOrder.BIG), buffer=BytesIO(big_endian_bytes)
    )
    little_endian_tag = tag_cls(
        BinaryHandler(ByteOrder.LITTLE),
        buffer=BytesIO(little_endian_bytes),
    )

    assert big_endian_tag.value == value
    assert little_endian_tag.value == value


def test_string_tag():
    value = "Hello 🌍!"
    big_endian_bytes = get_bytes(TagString, ByteOrder.BIG, value)
    little_endian_bytes = get_bytes(TagString, ByteOrder.LITTLE, value)

    assert big_endian_bytes == b"\x00\x0bHello \xf0\x9f\x8c\x8d!"
    assert little_endian_bytes == b"\x0b\x00Hello \xf0\x9f\x8c\x8d!"

    big_endian_tag = TagString(
        BinaryHandler(ByteOrder.BIG), buffer=BytesIO(big_endian_bytes)
    )
    little_endian_tag = TagString(
        BinaryHandler(ByteOrder.LITTLE), buffer=BytesIO(little_endian_bytes)
    )
    assert big_endian_tag.value == value
    assert little_endian_tag.value == value

    with pytest.raises(ValueError):
        TagString(BinaryHandler(ByteOrder.BIG), buffer=BytesIO(little_endian_bytes))

    with pytest.raises(ValueError):
        TagString(BinaryHandler(ByteOrder.BIG), buffer=BytesIO(b"\x00\x0cHello"))
