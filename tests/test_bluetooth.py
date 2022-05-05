import asyncio
import pytest
from unittest.mock import patch, AsyncMock
from dalybms import DalyBMSBluetooth


class TestBluetoothCommands:
    notification_handler = None

    async def write_gatt_char_mock(self, char, data):
        assert (self.notification_handler is not None)

        # SoC command
        if data == b'\xa5\x80\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\xbd':
            # {'total_voltage': 53.0, 'current': -5.9, 'soc_percent': 92.2}
            self.notification_handler('90', b'\xa5\x01\x90\x08\x02\x12\x00\x00t\xf5\x03\x9aX')

        # Cell Voltage Range command
        if data == b'\xa5\x80\x91\x08\x00\x00\x00\x00\x00\x00\x00\x00\xbe':
            # {'highest_voltage': 3.315, 'highest_cell': 10, 'lowest_voltage': 3.308, 'lowest_cell': 1}
            self.notification_handler('91', b'\xa5\x01\x91\x08\x0c\xf3\n\x0c\xec\x01\x03\x9a\xde')

        # Temp range command
        if data == b'\xa5\x80\x92\x08\x00\x00\x00\x00\x00\x00\x00\x00\xbf':
            self.notification_handler('92', b'\xa5\x01\x92\x08=\x01=\x01\x00\x00\x00\xadi')

        # Mosfet status command
        if data == b'\xa5\x80\x93\x08\x00\x00\x00\x00\x00\x00\x00\x00\xc0':
            # {'mode': 'discharging', 'charging_mosfet': True, 'discharging_mosfet': True, 'capacity_ah': 256.76}
            self.notification_handler('93', b'\xa5\x01\x93\x08\x02\x01\x01\x9e\x00\x03\xea\xf8\xc8')

        # Status command
        if data == b'\xa5\x80\x94\x08\x00\x00\x00\x00\x00\x00\x00\x00\xc1':
            self.notification_handler('94', b'\xa5\x01\x94\x08\x10\x01\x00\x00\x02\x00\x0b\x9b\xfb')

        # Cell Voltages command
        if data == b'\xa5\x80\x95\x08\x00\x00\x00\x00\x00\x00\x00\x00\xc2':
            self.notification_handler('95',
                                      b'\xa5\x01\x95\x08\x01\r7\r6\r4\x9b\xa7\xa5\x01\x95\x08\x02\r5\r5\r5\x9b\xa6'
                                      b'\xa5\x01\x95\x08\x03\r4\r>\r6\x9b\xb0\xa5\x01\x95\x08\x04\r7\r6\r7\x9b\xad'
                                      b'\xa5\x01\x95\x08\x05\r4\r5\r4\x9b\xa7\xa5\x01\x95\x08\x06\r7\x00\x00\x00\x00'
                                      b'\x9b(\xa5\x01\x95\x08\x07\x00\x00\x00\x00\x00\x00\x9b\xe5\xa5\x01\x95\x08\x08'
                                      b'\x00\x00\x00\x00\x00\x00\x9b\xe6\xa5\x01\x95\x08\t\x00\x00\x00\x00\x00\x00'
                                      b'\x9b\xe7\xa5\x01\x95\x08\n\x00\x00\x00\x00\x00\x00\x9b\xe8\xa5\x01\x95\x08'
                                      b'\x0b\x00\x00\x00\x00\x00\x00\x9b\xe9\xa5\xa8\x00@\x00p$@\x00\r0\x00\x00p$'
                                      b'@\x008\xa7\x00\x00m2\x00\x00p$@\x00S1\x00\x00\x00\x00\x00\x00\xa8\x00\xa5\x01'
                                      b'\x95\x08\x0f\x00\x00\x00\x00\x00\x00\x9b\xed\xa5\x01\x95\x08\x10')

        # Temperatures command
        if data == b'\xa5\x80\x96\x08\x00\x00\x00\x00\x00\x00\x00\x00\xc3':
            self.notification_handler('96', b'\xa5\x01\x96\x08\x01=\x00\x00\x00\x00\x00\x00\x82\xa5\x01\x96\x08\x02\x00\x00\x00\x00\x00\x00\x00F')

        # Balancing status command
        if data == b'\xa5\x80\x97\x08\x00\x00\x00\x00\x00\x00\x00\x00\xc4':
            self.notification_handler('97', b'\xa5\x01\x97\x08\x00\x00\x00\x00\x00\x00\x00\x00E')

        # get errors command
        if data == b'\xa5\x80\x98\x08\x00\x00\x00\x00\x00\x00\x00\x00\xc5':
            # []
            self.notification_handler('98', b'\xa5\x01\x98\x08\x00\x00\x00\x00\x00\x00\x00\x00F')

    async def start_notify_mock(self, char_uuid, notification_handler):
        self.notification_handler = notification_handler

    def setup_bleak_mock(self, bleak_mock):
        instance = bleak_mock.return_value
        instance.connect = AsyncMock(return_value=True)
        instance.start_notify = self.start_notify_mock
        instance.write_gatt_char = self.write_gatt_char_mock

    @pytest.mark.asyncio
    async def test_get_soc(self):
        with patch('dalybms.daly_bms_bluetooth.BleakClient') as bleak_mock:
            self.setup_bleak_mock(bleak_mock)

            daly = DalyBMSBluetooth()
            await daly.connect('99:99:99:99:99:99')

            response = await daly.get_soc()

            # {'total_voltage': 53.0, 'current': -5.9, 'soc_percent': 92.2}
            assert (response['total_voltage'] == 53.0)
            assert (response['current'] == -5.9)
            assert (response['soc_percent'] == 92.2)

    @pytest.mark.asyncio
    async def test_get_cell_voltage_range(self):
        with patch('dalybms.daly_bms_bluetooth.BleakClient') as bleak_mock:
            self.setup_bleak_mock(bleak_mock)

            daly = DalyBMSBluetooth()
            await daly.connect('99:99:99:99:99:99')

            response = await daly.get_cell_voltage_range()

            # {'highest_voltage': 3.315, 'highest_cell': 10, 'lowest_voltage': 3.308, 'lowest_cell': 1}
            assert (response['highest_voltage'] == 3.315)
            assert (response['highest_cell'] == 10)
            assert (response['lowest_voltage'] == 3.308)
            assert (response['lowest_cell'] == 1)

    @pytest.mark.asyncio
    async def test_get_max_min_temperature(self):
        with patch('dalybms.daly_bms_bluetooth.BleakClient') as bleak_mock:
            self.setup_bleak_mock(bleak_mock)

            daly = DalyBMSBluetooth()
            await daly.connect('99:99:99:99:99:99')

            response = await daly.get_max_min_temperature()

            assert (response['highest_temperature'] == 21)
            assert (response['highest_sensor'] == 1)
            assert (response['lowest_temperature'] == 21)
            assert (response['lowest_sensor'] == 1)

    @pytest.mark.asyncio
    async def test_get_mosfet_status(self):
        with patch('dalybms.daly_bms_bluetooth.BleakClient') as bleak_mock:
            self.setup_bleak_mock(bleak_mock)

            daly = DalyBMSBluetooth()
            await daly.connect('99:99:99:99:99:99')

            response = await daly.get_mosfet_status()

            # {'mode': 'discharging', 'charging_mosfet': True, 'discharging_mosfet': True, 'capacity_ah': 256.76}
            assert (response['mode'] == 'discharging')
            assert (response['charging_mosfet'] is True)
            assert (response['discharging_mosfet'] is True)
            assert (response['capacity_ah'] == 256.76)

    @pytest.mark.asyncio
    async def test_status(self):
        with patch('dalybms.daly_bms_bluetooth.BleakClient') as bleak_mock:
            self.setup_bleak_mock(bleak_mock)

            daly = DalyBMSBluetooth()
            await daly.connect('99:99:99:99:99:99')

            response = await daly.get_status()

            assert (response['cells'] == 16)
            assert (response['cycles'] == 11)
            assert (response['temperature_sensors'] == 1)

    @pytest.mark.asyncio
    async def test_get_cell_voltages(self):
        with patch('dalybms.daly_bms_bluetooth.BleakClient') as bleak_mock:
            self.setup_bleak_mock(bleak_mock)

            daly = DalyBMSBluetooth()
            await daly.connect('99:99:99:99:99:99')

            daly.status = {"cells": 16}

            response = await daly.get_cell_voltages()

            assert (response[1] == 3.383)
            assert (response[2] == 3.382)
            assert (response[3] == 3.380)
            assert (response[4] == 3.381)
            assert (response[5] == 3.381)
            assert (response[6] == 3.381)
            assert (response[7] == 3.380)
            assert (response[8] == 3.390)
            assert (response[9] == 3.382)
            assert (response[10] == 3.383)
            assert (response[11] == 3.382)
            assert (response[12] == 3.383)
            assert (response[13] == 3.380)
            assert (response[14] == 3.381)
            assert (response[15] == 3.380)
            assert (response[16] == 3.383)

    @pytest.mark.asyncio
    async def test_get_temperatures(self):
        with patch('dalybms.daly_bms_bluetooth.BleakClient') as bleak_mock:
            self.setup_bleak_mock(bleak_mock)

            daly = DalyBMSBluetooth()
            await daly.connect('99:99:99:99:99:99')
            await daly.get_status()

            response = await daly.get_temperatures()

            assert (response[1] == 21)


    @pytest.mark.asyncio
    async def test_get_balancing_status(self):
        with patch('dalybms.daly_bms_bluetooth.BleakClient') as bleak_mock:
            self.setup_bleak_mock(bleak_mock)

            daly = DalyBMSBluetooth()
            await daly.connect('99:99:99:99:99:99')
            await daly.get_status()

            response = await daly.get_balancing_status()

            assert (response['error'] == 'not implemented')


    @pytest.mark.asyncio
    async def test_get_errors(self):
        with patch('dalybms.daly_bms_bluetooth.BleakClient') as bleak_mock:
            self.setup_bleak_mock(bleak_mock)

            daly = DalyBMSBluetooth()
            await daly.connect('99:99:99:99:99:99')

            response = await daly.get_errors()

            assert (response == [])
