import struct
from dataclasses import dataclass
from monster_names import get_names
from item_names import decode_bits, ELEMENTS, FAMILIES


@dataclass
class MonsterStats:
    # Field meanings from the FF1 disassembly (some formats.txt, "Enemy data").
    # Several fields are stored "raw"; the game (and gamercorner guide) display
    # derived values - see the display_* properties below.
    exp: int
    gold: int
    HP: int
    morale: int      # raw; run level = (morale - 80) // 2, min 0 (see display_run_level)
    ai: int          # AI script index (0xff = none); see print_ai.py
    agility: int     # raw evade; displayed as agility // 2
    defense: int     # damage absorbed
    hits: int        # number of attacks
    hit_rate: int    # raw; displayed hit % = 84 + hit_rate // 2
    strength: int    # attack power (damage per hit)
    crit_rate: int
    attack_element: int  # byte E: element of the monster's attack (bitfield, see
                         # ELEMENTS) used vs. the target's resist when its attack
                         # inflicts a status. Non-zero iff `ailment` is set.
    ailment: int     # attack-inflicted status ailment
    family_group: int
    mag_def: int     # raw; displayed as mag_def // 2
    element_weak: int
    element_resist: int

    # Display conversions matching the game / gamercorner guide
    @property
    def display_hit(self):
        return 84 + self.hit_rate // 2

    @property
    def display_evade(self):
        return self.agility // 2

    @property
    def display_mag_def(self):
        return self.mag_def // 2

    @property
    def display_run_level(self):
        return max(0, (self.morale - 80) // 2)

    def __str__(self):
        ai = f"ai{self.ai}" if self.ai != 0xff else "no AI"
        atk_elem = decode_bits(self.attack_element, ELEMENTS)
        return (
            f"  family: {decode_bits(self.family_group, FAMILIES)}\t{ai}\n"
            f"  EXP:{self.exp} \t GLD: {self.gold} \t HP: {self.HP}\n"
            f"  DEF: {self.defense} \t HITS: {self.hits} \t DMG: {self.strength}"
            f" \t HIT%: {self.display_hit} \t CRIT: {self.crit_rate}\n"
            f"  EVA: {self.display_evade} \t MDEF: {self.display_mag_def}"
            f" \t RUN.LV: {self.display_run_level}\n"
            f"  ATK-ELEM: {atk_elem} \t AILMENT: 0x{self.ailment:02x}\n"
            f"  WEAK: {decode_bits(self.element_weak, ELEMENTS)}"
            f"\tRESIST: {decode_bits(self.element_resist, ELEMENTS)}\n"

        )


# Define the struct format for MonsterStats
struct_format = 'HHHBBBBBBBBBBBBBB'


# Function to create an instance of the MonsterStats dataclass from file_bytes starting at a given offset
def create_monster_stats_instance(file_bytes, offset):
    struct_size = struct.calcsize(struct_format)
    struct_data = file_bytes[int(offset):int(offset) + struct_size]
    unpacked_data = struct.unpack(struct_format, struct_data)
    return MonsterStats(*unpacked_data)


import sys

def main():
    rom_filename = sys.argv[1] if len(sys.argv) > 1 else 'Final Fantasy (USA).nes'
    
    try:
        # Open the file in binary mode
        with open(rom_filename, 'rb') as file:
            # Read the entire file as bytes
            file_bytes = file.read()
        
        offset = 0x30530  #TODO: magic number
        struct_size = struct.calcsize(struct_format)
        names = get_names(file_bytes)
        
        # Loop through all 128 monsters
        for x in range(0, 128):
            monster_stats = create_monster_stats_instance(file_bytes, offset+(x*struct_size))
            print(names[x], monster_stats)
    except FileNotFoundError:
        print(f"Error: ROM file '{rom_filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading ROM file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
