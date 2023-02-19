from chip8_emulator.cli_display import CliDisplay
from chip8_emulator.core import System
from chip8_emulator.tk_display import TkDisplay

# this acts ad Display and Control
dc = TkDisplay()
s = System(dc, dc)
s.load(open("test_opcode.ch8", "rb").read())
s.run()
