from pathlib import Path
from io import BytesIO

from nbt_helper.region import Region, SECTOR_SIZE

FILES_DIRECTORY = Path(__file__).parent.joinpath("data", "regions")


def skip_region_timetable(data: bytes) -> bytes:
    chunk_location_table = data[:SECTOR_SIZE]
    chunks_data = data[SECTOR_SIZE * 2 - 1 :]
    return chunk_location_table + chunks_data


def compare(filepath_1: Path, filepath_2: Path) -> bool:
    return skip_region_timetable(filepath_2.read_bytes()) == skip_region_timetable(
        filepath_2.read_bytes()
    )


def test_region(tmp_path):
    filename = "r.0.0.mca"
    INPUT = FILES_DIRECTORY
    OUTPUT = tmp_path.joinpath("output")
    OUTPUT.mkdir()
    r = Region(filepath=FILES_DIRECTORY.joinpath(filename))
    r.write_region_file(OUTPUT)

    assert compare(OUTPUT.joinpath(filename), INPUT.joinpath(filename))
