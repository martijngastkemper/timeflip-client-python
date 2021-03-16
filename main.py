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


async def print_update(string: str):
    print(string)


async def run():
    async with BleakClient(address) as client:
        """ Authorize this client with the Timeflip server password """
        await client.write_gatt_char(PASSWORD_UUID, bytearray('000000', 'utf-8'))

        """ Set calibration version after Timeflip reset """
        server_calibration_version = await client.read_gatt_char(CALIBRATION_UUID)
        if server_calibration_version != clientCalibrationVersion:
            storage.reset()
            await client.write_gatt_char(CALIBRATION_UUID, clientCalibrationVersion)

        async def calibrate_facet(facet: int):
            time_entries = productive.time_entries()
            option_list = time_entries_to_option_list(time_entries)
            picked_option = await timed_input.timed_input(option_list, 5)
            if picked_option is None:
                return
            picked_option = int(picked_option)
            if picked_option < 0 or picked_option >= len(time_entries):
                return
            time_entry = time_entries[picked_option]
            storage.calibrate_facet(facet, time_entry)
            loop.create_task(start_time_entry(time_entry))
            loop.create_task(show_started_time_entry(time_entry))

        def time_entries_to_option_list(time_entries):
            output = "Pick a task to assign to this icon:\n"
            for k, time_entry in enumerate(time_entries):
                output = output + "{0}) {1}\n".format(k, time_entry['description'])
            return output.rstrip("\n")

        def facet_handler(sender, data):
            if data == b'':
                loop.create_task(handle_error("Facet data is empty probable wrong password."))
                return

            time_entry = storage.get_time_entry(data[0])
            if time_entry is None:
                loop.create_task(calibrate_facet(data[0]))
            else:
                loop.create_task(start_time_entry(time_entry))

        async def handle_error(message: str):
            print("An error occurred, disconnecting: {0}".format(message))
            loop.create_task(client.disconnect())

        async def show_started_time_entry(time_entry: dict):
            print("Starting '{0}'".format(time_entry["description"]))

        async def start_time_entry(time_entry):
            stopped_time_entry = productive.stop_time_entry()
            print(stopped_time_entry)
            if stopped_time_entry != "":
                loop.create_task(print_update("Time entry '{0}' stopped".format(stopped_time_entry)))

            productive.start_time_entry(time_entry)
            loop.create_task(show_started_time_entry(time_entry))

        await client.start_notify(FACET_UUID, facet_handler)

        loop.create_task(print_update("Connected with Timeflip"))

        while await client.is_connected():
            await asyncio.sleep(1)


if __name__ == "__main__":
    address = "2B160B66-3467-472D-B8D1-E2BD976DBFFE"

    loop = asyncio.get_event_loop()
    loop.create_task(print_update("Connecting Timeflip"))
    loop.run_until_complete(run())
