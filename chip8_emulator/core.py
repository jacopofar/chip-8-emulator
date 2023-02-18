import array
from time import sleep

from typing_extensions import Protocol

SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32


def byte_to_bits(b: int) -> list[int]:
    """Bits as 0 or 1 integers from most to least significant."""
    return [(b >> (7 - p) & 1) for p in range(8)]


class Display(Protocol):
    def clear(self) -> None:
        ...

    def draw(self, x: int, y: int, sprite_data: bytearray) -> bool:
        ...

    def show(self) -> None:
        ...


class System:
    # bytes in the CHIP-8 RAM
    TOTAL_RAM = 4096
    INITIAL_PC = 512  # TODO should it be another position?

    def __init__(self, display: Display) -> None:
        self.ram = bytearray(System.TOTAL_RAM)
        self.stack = array.array("H")  # unsigned short
        self.pc: int = System.INITIAL_PC
        self.registers = bytearray(16)
        self.index_register: int = 0
        self.display = display

    def load(self, raw_data: bytes) -> None:
        self.ram[System.INITIAL_PC : System.INITIAL_PC + len(raw_data)] = raw_data

    def run(self) -> None:
        while True:
            sleep(0.001)
            self.step()

    def step(self) -> None:
        # step 1: fetch the instruction to execute
        # also increment PC for next instruction, if it's
        # branching it will jump later during execution
        [b1, b2] = self.ram[self.pc : self.pc + 2]
        self.pc += 2
        # step 2: execute the instruction
        # split into 4 nibbles
        n1, n2 = b1 >> 4, b1 & 0x0F
        n3, n4 = b2 >> 4, b2 & 0x0F
        match (n1, n2, n3, n4):
            case (0, 0, 0xE, 0):
                self.display.clear()
            case (1, _, _, _):
                # jump to the 3 nibbles read in order
                self.pc = n2 << 8 | b2
            case (6, _, _, _):
                # set register n2 as b2
                self.registers[n2] = b2
            case (7, _, _, _):
                # add to register
                self.registers[n2] += b2
            case (0xA, _, _, _):
                # set register I with the concatenated nibbles
                self.index_register = n2 << 8 | b2
            case (0xD, vx, vy, n):
                # get actual X and Y
                x = self.registers[vx]
                y = self.registers[vy]
                # set register F to 0, will be set to 1 if there are pixels that were switched off
                self.registers[0xF] = (
                    1
                    if self.display.draw(
                        x,
                        y,
                        self.ram[self.index_register : self.index_register + n],
                    )
                    else 0
                )
                # Extra step: display the display on the terminal
                self.display.show()

            case _:
                raise ValueError(f"Unknown operation {(n1, n2, n3, n4)}")
