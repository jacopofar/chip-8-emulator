from chip8_emulator import core


# this implements the Display protocol for the CLI interface
# but there's no Control protocol
class CliDisplay:
    def __init__(self) -> None:
        self.screen = bytearray(core.SCREEN_WIDTH * core.SCREEN_HEIGHT)

    def clear(self) -> None:
        for i in range(len(self.screen)):
            self.screen[i] = 0

    def draw(self, x: int, y: int, sprite_data: bytearray) -> bool:
        x = x % core.SCREEN_WIDTH
        y = y % core.SCREEN_HEIGHT
        did_switch = False
        for yo, sprite_byte in enumerate(sprite_data):
            if y + yo >= core.SCREEN_HEIGHT:
                break
            for xo, bit in enumerate(core.byte_to_bits(sprite_byte)):
                if x + xo >= core.SCREEN_WIDTH:
                    break
                # position this refers to
                cur_pixel_idx = x + xo + (y + yo) * core.SCREEN_WIDTH
                if bit == 1:
                    if self.screen[cur_pixel_idx] == 1:
                        self.screen[cur_pixel_idx] = 0
                        did_switch = True
                    else:
                        self.screen[cur_pixel_idx] = 1
        return did_switch

    def show(self) -> None:
        res = ""
        for idx in range(len(self.screen)):
            if idx % core.SCREEN_WIDTH == 0:
                res += "\n"
            res += "░" if self.screen[idx] == 0 else "█"
        print(res)
