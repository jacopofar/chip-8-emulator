import array
from time import sleep, time
from random import randint
from typing_extensions import Protocol

SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32

FONT_DATA = [
    0xF0,
    0x90,
    0x90,
    0x90,
    0xF0,  # 0
    0x20,
    0x60,
    0x20,
    0x20,
    0x70,  # 1
    0xF0,
    0x10,
    0xF0,
    0x80,
    0xF0,  # 2
    0xF0,
    0x10,
    0xF0,
    0x10,
    0xF0,  # 3
    0x90,
    0x90,
    0xF0,
    0x10,
    0x10,  # 4
    0xF0,
    0x80,
    0xF0,
    0x10,
    0xF0,  # 5
    0xF0,
    0x80,
    0xF0,
    0x90,
    0xF0,  # 6
    0xF0,
    0x10,
    0x20,
    0x40,
    0x40,  # 7
    0xF0,
    0x90,
    0xF0,
    0x90,
    0xF0,  # 8
    0xF0,
    0x90,
    0xF0,
    0x10,
    0xF0,  # 9
    0xF0,
    0x90,
    0xF0,
    0x90,
    0x90,  # A
    0xE0,
    0x90,
    0xE0,
    0x90,
    0xE0,  # B
    0xF0,
    0x80,
    0x80,
    0x80,
    0xF0,  # C
    0xE0,
    0x90,
    0x90,
    0x90,
    0xE0,  # D
    0xF0,
    0x80,
    0xF0,
    0x80,
    0xF0,  # E
    0xF0,
    0x80,
    0xF0,
    0x80,
    0x80,  # F
]


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


class Control(Protocol):
    def is_closed(self) -> bool:
        ...

    def is_pressed(self, key: int) -> bool:
        ...


class System:
    # bytes in the CHIP-8 RAM
    TOTAL_RAM = 4096
    INITIAL_PC = 512

    def __init__(self, display: Display, control: Control) -> None:
        self.ram = bytearray(System.TOTAL_RAM)
        self.ram[0x50:0x9F] = FONT_DATA
        self.stack = array.array("H")  # unsigned short
        self.pc: int = System.INITIAL_PC
        self.registers = bytearray(16)
        self.index_register: int = 0
        self.display = display
        self.control = control
        # timestamp of when the timer was started
        self.delay_timer = 0
        self.delay_timer_start = 0.0
        self.sound_timer = 0
        self.sound_timer_start = 0.0

    def update_timers(self) -> None:
        if self.delay_timer != 0:
            cur_time = time()
            elapsed_timer = int(60 * abs(cur_time - self.delay_timer_start))
            self.delay_timer = max(0, self.delay_timer - elapsed_timer)

        if self.sound_timer != 0:
            cur_time = time()
            elapsed_timer = int(60 * abs(cur_time - self.sound_timer_start))
            self.sound_timer = max(0, self.sound_timer - elapsed_timer)

    def load(self, raw_data: bytes) -> None:
        self.ram[System.INITIAL_PC : System.INITIAL_PC + len(raw_data)] = raw_data

    def run(self) -> None:
        while True:
            if self.control.is_closed():
                return
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
        # print(self.pc, "->", n1, n2, n3, n4)
        match (n1, n2, n3, n4):
            case (0, 0, 0xE, 0):
                self.display.clear()
            case (0, 0, 0xE, 0xE):
                # TODO untested opcode
                # return from subroutine
                self.pc = self.stack.pop()
            case (1, _, _, _):
                # jump to the 3 nibbles read in order
                self.pc = n2 << 8 | b2
            case (2, _, _, _):
                # TODO untested opcode
                # subroutine at NNN
                # store the current PC, and jump to the new one
                self.stack.append(self.pc)
                self.pc = n2 << 8 | b2
            case (3, _, _, _):
                # TODO untested opcode
                # if register n2 is equal to b2, skip next instruction
                if self.registers[n2] == b2:
                    self.pc += 2
            case (4, _, _, _):
                # TODO untested opcode
                # if register n2 is NOT equal to b2, skip next instruction
                if self.registers[n2] != b2:
                    self.pc += 2
            case (5, _, _, 0):
                # TODO untested opcode
                # skip if n2 and n3 register are equal
                if self.registers[n2] == self.registers[n3]:
                    self.pc += 2
            case (6, _, _, _):
                # set register n2 as b2
                self.registers[n2] = b2
            case (7, _, _, _):
                # add to register, ignore overflow
                self.registers[n2] = (self.registers[n2] + b2) & 0xFF
            case (8, _, _, 0):
                # TODO untested opcode
                # set n2 register to n3
                self.registers[n2] = self.registers[n3]
            case (8, _, _, 1):
                # TODO untested opcode
                # binary OR
                # set n2 register to n2 | n3
                self.registers[n2] |= self.registers[n3]
            case (8, _, _, 2):
                # TODO untested opcode
                # binary AND
                # set n2 register to n2 & n3
                self.registers[n2] &= self.registers[n3]
            case (8, _, _, 3):
                # TODO untested opcode
                # binary XOR
                # set n2 register to n2 ^ n3
                self.registers[n2] ^= self.registers[n3]
            case (8, _, _, 4):
                # TODO untested opcode
                # ADD with carry
                # set n2 register to n2 + n3
                # register F is set to the overflow
                sum_value = self.registers[n2] + self.registers[n3]
                self.registers[0xF] = sum_value >> 8
                self.registers[n2] = sum_value & 0xFF
            case (8, _, _, 5):
                # TODO untested opcode
                # SUB with carry
                # set n2 register to n2 - n3
                # register F is set to the overflow
                self.registers[0xF] = (
                    1 if self.registers[n2] > self.registers[n3] else 0
                )
                self.registers[n2] = (self.registers[n2] - self.registers[n3]) & 0xFF
            case (8, _, _, 6):
                # TODO untested opcode
                # NOTE this apparently is the SUPER-CHIP version,
                # the original CHIP-8 version did
                # self.registers[n2] = self.registers[n3]
                self.registers[0xF] = self.registers[n2] & 1
                self.registers[n2] = self.registers[n2] >> 1
            case (8, _, _, 7):
                # TODO untested opcode
                # SUB with carry
                # set n2 register to n3 - n2
                # register F is set to the overflow
                self.registers[0xF] = (
                    1 if self.registers[n3] > self.registers[n2] else 0
                )
                self.registers[n2] = (self.registers[n3] - self.registers[n2]) & 0xFF
            case (8, _, _, 0xE):
                # TODO untested opcode
                # shift register n2 left, bit 7 stored into register VF
                # note that n3 is ignored
                self.registers[0xF] = self.registers[n2] & 0x80 >> 7
                self.registers[n2] = (self.registers[n2] << 1) & 0xFF
            case (9, _, _, 0):
                # TODO untested opcode
                # skip if n2 and n3 register are NOT equal
                if self.registers[n2] != self.registers[n3]:
                    self.pc += 2
            case (0xA, _, _, _):
                # set register I with the concatenated nibbles
                self.index_register = n2 << 8 | b2
            case (0xC, _, _, _):
                # TODO untested opcode
                # set register n2 to a random byte AND with b2
                self.registers[n2] = randint(0, 0xFF) & b2
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
            case (0xE, _, 9, 0xE):
                if self.control.is_pressed(n2):
                    self.pc += 2
            case (0xE, _, 0xA, 1):
                if not self.control.is_pressed(n2):
                    self.pc += 2
            case (0xF, _, 0, 7):
                # TODO untested opcode
                self.update_timers()
                self.registers[n2] = self.delay_timer
            case (0xF, _, 1, 5):
                # TODO untested opcode
                self.delay_timer = self.registers[n2]
                self.delay_timer_start = time()
            case (0xF, _, 1, 8):
                # TODO untested opcode
                self.sound_timer = self.registers[n2]
                self.sound_timer_start = time()
            case (0xF, _, 2, 9):
                # TODO untested opcode
                # location of font data for difig in n2
                self.index_register = 0x50 + n2 * 5
            case (0xF, _, 3, 3):
                # TODO untested opcode
                # binary-coded decimal conversion
                num = str(int(self.registers[n2]))
                if self.index_register > len(self.registers):
                    print("WARNING: out of range on FX33: ", self.index_register)
                    return
                self.registers[self.index_register] = int(num[0])
                self.registers[self.index_register + 1] = int(num[2])
                self.registers[self.index_register + 2] = int(num[2])

            case (0xF, _, 1, 0xE):
                # TODO untested opcode
                # add to I the register in n2
                # NOTE: this changes depending on the implementations
                # some allow overflowing and some cap to 0xFF
                # self.index_register = (self.index_register + self.registers[n2]) & 0xFF
                self.index_register = self.index_register + self.registers[n2]

            case (0xF, _, 5, 5):
                # TODO untested opcode
                for ri in range(n2 + 1):
                    self.ram[self.index_register + ri] = self.registers[ri]
            case (0xF, _, 6, 5):
                # TODO untested opcode
                for ri in range(n2 + 1):
                    self.registers[ri] = self.ram[self.index_register + ri]
            case _:
                raise ValueError(f"Unknown operation {(n1, n2, n3, n4)}")
