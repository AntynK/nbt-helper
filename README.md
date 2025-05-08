# NBT helper
This package provides tools for reading and writing Minecraft data files. 

Current version support reading and writing all NBT tag and also reading and writing region files(.mca).

## Features
Module uses BinaryHandle a special class for reading and writing binary data. Because of that, byte order can be easily changed. 

> [!NOTE]
> Java Edition(JE) uses big-endian integers, but Bedrock Edition(BE) uses little-endian integers

