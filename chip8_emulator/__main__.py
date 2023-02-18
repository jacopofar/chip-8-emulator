from chip8_emulator.core import System
from chip8_emulator.display import Display

s = System(Display())
s.load(open("IBM Logo.ch8", "rb").read())
s.run()
