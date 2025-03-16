from nbt_convutils.nbt import BinaryHandler, ByteOrder, TagCompound

binary_handler = BinaryHandler(ByteOrder.BIG)

with open("ignore/hotbar.nbt", "rb") as file:
    file.read(3)  # Bedrock header 11, Java 3
    data = TagCompound(binary_handler, buffer=file)

with open("ignore/hotbar_be.nbt", "wb") as file:
    TagCompound(binary_handler, value=[data]).write_to_buffer(file)
