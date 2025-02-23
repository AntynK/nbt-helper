from nbt_convutils.nbt.loaders import BigEndianLoader
from typing import Any, BinaryIO, Sequence, Type

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12


class BaseTag:
    def __init__(
        self,
        loader: Type[BigEndianLoader],
        name: str = "",
        value: Any = None,
        buffer: BinaryIO | None = None,
    ) -> None:
        self.loader = loader
        self.name = name
        self.value = value
        if buffer:
            self.load_from_buffer(buffer)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        pass
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}): {self.value}"


class TagByte(BaseTag):
    TAG_ID = TAG_BYTE

    def __init__(
        self,
        loader: Type[BigEndianLoader],
        name: str = "",
        value: int = 0,
        buffer: BinaryIO | None = None,
    ) -> None:
        super().__init__(loader, name, value, buffer)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.value = self.loader.read_byte(buffer)


class TagShort(BaseTag):
    TAG_ID = TAG_SHORT

    def __init__(
        self,
        loader: Type[BigEndianLoader],
        name: str = "",
        value: int = 0,
        buffer: BinaryIO | None = None,
    ) -> None:
        super().__init__(loader, name, value, buffer)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.value = self.loader.read_short(buffer)


class TagInt(BaseTag):
    TAD_ID = TAG_INT

    def __init__(
        self,
        loader: Type[BigEndianLoader],
        name: str = "",
        value: int = 0,
        buffer: BinaryIO | None = None,
    ) -> None:
        super().__init__(loader, name, value, buffer)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.value = self.loader.read_int(buffer)


class TagLong(BaseTag):
    TAG_ID = TAG_LONG

    def __init__(
        self,
        loader: Type[BigEndianLoader],
        name: str = "",
        value: int = 0,
        buffer: BinaryIO | None = None,
    ) -> None:
        super().__init__(loader, name, value, buffer)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.value = self.loader.read_long(buffer)


class TagFloat(BaseTag):
    TAG_ID = TAG_FLOAT

    def __init__(
        self,
        loader: Type[BigEndianLoader],
        name: str = "",
        value: float = 0,
        buffer: BinaryIO | None = None,
    ) -> None:
        super().__init__(loader, name, value, buffer)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.value = self.loader.read_float(buffer)


class TagDouble(BaseTag):
    TAD_ID = TAG_DOUBLE

    def __init__(
        self,
        loader: Type[BigEndianLoader],
        name: str = "",
        value: float = 0,
        buffer: BinaryIO | None = None,
    ) -> None:
        super().__init__(loader, name, value, buffer)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.value = self.loader.read_double(buffer)


class TagString(BaseTag):
    TAG_ID = TAG_STRING

    def __init__(
        self,
        loader: Type[BigEndianLoader],
        name: str = "",
        value: str = "",
        buffer: BinaryIO | None = None,
    ) -> None:
        super().__init__(loader, name, value, buffer)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        length = self.loader.read_short(buffer)
        data = buffer.read(length)
        if len(data) != length:
            raise ValueError(f"String length not equal: {length=}, {data=}.")
        self.value = data.decode("utf-8")


class TagList(BaseTag):
    TAG_ID = TAG_LIST

    def __init__(
        self,
        loader: Type[BigEndianLoader],
        name: str = "",
        value: Sequence | None = None,
        buffer: BinaryIO | None = None,
        tag_id: int = TAG_END,
    ) -> None:
        super().__init__(loader, name, [], buffer)
        self.tag_id = tag_id
        if value:
            self.value.extend(value)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        self.tag_id = self.loader.read_byte(buffer)
        length = self.loader.read_int(buffer)
        self.value = [
            TAGS_LIST[self.tag_id](self.loader, buffer=buffer) for _ in range(length)
        ]


class TagCompound(BaseTag):
    TAG_ID = TAG_COMPOUND

    def __init__(
        self,
        loader: Type[BigEndianLoader],
        name: str = "",
        value: Sequence | None = None,
        buffer: BinaryIO | None = None,
    ) -> None:
        super().__init__(loader, name, [], buffer)
        if value:
            self.value.extend(value)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        while True:
            tag_type = self.loader.read_byte(buffer)
            if tag_type == TAG_END:
                break
            name = TagString(self.loader, buffer=buffer).value
            tag = TAGS_LIST[tag_type](self.loader, name=name, buffer=buffer)
            self.value.append(tag)


class TagIntArray(BaseTag):
    TAG_ID = TAG_INT_ARRAY

    def __init__(
        self,
        loader: Type[BigEndianLoader],
        name: str = "",
        value: Sequence | None = None,
        buffer: BinaryIO | None = None,
    ) -> None:
        super().__init__(loader, name, [], buffer)
        if value:
            self.value.extend(value)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        length = self.loader.read_int(buffer)
        self.value = list(self.loader.read_int_array(buffer, length))


class TagLongArray(BaseTag):
    TAG_ID = TAG_LONG_ARRAY

    def __init__(
        self,
        loader: Type[BigEndianLoader],
        name: str = "",
        value: Sequence | None = None,
        buffer: BinaryIO | None = None,
    ) -> None:
        super().__init__(loader, name, [], buffer)
        if value:
            self.value.extend(value)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        length = self.loader.read_int(buffer)
        self.value = list(self.loader.read_long_array(buffer, length))


class TagByteArray(BaseTag):
    TAG_ID = TAG_BYTE_ARRAY

    def __init__(
        self,
        loader: Type[BigEndianLoader],
        name: str = "",
        value: bytearray | None = None,
        buffer: BinaryIO | None = None,
    ) -> None:
        super().__init__(loader, name, value or bytearray(), buffer)

    def load_from_buffer(self, buffer: BinaryIO) -> None:
        length = self.loader.read_int(buffer)
        self.value = bytearray(buffer.read(length))


TAGS_LIST = {
    TAG_BYTE: TagByte,
    TAG_SHORT: TagShort,
    TAG_INT: TagInt,
    TAG_LONG: TagLong,
    TAG_FLOAT: TagFloat,
    TAG_DOUBLE: TagDouble,
    TAG_STRING: TagString,
    TAG_LIST: TagList,
    TAG_COMPOUND: TagCompound,
    TAG_INT_ARRAY: TagIntArray,
    TAG_LONG_ARRAY: TagLongArray,
    TAG_BYTE_ARRAY: TagByteArray,
}
