from storage import TomlConfig
from scheduler import Scheduler
from staff import issues
from web import WebAPI
import asyncio


async def main(loop):
    config = TomlConfig("config.toml", "config.template.toml")
    if config.is_new:
        print("No config detected, extracting from the template...")
        return
    scheduler = Scheduler(loop)
    WebAPI(config, issues).start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
