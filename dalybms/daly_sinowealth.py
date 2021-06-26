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

        if len(response_data) == 5:
            ctype = "i"
        else:
            ctype = "h"

        self.logger.debug("%s (%i)" % (response_data.hex(), len(response_data)))
        return struct.unpack('>%s x' % ctype, response_data)[0]

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
            responses[key] = value - 273
        return responses

    # dummy functions for everything that is not supported by the Sinowealth BMS
    def get_status(self):
        return {}

    def get_cell_voltage_range(self):
        return {}

    def get_temperature_range(self):
        return {}

    def get_mosfet_status(self):
        return {}

    def get_balancing_status(self):
        return {}

    def get_errors(self):
        return {}
