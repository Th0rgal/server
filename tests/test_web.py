import sys
import unittest
import logging
import asyncio
import time

sys.path.append("../")
import cashplace

logging.basicConfig(level=logging.INFO)


class TestQueries(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        loop = asyncio.get_event_loop()
        cashplace.__main__.main(loop)
        loop.run_forever()

    async def test_connection(self):
        pass


if __name__ == "__main__":
    unittest.main()
