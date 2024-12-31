import struct
from dataclasses import dataclass
from monster_names import get_names


@dataclass
class MonsterStats:
    exp: int
    gold: int
    HP: int
    morale: int
    unknown1: int  # ai?
    unknown2: int  # evade?
    absorb: int
    hits: int
    unknown5: int  # hit rate?
    dmg: int
    unknown6: int  # crit rate?
    unknown7: int  # ?
    unknown8: int  # attack ailment?
    family_group: int
    unknown10: int  # magic def?
    element_weak: int
    element_resist: int

    def __str__(self):
        return (
            f"  ({self.family_group})\n"
            f"  EXP:{self.exp} \t GLD: {self.gold} \t HP: {self.HP}\n"
            f"  ABS: {self.absorb} \t HIT: {self.hits} \t DMG: {self.dmg}\n"
            f"  WEAK:{self.element_weak}\tRESIST:{self.element_resist}\n"

        )


# Define the struct format for MonsterStats
struct_format = 'HHHBBBBBBBBBBBBBB'


# Function to create an instance of the MonsterStats dataclass from file_bytes starting at a given offset
def create_monster_stats_instance(file_bytes, offset):
    struct_size = struct.calcsize(struct_format)
    struct_data = file_bytes[int(offset):int(offset) + struct_size]
    unpacked_data = struct.unpack(struct_format, struct_data)
    return MonsterStats(*unpacked_data)


# Open the file in binary mode
with open('Final Fantasy (USA).nes', 'rb') as file:
    # Read the entire file as bytes
    file_bytes = file.read()

offset = 0x30530  #TODO: magic number
struct_size = struct.calcsize(struct_format)
names = get_names(file_bytes)

# Loop through all 128 monsters
for x in range(0, 128):
    monster_stats = create_monster_stats_instance(file_bytes, offset+(x*struct_size))
    print(names[x], monster_stats)
