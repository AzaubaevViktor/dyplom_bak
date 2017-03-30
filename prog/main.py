import argparse
import logging

from prog.actions import Actions

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s [%(asctime)s] |%(name)s| %(filename)s:%(funcName)s:%(lineno)d\n    %(message)s",
    datefmt='%d.%m.%Y %H:%M:%S'
)
logging.getLogger("requests").setLevel(logging.WARNING)

actions = Actions()

parser = argparse.ArgumentParser(
    description="Vk online grabber"
)

parser.add_argument("action", help="Actions")

namespace = parser.parse_args()

actions(namespace.action)
