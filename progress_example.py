import time
import better_exceptions
from better_exceptions import color

from progressbar import Progress

progress = Progress(max_value=1000)

print(progress.widht)


def some_func(i):
    time.sleep(0.1)

print("Start")

for i in range(1000):
    some_func(i)
    progress.update()

print("\nEnd!")