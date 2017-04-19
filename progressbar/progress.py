import time
import shutil

import math

import sys


def print_line(s):
    sys.stdout.write("\r" + s)
    sys.stdout.flush()


class Progress:
    phases = (' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█')

    def __init__(self, max_value, item_name="i", significant = 10):
        self.widht, _ = shutil.get_terminal_size()
        self.widht -= 1
        self.current_value = 0
        self.max_value = max_value
        self.start_time = None
        self.significant_times = []
        self.significant = significant
        self.speed = 0
        self.item_name = item_name

    def update_max(self, max_value: int):
        self.max_value = max_value

    def update(self, increment=1):
        self.current_value += 1
        if self.start_time is None:
            self.start_time = time.time()
        cur_time = time.time()

        if len(self.significant_times) > self.significant:
            self.significant_times = self.significant_times[1:]

        self.significant_times.append(cur_time)

        if cur_time == self.significant_times[0]:
            self.speed = 0
        else:
            self.speed = len(self.significant_times) / (cur_time - self.significant_times[0])

        print_line(self._write(cur_time))

    def _write(self, cur_time):
        before = self._percent() + "["
        after = "] {} {} {}".format(
            self._speed(),
            self._elapsed(cur_time),
            self._eta(cur_time)
        )
        bar = self._bar(self.widht - len(before) - len(after))
        return before + bar + after

    @property
    def percent(self):
        return self.current_value / self.max_value

    def _percent(self):
        return "{:.2f}% ({}/{})".format(
            self.percent * 100,
            self.current_value,
            self.max_value,
        )

    def _bar(self, size):
        part = self.percent * size
        s = ""
        s += self.phases[-1] * math.trunc(part)
        s += self.phases[math.trunc(math.modf(part)[0] * 8)]
        s += " " * (size - len(s))
        return s

    @staticmethod
    def _time_convert(seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)

    def _elapsed(self, cur_time: int):
        return "Elapsed: {}".format(
            self._time_convert(cur_time - self.start_time)
        )

    def _speed(self):
        return "{:.2f} {}/s".format(self.speed, self.item_name)

    def _eta(self, cur_time):
        s = "ETA: "
        if self.speed == 0:
            return s + "Unknown"
        s += self._time_convert(
            (self.max_value - self.current_value) / self.speed
        )
        return s



