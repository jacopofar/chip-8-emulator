import tkinter
from multiprocessing import Process, Queue
from queue import Empty
from typing import Any

from chip8_emulator import core


class TkDisplay:
    PIXEL_SIZE = 10

    def _tk_window(
        self, queue_screen: "Queue[bytearray]", queue_event: "Queue[tuple[str]]"
    ) -> None:
        # init tk
        root = tkinter.Tk()

        # create canvas
        myCanvas = tkinter.Canvas(
            root,
            bg="white",
            height=core.SCREEN_HEIGHT * TkDisplay.PIXEL_SIZE,
            width=core.SCREEN_WIDTH * TkDisplay.PIXEL_SIZE,
        )

        pixels = []
        for y in range(core.SCREEN_HEIGHT):
            for x in range(core.SCREEN_WIDTH):
                pixels.append(
                    myCanvas.create_rectangle(
                        (
                            x * TkDisplay.PIXEL_SIZE,
                            y * TkDisplay.PIXEL_SIZE,
                            (x + 1) * TkDisplay.PIXEL_SIZE,
                            (y + 1) * TkDisplay.PIXEL_SIZE,
                        ),
                        fill="red",
                    )
                )

        # add to window and show
        myCanvas.pack()

        def key_pressed(event: Any) -> None:
            print(event)

        root.bind("<Key>", key_pressed)

        def check_queue(queue: "Queue[bytearray]" = queue_screen) -> None:
            try:
                screen = queue.get_nowait()
                for idx, value in enumerate(screen):
                    myCanvas.itemconfig(
                        pixels[idx], fill="grey" if value == 0 else "white"
                    )
            except Empty:
                pass
            root.after(2, check_queue)

        root.after(2, check_queue)
        root.mainloop()
        queue_event.put(("close",))

    def __init__(self) -> None:
        self.screen = bytearray(core.SCREEN_WIDTH * core.SCREEN_HEIGHT)
        self.queue_screen: Queue[bytearray] = Queue()
        self.queue_events: Queue[tuple[str]] = Queue()
        self.tk_process = Process(
            target=self._tk_window, args=(self.queue_screen, self.queue_events)
        )
        self.tk_process.start()
        self.closed = False  # did the user close the window?

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
        self.queue_screen.put(self.screen)
        return did_switch

    def show(self) -> None:
        # do nothing, the display happens in a thread regardless
        pass

    def check_queue(self) -> None:
        try:
            while True:
                update = self.queue_events.get_nowait()
                if update == ("close",):
                    self.closed = True
        except Empty:
            pass

    def is_closed(self) -> bool:
        self.check_queue()
        return self.closed
