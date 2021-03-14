import asyncio
import timed_input
import storage

from bleak import BleakClient

clientCalibrationVersion = b'\x00\x00\x00\x01';

storage = storage.Repository()
storage.load()

CALIBRATION_UUID = "F1196F56-71A4-11E6-BDF4-0800200C9A66"
FACET_UUID = "F1196F52-71A4-11E6-BDF4-0800200C9A66"
PASSWORD_UUID = "F1196F57-71A4-11E6-BDF4-0800200C9A66"


async def run(address):
    async with BleakClient(address) as client:
        """ Authorize this client with the Timeflip server password """
        await client.write_gatt_char(PASSWORD_UUID, bytearray('000000', 'utf-8'))

        """ Set calibration version after Timeflip reset """
        server_calibration_version = await client.read_gatt_char(CALIBRATION_UUID)
        if server_calibration_version != clientCalibrationVersion:
            storage.reset()
            await client.write_gatt_char(CALIBRATION_UUID, clientCalibrationVersion)

        """ Handle uncalibrated facet """
        async def calibrate_facet(facetId):
            icon_name = await timed_input.timed_input("Which icon do you see? ", 5)
            if icon_name is None:
                return
            storage.calibrate_facet(facetId, icon_name)
            loop.create_task(print_icon(icon_name))

        """ Handle facet change """

        def facet_handler(sender, data):
            if data == b'':
                loop.create_task(handle_error("Facet data is empty probable wrong password."))
                return

            icon = storage.get_icon(data[0])
            if icon is None:
                loop.create_task(calibrate_facet(data[0]))
            else:
                loop.create_task(print_icon(icon))

        async def handle_error(message):
            print("An error occurred, disconnecting: {0}".format(message))
            loop.create_task(client.disconnect())

        async def print_icon(icon):
            print("Icon {0} is now up".format(icon))

        await client.start_notify(FACET_UUID, facet_handler)

        while await client.is_connected():
            await asyncio.sleep(1)

if __name__ == "__main__":
    address = "2B160B66-3467-472D-B8D1-E2BD976DBFFE"

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address))