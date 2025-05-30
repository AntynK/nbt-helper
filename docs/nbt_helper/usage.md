# Tags
The `BinaryHandler` must be provided to each tag. Byte order can be changed with the `change_byte_order` method, this will not affect the data that the tag is storing.

# Region
To load region file use the `nbt_helper.region.Region` class. Region file name must have pattern as described in [region.md](../minecraft/region.md) file.

# Files
To interact with Minecraft data files, it is recommended to use the `nbt_helper.file.NBTFile` class, as it can automatically detect file type. Also, you can use other classes directly to read/write specific data formats.

> [!NOTE]
> If you try to save big-endian tags using one of the Bedrock Edition file types, it will automatically change to little-endian and vice versa.