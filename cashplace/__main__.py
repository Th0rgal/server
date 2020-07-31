import argparse
import logging

# cli options
parser = argparse.ArgumentParser()
parser.add_argument(
    "-v", "--verbose", action="count", help="increase verbosity", default=0
)
parser.add_argument(
    "-s", "--silent", action="count", help="decrease verbosity", default=0
)
parser.add_argument("--fps", action="store", type=int, default=60)
options = parser.parse_args()
verbosity = 10 * max(0, min(3 - options.verbose + options.silent, 5))

# logging configuration
stdout = logging.StreamHandler()
stdout.formatter = logging.Formatter(
    "{asctime} [{levelname}] <{name}:{funcName}> {message}", style="{"
)
logging.root.handlers.clear()
logging.root.addHandler(stdout)
logging.root.setLevel(verbosity)
logger = logging.getLogger(__name__)

from storage import TomlConfig
from scheduler import Scheduler
from web import WebAPI
import asyncio

def main(loop):
    config = TomlConfig("config.toml", "config.template.toml")
    if config.is_new:
        logger.warning("No config detected, extracting from the template...")
        return
    scheduler = Scheduler(loop)
    WebAPI(config).start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    main(loop)
    loop.run_forever()
