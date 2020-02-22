"""
AsciiPlayer() opens a text file and plays the text column-wise at a set
number of columns per second.
"""
import time
import curses
from collections import deque
from curses import wrapper


class AsciiPlayer:
    def __init__(self, in_stream, out_stream=None, speed=50):
        self.input = in_stream
        self.output = out_stream
        self.speed = speed
    
    def frames(self, max_char_length):
        lines = self.input.readlines()
        max_inp_length = len(max(lines, key=len))
        output = [deque([]) for _ in lines]
        total_chars = 0
        inp_char_index = 0
        inp_chars_onscreen = 0

        while True:
            if inp_char_index < max_inp_length:
                for lineno, line in enumerate(lines):
                    if len(line) > inp_char_index and line[inp_char_index] != '\n':
                        output[lineno].append(line[inp_char_index])
                    else:
                        output[lineno].append(' ')
                inp_char_index += 1
                inp_chars_onscreen += 1
                total_chars += 1
            elif total_chars < max_char_length:
                for l in output:
                    l.append(' ')
                total_chars += 1
            if total_chars >= max_char_length:
                for l in output:
                    l.popleft()
                total_chars -= 1
                inp_chars_onscreen -= 1
            yield output, total_chars
            if inp_chars_onscreen <= 0:
                break

    @property
    def screen_length(self):
        return curses.COLS

    def print_frame(self, frame):
        left_pad = self.screen_length-1
        f_string = '{:>%d}\n' % (left_pad)
        self.screen.clear()
        for l in frame:
            self.screen.addstr(f_string.format(''.join(l)))
        self.screen.refresh()

    def tick(self):
        frame, _ = next(self.frame_iter)
        self.print_frame(frame)

    def _init(self, screen):
        self.screen = screen
        self.frame_iter = self.frames(max_char_length=self.screen_length-1)

    def _start(self):
        while True:
            try:
                self.tick()
            except StopIteration:
                break
            time.sleep(1/self.speed)

    def init(self):
        # Initialize curses
        stdscr = curses.initscr()

        # Turn off echoing of keys, and enter cbreak mode,
        # where no buffering is performed on keyboard input
        curses.noecho()
        curses.cbreak()

        # In keypad mode, escape sequences for special keys
        # (like the cursor keys) will be interpreted and
        # a special value like curses.KEY_LEFT will be returned
        stdscr.keypad(1)
        self.stdscr = stdscr
        self._init(stdscr)

    def start(self):
        try:
            self.init()
            self._start()
        finally:
            if self.stdscr:
                self.stdscr.keypad(0)
                curses.echo()
                curses.nocbreak()
                curses.endwin()

if __name__ == '__main__':
    with open('art.txt', 'r') as f:
        p = AsciiPlayer(f)
        p.start()
