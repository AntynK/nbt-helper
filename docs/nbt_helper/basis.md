# Basis
The main point of this package is to make switching between byte orders an easy task. To do so, the package uses the special class `BinaryHandler` and the enum `ByteOrder`.

The `BinaryHandler` is responsible for reading and writing from the buffer. Byte order can be specified during creation (defaults to `ByteOrder.BIG`) or can be changed by the `change_byte_order` method.

Example:
``` Python
from io import BytesIO
from nbt_helper.tags import BinaryHandler, ByteOrder

buffer = BytesIO()

handler = BinaryHandler(ByteOrder.BIG)
handler.write_int(buffer, 12) # Big-endian: b'\x00\x00\x00\x0c'

buffer.seek(0)
handler.change_byte_order(ByteOrder.LITTLE)
result = handler.read_int(buffer) # 201326592
```
