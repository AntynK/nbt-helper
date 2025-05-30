# Region
The region file stores the world in chunks, there are 1024 chunks in a fully loaded region file. 

> [!IMPORTANT]
> Each region file must have the same name pattern: "r.x.z.mca", where x and z are integers that can be negative.

At the beginning of the region file, there are 2 tables, each one has 1024 integers (in total occupying 4096 bytes, this is called a `sector`).

> [!NOTE]
> Term `sector` often used, and refers to 4096 bytes.


The first table describes where the chunk is stored in the file (the location table). The second stores the timestamps when the chunk was last updated (the timestamp table).

## Location table
There are 1024 entries in this table. Each entry stores the chunk relative offset (the first 3 bytes) and chunk size (1 byte). 

The relative offset must be multiplied by 4096 bytes (the `sector`), as a result, this will give an absolute offset from the beginning of the file.

The chunk size indicates how many `sectors` the chunk occupies. If the chunk occupies less than the `sector`, it must be padded with zeros at the end.

Relative chunk position can be calculated from entry index with the help of this formula: 
``` Python
z = index // 32
x = index % 32
# Other way
index = x + z * 32

# Bitwise
z = index >> 5
x = index & 31
# Other way
index = x + (z << 5)
``` 

## Chunk
Part of the Minecraft world is 16×384×16 blocks, but the Nether, the End and older versions of the game are 16×256×16 blocks. Detailed information about chunk format: https://minecraft.wiki/w/Chunk_format 

| 4 bytes (unsigned integer) | 1 byte (unsigned byte) | n bytes (payload) |
|---|---|---|
| The length of the chunk. | Compression type. There are 3 types: 0. Uncompressed; 1. Gzip compressed; 2. Zlib compressed. | Actual chunk data (TagCoumpound at the root of the chunk) |

