def byte_to_bits(b: int) -> list[int]:
    """Bits as 0 or 1 integers from most to least significant."""
    return [(b >> (7 - p) & 1) for p in range(8)]


class Display:
    WIDTH = 64
    HEIGHT = 32

    def __init__(self) -> None:
        self.screen = bytearray(Display.WIDTH * Display.HEIGHT)

    def clear(self) -> None:
        for i in range(len(self.screen)):
            self.screen[i] = 0

    def draw(self, x: int, y: int, sprite_data: bytearray) -> bool:
        x = x % Display.WIDTH
        y = y % Display.HEIGHT
        did_switch = False
        for yo, sprite_byte in enumerate(sprite_data):
            if y + yo >= Display.HEIGHT:
                break
            for xo, bit in enumerate(byte_to_bits(sprite_byte)):
                if x + xo >= Display.WIDTH:
                    break
                # position this refers to
                cur_pixel_idx = x + xo + (y + yo) * Display.WIDTH
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
            if idx % Display.WIDTH == 0:
                res += "\n"
            res += "░" if self.screen[idx] == 0 else "█"
        print(res)
