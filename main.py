import asyncio
from bleak import BleakClient
from dotenv import load_dotenv
import facet_action
import os
from productive import Productive
from productive import TimeEntry
import timed_input
import time_entry_picker

load_dotenv()

clientCalibrationVersion = b'\x00\x00\x00\x01'

productive = Productive(os.getenv('PRODUCTIVE_TOKEN'), os.getenv('PRODUCTIVE_ORGANIZATION_ID'))

storage = facet_action.Storage()
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
            picker = time_entry_picker.TimeEntryPicker(time_entries)
            picked_option = await timed_input.timed_input(picker.create_option_list(), 5)
            if picked_option is None:
                return
            picked_option = int(picked_option)
            if picked_option < 0 or picked_option >= len(time_entries):
                return
            action = picker.get_facet_action(picked_option)
            storage.add_facet_action(facet, action)
            loop.create_task(execute_facet_action(action))

        async def execute_facet_action(action: facet_action.FacetAction):
            stopped_time_entry = productive.stop_time_entry()

            if stopped_time_entry is not None:
                loop.create_task(print_update("Stopped '{0}'".format(stopped_time_entry.description)))

            if action.action == facet_action.Actions.START:
                productive.start_time_entry(action.time_entry)
                loop.create_task(show_started_time_entry(action.time_entry))

        def facet_handler(sender, data):
            if data == b'':
                loop.create_task(handle_error("Facet data is empty probable wrong password."))
                return

            loop.create_task(print_update("Facet changed"))

            action = storage.get_facet_action(data[0])
            if action is None:
                loop.create_task(calibrate_facet(data[0]))
            else:
                loop.create_task(execute_facet_action(action))

        async def handle_error(message: str):
            print("An error occurred, disconnecting: {0}".format(message))
            loop.create_task(client.disconnect())

        async def show_started_time_entry(time_entry: TimeEntry):
            print("Started '{0}'".format(time_entry.description))

        await client.start_notify(FACET_UUID, facet_handler)

        loop.create_task(print_update("Connected with Timeflip"))

        while await client.is_connected():
            await asyncio.sleep(1)


if __name__ == "__main__":
    address = "2B160B66-3467-472D-B8D1-E2BD976DBFFE"

    loop = asyncio.get_event_loop()
    loop.create_task(print_update("Connecting Timeflip"))
    loop.run_until_complete(run())
