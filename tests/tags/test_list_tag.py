from io import BytesIO

import pytest

from nbt_helper.tags import (
    ByteOrder,
    BinaryHandler,
    TagByte,
    TagList,
    BaseTag,
    TAG_LIST,
    TAG_BYTE,
    TAG_END,
)


def tag_as_bytes(tag: BaseTag) -> bytes:
    buffer = BytesIO()
    tag.write_to_buffer(buffer)
    return buffer.getvalue()


@pytest.mark.parametrize(
    ["tag", "tag_id", "expected_bytes"],
    [
        (TagList(BinaryHandler(ByteOrder.BIG)), TAG_END, b"\x00\x00\x00\x00\x00"),
        (
            TagList(BinaryHandler(ByteOrder.BIG), tag_id=TAG_BYTE),
            TAG_BYTE,
            b"\x01\x00\x00\x00\x00",
        ),
        (
            TagList(
                BinaryHandler(ByteOrder.BIG),
                value=[TagByte(BinaryHandler(ByteOrder.BIG))],
            ),
            TAG_BYTE,
            b"\x01\x00\x00\x00\x01\x00",
        ),
        (
            TagList(
                BinaryHandler(ByteOrder.BIG),
                value=[
                    TagList(
                        BinaryHandler(ByteOrder.BIG),
                        value=[TagByte(BinaryHandler(ByteOrder.BIG))],
                    )
                ],
            ),
            TAG_LIST,
            b"\t\x00\x00\x00\x01\x01\x00\x00\x00\x01\x00",
        ),
    ],
)
def test_io(tag: TagList, tag_id: int, expected_bytes: bytes) -> None:
    assert tag_as_bytes(tag) == expected_bytes
    assert tag.tag_id == tag_id

    buffer = BytesIO(expected_bytes)
    new_tag = TagList(BinaryHandler(ByteOrder.BIG), buffer=buffer)
    assert tag == new_tag
    assert tag.tag_id == new_tag.tag_id


def test_special_case() -> None:
    handler = BinaryHandler(ByteOrder.BIG)
    tag = TagList(handler)
    assert tag.tag_id == TAG_END
    tag.append(TagByte(handler))
    assert tag_as_bytes(tag) == b"\x01\x00\x00\x00\x01\x00"
    assert tag.tag_id == TAG_BYTE
