from chip8_emulator.cli_display import CliDisplay
from chip8_emulator.core import System
from chip8_emulator.tk_display import TkDisplay

s = System(TkDisplay())
s.load(open("IBM Logo.ch8", "rb").read())
s.run()
