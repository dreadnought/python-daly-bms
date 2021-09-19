import serial
import struct
import logging

"""
List from BMStool PC / Sinowealth
1 = Cell 1 Voltage
...
09 = Cell 9 Voltage
0A = Cell 10 Voltage
0B = Total Voltage
0C = External Temperature 1
0D = External Temperature 2
0E = IC Temperature 1
0F = IC Temperature 2
10 = CADC Current (4 byte)
11 = Full Charge Capacity (4 byte)
12 = Remaining Capacity (4 byte)
13 = RSOC
14 = Cycle Count
15 = Pack Status
16 = Battery Status
17 = Pack Config
18 = Manufacture Access
"""


class DalyBMSSinowealth:
    PACK_STATUS = {
        0: 'CAL: ',
        5: 'VDQ: Valid Discharge Qualified',
        6: 'FD: Fully Discharged',
        7: 'FC: Fully Charged',
        9: 'FAST_DSG: Fast Discharging',
        10: 'MID_DSG: Medium Discharging',
        11: 'SLOW_DSG: Slow Discharging',
        12: 'DSGING: Discharging',
        13: 'CHGING: Charging',
        14: 'DSGMOS: Discharging enabled',
        15: 'CHGMOS: Charging enabled',
    }

    BATTERY_STATUS = {
        1: 'CTO',
        2: 'AFE_SC: Short Circuit in AFE (Analog Front End)',
        3: 'AFE_OV: Over Voltage in AFE (Analog Front End)',
        4: 'UTD: Under Voltage in Discharge',
        5: 'UTC: Under Voltage in Charge',
        6: 'OTD: Over Voltage in Discharge',
        7: 'OTC: Over Voltage in Charge',
        12: 'OCD: Overcurrent Discharge',
        13: 'OCC: Overcurrent Charge',
        14: 'UV: Undervoltage',
        15: 'OV: Overvoltage',
    }

    def __init__(self, request_retries=3, logger=None):
        """

        :param request_retries: How often read requests should get repeated in case that they fail (Default: 3).
        :param logger: Python Logger object for output (Default: None)
        """
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
        self.request_retries = request_retries

    def connect(self, device):
        """
        Connect to a serial device

        :param device: Serial device, e.g. /dev/ttyUSB0
        """
        self.serial = serial.Serial(
            port=device,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.5,
            xonxoff=False,
            writeTimeout=0.5
        )

    def _format_message(self, command, length):
        message = "0a%s0%s" % (command.zfill(2), length)
        message_bytes = bytearray.fromhex(message)
        self.logger.debug("message: %s, %s" % (message_bytes, message_bytes.hex()))
        return message_bytes

    def _read(self, command):
        if not self.serial.isOpen():
            self.serial.open()
        if command in ("10", "11", "12"):
            length = 4
        else:
            length = 2
        message_bytes = self._format_message(command, length)

        # clear all buffers, in case something is left from a previous command that failed
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

        if not self.serial.write(message_bytes):
            self.logger.error("serial write failed for command" % command)
            return False

        response_data = self.serial.read(length + 1)
        if len(response_data) == 0:
            self.logger.debug("empty response for command %s" % (command))
            return False

        self.logger.debug("%s (%i)" % (response_data.hex(), len(response_data)))
        if command in ("10", "11", "12"):
            return struct.unpack('>i x', response_data)[0]
        elif command in ("15", "16", "17", "18"):
            return bin(int.from_bytes(response_data[:-1], byteorder='big'))[2:].zfill(16)
        else:
            return struct.unpack('>h x', response_data)[0]

    def get_cell_voltages(self):
        max_cells = 10
        x = 1
        cell_voltages = {}
        while x <= max_cells:
            response_data = self._read("%02x" % x)
            if not response_data:
                break
            if response_data == 0:
                # last cell
                break

            cell_voltages[x] = response_data / 1000
            x += 1

        return cell_voltages

    def _read_bulk(self, requests):
        data = {}
        for key, command in requests.items():
            response_data = self._read(command[0])
            if response_data is False:
                continue
            data[key] = response_data / command[1]

        return data

    def get_soc(self):
        requests = {
            "total_voltage": ("b", 1000),
            "current": ("10", 1000),
            "soc_percent": ("13", 1)
        }
        return self._read_bulk(requests)

    def get_temperatures(self):
        # The BMS returns temperatures in Kelvin
        # 2731 / 10 = 273,1 K = 0°C
        requests = {
            "external1": ("c", 10),
            "external2": ("d", 10),
            # "ic1": ("e", 10),
            # "ic2": ("f", 100), # always 71
        }
        responses = self._read_bulk(requests)

        for key, value in responses.items():
            # change temperatures from Kelvin to °C
            responses[key] = round(value-273, 2)
        return responses

    def get_status(self):
        requests = {
            "cycles": ("14", 1),
        }
        responses = self._read_bulk(requests)

        for key, value in responses.items():
            if type(responses[key]) is float:
                responses[key] = int(value)
        return responses

    def get_mosfet_status(self):
        requests = {
            "full_capacity_ah": ("11", 1000),
            "remaining_capacity_ah": ("12", 1000),
        }
        responses = self._read_bulk(requests)

        for key, value in responses.items():
            if type(responses[key]) is float:
                responses[key] = round(value, 2)

        pack_response = self._read("15")
        pack_state = []
        for key, value in self.PACK_STATUS.items():
            if pack_response[key] == "1":
                pack_state.append(value)

        responses['pack_state'] = pack_state
        return responses

    def get_errors(self):
        response = self._read("16")
        pack_state = []
        for key, value in self.BATTERY_STATUS.items():
            if response[key] == "1":
                pack_state.append(value)

        return pack_state

    # dummy functions for everything that is not supported by the Sinowealth BMS
    def get_cell_voltage_range(self):
        return {}

    def get_temperature_range(self):
        return {}

    def get_balancing_status(self):
        return {}

    def get_all(self):
        return {
            "soc": self.get_soc(),
            #"cell_voltage_range": self.get_cell_voltage_range(),
            #"temperature_range": self.get_temperature_range(),
            "mosfet_status": self.get_mosfet_status(),
            "status": self.get_status(),
            "cell_voltages": self.get_cell_voltages(),
            "temperatures": self.get_temperatures(),
            #"balancing_status": self.get_balancing_status(),
            "errors": self.get_errors()
        }
