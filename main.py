import asyncio
from bleak import BleakClient
from dotenv import load_dotenv
import os
import productive
import storage
import timed_input

load_dotenv()

clientCalibrationVersion = b'\x00\x00\x00\x01'

productive = productive.Productive(os.getenv('PRODUCTIVE_TOKEN'), os.getenv('PRODUCTIVE_ORGANIZATION_ID'))

storage = storage.Repository()
storage.load()

CALIBRATION_UUID = "F1196F56-71A4-11E6-BDF4-0800200C9A66"
FACET_UUID = "F1196F52-71A4-11E6-BDF4-0800200C9A66"
PASSWORD_UUID = "F1196F57-71A4-11E6-BDF4-0800200C9A66"


async def run(address: str):
    async with BleakClient(address) as client:
        """ Authorize this client with the Timeflip server password """
        await client.write_gatt_char(PASSWORD_UUID, bytearray('000000', 'utf-8'))

        """ Set calibration version after Timeflip reset """
        server_calibration_version = await client.read_gatt_char(CALIBRATION_UUID)
        if server_calibration_version != clientCalibrationVersion:
            storage.reset()
            await client.write_gatt_char(CALIBRATION_UUID, clientCalibrationVersion)

        async def calibrate_facet(facet: int):
            time_entry_id = await timed_input.timed_input("Which time entry do you want to start? ", 5)
            if time_entry_id is None:
                return
            storage.calibrate_facet(facet, time_entry_id)
            loop.create_task(print_icon(time_entry_id))
            loop.create_task(start_time_entry(time_entry_id))

        def facet_handler(sender, data):
            if data == b'':
                loop.create_task(handle_error("Facet data is empty probable wrong password."))
                return

            icon = storage.get_icon(data[0])
            if icon is None:
                loop.create_task(calibrate_facet(data[0]))
            else:
                loop.create_task(print_icon(icon))
                loop.create_task(start_time_entry(icon))

        async def handle_error(message: str):
            print("An error occurred, disconnecting: {0}".format(message))
            loop.create_task(client.disconnect())

        async def print_icon(icon: str):
            print("Icon {0} is now up".format(icon))

        async def start_time_entry(time_entry_id):
            print(productive.start_time_entry(time_entry_id))

        await client.start_notify(FACET_UUID, facet_handler)

        while await client.is_connected():
            await asyncio.sleep(1)


if __name__ == "__main__":
    address = "2B160B66-3467-472D-B8D1-E2BD976DBFFE"

    print(productive.time_entries())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address))
