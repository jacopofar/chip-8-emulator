from chip8_emulator.cli_display import CliDisplay
from chip8_emulator.core import System
from chip8_emulator.tk_display import TkDisplay

# this acts ad Display and Control
dc = TkDisplay()
s = System(dc, dc)
# s.load(open("Pong (alt).ch8", "rb").read())
# s.load(open("Zero Demo [zeroZshadow, 2007].ch8", "rb").read())
# s.load(open("Sierpinski [Sergey Naydenov, 2010].ch8", "rb").read())
# s.load(open("Maze (alt) [David Winter, 199x].ch8", "rb").read())
# s.load(open("Chip8 Picture.ch8", "rb").read())
s.load(open("test_opcode.ch8", "rb").read())
# s.load(open("Particle Demo [zeroZshadow, 2008].ch8", "rb").read())
s.run()
