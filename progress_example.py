import time
import better_exceptions
from better_exceptions import color

from progressbar import Progress

progress = Progress(max_value=1000, significant=105)

print(progress.widht)


def some_func(i):
    time.sleep(2)


def sharp_func(i):
    if 0 == i % 100:
        time.sleep(1)

print("Start")

for i in range(1000):
    some_func(i)
    progress.update()

print("\nEnd!")