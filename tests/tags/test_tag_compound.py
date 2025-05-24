from io import BytesIO

import pytest

from nbt_helper.tags import BinaryHandler, ByteOrder, BaseTag, TagCompound, TagByte


def tag_as_bytes(tag: BaseTag) -> bytes:
    buffer = BytesIO()
    tag.write_to_buffer(buffer)
    return buffer.getvalue()


@pytest.mark.parametrize(
    ["tag", "expected_bytes"],
    [
        (
            TagCompound(
                BinaryHandler(ByteOrder.BIG),
                value=[TagByte(BinaryHandler(ByteOrder.BIG), name="Data", value=10)],
            ),
            b"\x01\x00\x04Data\n\x00",
        ),
        (
            TagCompound(
                BinaryHandler(ByteOrder.BIG),
                value=[
                    TagCompound(
                        BinaryHandler(ByteOrder.BIG),
                        name="Inner",
                        value=[
                            TagByte(
                                BinaryHandler(ByteOrder.BIG), name="InnerData", value=10
                            )
                        ],
                    ),
                    TagByte(BinaryHandler(ByteOrder.BIG), name="Data", value=10),
                ],
            ),
            b"\n\x00\x05Inner\x01\x00\x09InnerData\n\x00\x01\x00\x04Data\n\x00",
        ),
    ],
)
def test_io(tag: TagCompound, expected_bytes: bytes) -> None:
    assert tag_as_bytes(tag) == expected_bytes
    new_tag = TagCompound(BinaryHandler(ByteOrder.BIG), buffer=BytesIO(expected_bytes))
    assert tag == new_tag
    assert tag.value == new_tag.value
