from nbt_convutils.nbt import Region

r = Region(filepath=r"ignore\b\r.-1.0.mca")
r.write_region_file("ignore/")

# from ignore.nbt_ignore.region import Region

# r = Region()
# r.load_region(r"ignore\b\r.-1.0.mca")
# print(r)
# input()
