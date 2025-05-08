from nbt_helper.tags import (
    write_nbt_file,
    BinaryHandler,
    ByteOrder,
    TagCompound,
    TagByte,
    TagString,
)

binary_handler = BinaryHandler(ByteOrder.BIG)
data = TagCompound(
    binary_handler,
    name="Data",
    value=[
        TagByte(binary_handler, name="Just example", value=100),
        TagString(
            binary_handler, name="Name", value="The best world in the world!"
        ),
    ],
)

with open("level_je.dat", "wb") as file:
    write_nbt_file(data, file)
