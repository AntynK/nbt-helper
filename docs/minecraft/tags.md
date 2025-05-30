# Basis
Both Java and Bedrock editions use the same format (but with different byte orders). At the top of each NBT file, there is TagCompound (described below).

> [!NOTE]
> Java Edition(JE) tags are big-endian, but Bedrock Edition(BE) tags are little-endian

## Format
### Base tag format 
| 1 byte | 2 bytes | n bytes | Payload |  
|---|---|---|---|
| Tag id | Length of tag's name | Tag name encoded with UTF-8 | Depends on tag |  

### Tags
| Tag ID | Tag type | Payload | Description |  
|---|---|---|---|
| 1 | TagByte | 1 byte | Signed byte. |  
| 2 | TagShort | 2 bytes | Signed short. |  
| 3 | TagInt | 4 bytes | Signed int. |  
| 4 | TagLong | 8 bytes | Signed long. |  
| 5 | TagFloat | 4 bytes | Signed float. |  
| 6 | TagDouble | 8 bytes | Signed double. |  
| 8 | TagString | 2 bytes (string size) + actual string | Stores string encoded with UTF-8. |  
| 9 | TagList | 1 byte (tag ID) + 4 bytes (list size) + payload | List (array) of tags (tag type cannot be changed). TagID must be nonzero, it indicates what type of tag is stored in the list. |  
| 10 | TagCompound | This tag does not store its length, but it must end with 0 (TagEnd) at the end of the payload. | Dict-like structure. Each tag has a name and payload. Can be nested. Section "Base tag format" describes this tag. |  
| 11 | TagIntArray | 4 bytes (length) + array of integers | Array of integers. |
| 12 | TagLongArray | 4 bytes (length) + array of longs | Array of longs. |  
| 13 | TagByteArray | 4 bytes (length) + array of bytes | Array of bytes. |  
