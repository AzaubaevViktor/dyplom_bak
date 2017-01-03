import argparse

from actions import Actions

actions = Actions()

parser = argparse.ArgumentParser(
    description="Vk online grabber"
)

parser.add_argument("action", help="Actions")

namespace = parser.parse_args()

actions(namespace.action)
