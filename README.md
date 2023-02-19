## CHIP 8 emulator

This is an emulator for the CHIP-8 virtual console written in Python 3.11.

No dependencies are needed to run is, the code is compliant with `mypy` strict-mode check.

## Status

The code passes the [CHIP-8 test ROM](https://github.com/corax89/chip8-test-rom), and can run several programs I found online. At the moment the keyboard seems to be weird but I am not sure how it was supposed to run in first place.

There are a few instructions that are "ambiguous" and have a different effect across versions of CHIP-8. Unfortunately there's no way to tell which version is used by a RO, only guess. In those cases I adopted the most recent ones because it seems to be the most common.

__NOTE__: sound is not implemented. There are no nice ways to do so without extra libraries.

# Links

* guide: https://tobiasvl.github.io/blog/write-a-chip-8-emulator
* test ROM: https://github.com/corax89/chip8-test-rom
* sparse roms: https://github.com/loktar00/chip8/tree/master/roms
* even more resources: https://github.com/tobiasvl/awesome-chip-8
