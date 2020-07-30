from config import TomlConfig
from web import WebAPI
import asyncio


async def main(loop):
    config = TomlConfig()
    WebAPI(config)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))
    loop.run_forever()