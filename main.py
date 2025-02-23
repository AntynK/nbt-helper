from nbt_convutils.nbt.tags import TagCompound
from nbt_convutils.nbt.loaders import BigEndianLoader, LittleEndianLoader


with open("hotbar.nbt", "rb") as file:
    file.read(3) # Bedrock header 11, Java 3
    print(TagCompound(BigEndianLoader, buffer=file))
