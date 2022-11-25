import unittest
from unittest import IsolatedAsyncioTestCase
import asyncio
import logging
import sys
from bot import write_json, get_delta, startup
import json

channel = 0 # <- change this to the channel you want to run tests on


async def mock_write_json():
        channelId = channel
        delta = get_delta(10,'s')
        await write_json(channelId, delta)
        f = open('timers.json', 'r')
        timers = json.loads(f.read())
        f.close()
        return len(timers)

class Test(IsolatedAsyncioTestCase):
    async def test_write_json(self):
        # Write empty file
        f = open('timers.json', 'w')
        f.write('[]')
        f.close()
        
        # Add the same channel x2 
        await mock_write_json()
        entries = await mock_write_json()

        self.assertEqual(1, entries)

    async def test_startup(self):
        await startup()



if __name__ == "__main__":
    logging.basicConfig( stream=sys.stderr )
    logging.getLogger( "SomeTest.testSomething" ).setLevel( logging.DEBUG )
    asyncio.run(unittest.main())
