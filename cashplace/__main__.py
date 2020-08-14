import argparse
import logging
from tickets import TicketsManager

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
import tickets


def main(loop):
    config = TomlConfig("config.toml", "config.template.toml")
    if config.is_new:
        logger.warning("No config detected, extracting from the template...")
        return
    tickets_manager = TicketsManager(config)
    tickets_manager.load()
    if config.auto_clean:
        scheduler = Scheduler(loop)
        scheduler.schedule_repeating_task(
            config.task_delay,
            tickets.clean,
            tickets_manager=tickets_manager,
            config=config,
        )
    WebAPI(config, tickets_manager).start()


loop = asyncio.get_event_loop()
main(loop)
loop.run_forever()
