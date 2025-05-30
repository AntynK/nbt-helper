# Java Edition specific
## Uncompressed
Just big-endian TagCompound (see [tags](./tag.md) for more info). 

Magic number (hex): 0xa0000

## Gzip compressed
Structure is the same as uncompressed, but it is compressed with gzip.

Magic number (hex): 0x1f8b08

## Zlib compressed
Structure is the same as uncompressed, but it is compressed with zlib.

Magic number (hex): 0x78

# Bedrock Edition specific
## Plain
Just little-endian TagCompound (see [tags](./tag.md) for more info).

Magic number (hex): 0xa0000

## With header
The first 2 bytes of the file are the magic number (little-endian short) and the next 4 bytes are the size of the payload (little-endian unsigned int). After that, the structure is the same as plain.

Magic number (hex): 0x8
