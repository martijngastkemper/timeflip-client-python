# Connect with Timeflip

I frist tried to make [a NodeJS version](https://github.com/martijngastkemper/timeflip-client), but that didn't work out. With [the Python package Bleak](https://github.com/hbldh/bleak) it works much better. It just works on MacOS.

The goal with this client is to connect Timeflip with Productive. To easily which between tasks.

## Usage

Install Python 3 and check out the source.

`cp .env.example .env`

Add the Productive API token to .env

Run `python main.py`.

## Features

- Bind facet to a Productive time entry
- Reset facet bindings when a new days starts

## Timeflip docs

[BLE documentation](https://github.com/DI-GROUP/TimeFlip.Docs/blob/master/Hardware/BLE_device_commutication_protocol_v3.0_en.md)
