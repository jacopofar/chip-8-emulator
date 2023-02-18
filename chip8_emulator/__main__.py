from chip8_emulator.core import System

s = System()
s.load(open("IBM Logo.ch8", "rb").read())
s.run()
