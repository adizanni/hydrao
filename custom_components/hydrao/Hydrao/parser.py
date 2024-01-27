"""Parser for Hydrao BLE devices"""

from __future__ import annotations

import asyncio
import dataclasses
import struct
from collections import namedtuple
from datetime import datetime
import logging

# from logging import Logger
from math import exp
from typing import Any, Callable, Tuple

from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection

READ_UUID = "0000ff02-0000-1000-8000-00805f9b34fb"

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class HydraoDevice:
    """Response data with information about the Hydrao device"""

    hw_version: str = ""
    sw_version: str = ""
    name: str = ""
    identifier: str = ""
    address: str = ""
    sensors: dict[str, str | float | None] = dataclasses.field(
        default_factory=lambda: {}
    )

# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
class HydraoBluetoothDeviceData:
    """Data for Hydrao BLE sensors."""

    _event: asyncio.Event | None
    _command_data: bytearray | None

    def __init__(
        self,
        logger: logging.Logger,
    ):
        super().__init__()
        self.logger = logger
        self.logger.debug("In Device Data")
        
    def decode(self, byte_frame : bytes ):

        frame_array = [int(x) for x in byte_frame]
        size = len(frame_array)

        for i in range(size-1, 0 , -1):
            tmp=frame_array[i]
            hibit1=(tmp&0x55)<<1
            lobit1=(tmp&0xAA)>>1
            tmp=frame_array[i-1]
            hibit=(tmp&0x55)<<1
            lobit=(tmp&0xAA)>>1
            frame_array[i]=0xff -(hibit1|lobit)
            frame_array[i-1]= 0xff -(hibit|lobit1)

        return frame_array
    
    def reverse_bytes(self, bytes : list):
        return (bytes[0] << 8) + bytes[1]

    def decode_position(self,decodedData,idx):
        return self.reverse_bytes(decodedData[idx:idx+2])
        
    async def _get_status(self, client: BleakClient, device: HydraoDevice) -> HydraoDevice:
        
        _LOGGER.debug("Getting Status")

        #battery_service_uuid = "0000180f-0000-1000-8000-00805f9b34fb"
        #service = await client.services[]
        
        data1 = await client.read_gatt_char("0000ca1c-0000-1000-8000-00805f9b34fb")
        device.sensors["current_volume"] = int.from_bytes(data1[2:4], byteorder="little")
        device.sensors["total_volume"] = int.from_bytes(data1[0:2], byteorder="little")
        data2 = await client.read_gatt_char("0000ca32-0000-1000-8000-00805f9b34fb")
        device.sensors["current_temperature"] = (int.from_bytes(data2[0:2], byteorder="little") / 2)
        device.sensors["average_temperature"] = (int.from_bytes(data2[2:4], byteorder="little") / 2)
        data3 = await client.read_gatt_char("0000ca26-0000-1000-8000-00805f9b34fb")
        device.sensors["current_duration"] = (int.from_bytes(data3[0:2], byteorder="little") / 50)

        _LOGGER.debug("Got Status")
        
        return device
    
    async def update_device(self, ble_device: BLEDevice) -> HydraoDevice:
        """Connects to the device through BLE and retrieves relevant data"""
        _LOGGER.debug("Update Device")
        client = await establish_connection(BleakClient, ble_device, ble_device.address,max_attempts=1)
        _LOGGER.debug("Got Client")
        #await client.pair()
        device = HydraoDevice()
        _LOGGER.debug("Made Device")
        try:
            device = await self._get_status(client, device)
            device.name = ble_device.address
            device.address = ble_device.address
            _LOGGER.debug("device.name: %s", device.name)
            _LOGGER.debug("device.address: %s", device.address)
        except:
            _LOGGER.debug("Disconnect")
        
        await client.disconnect()

        return device