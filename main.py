import asyncio

from bleak import BleakClient
from bleak import _logger as logger

PASSWORD_UUID = "F1196F57-71A4-11E6-BDF4-0800200C9A66"
FACET_UUID = "F1196F52-71A4-11E6-BDF4-0800200C9A66"

facetDictionary = {
    2: "Fork and knife",
    17: "Television",
    14: "Brush",
    13: "Talk",
    9: "Pencil",
    7: "Shake hands",
    10: "Rocket",
    15: "Pauze",
    11: "Gaming",
    6: "Paw",
    16: "Lighting",
    12: "Dumble"
}

async def run(address):
    async with BleakClient(address) as client:
        x = await client.is_connected()
        logger.info("Connected: {0}".format(x))

        def facet_handler(sender, data):
            """ Stop when fork and knife is up """
            if data[0] == 2:
                loop.create_task(client.disconnect())

            icon = facetDictionary.get(data[0])
            loop.create_task(print_icon(icon))

        async def print_icon(icon):
            print("Icon {0} is now up".format(icon))

        await client.write_gatt_char(PASSWORD_UUID, bytearray('000000', 'utf-8'))
        await client.start_notify(FACET_UUID, facet_handler)

        while await client.is_connected():
            await asyncio.sleep(1)

if __name__ == "__main__":
    address = ("2B160B66-3467-472D-B8D1-E2BD976DBFFE")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address))