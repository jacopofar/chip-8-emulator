## CHIP 8 emulator

This is an emulator for the CHIP-8 virtual console written in Python 3.11.

No dependencies are needed to run is, the code is compliant with `mypy` strict-mode check.

## Status

The code passes the [CHIP-8 test ROM](https://github.com/corax89/chip8-test-rom) except for the (rare) FX33 instruction, and several programs I found online.

There are a few instructions that are "ambiguous" and have a different effect across versions of CHIP-8. Unfortunately there's no way to tell which version is used by a RO, only guess. In those cases I adopted the most recent ones because it seems to be the most common.

__NOTE__: sound and keyboad input are not yet implemented.