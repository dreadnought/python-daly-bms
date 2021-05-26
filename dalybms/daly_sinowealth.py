import serial
import struct
import logging

class DalyBMSSinowealth:
    def __init__(self, request_retries=3,  logger=None):
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

    def _format_message(self, command):
        message = "0a%s02" % command.zfill(2)
        message_bytes = bytearray.fromhex(message)
        self.logger.debug("message: %s, %s" % (message_bytes, message_bytes.hex()))
        return message_bytes

    def _read(self, command):
        if not self.serial.isOpen():
            self.serial.open()
        message_bytes = self._format_message(command)

        # clear all buffers, in case something is left from a previous command that failed
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

        if not self.serial.write(message_bytes):
            self.logger.error("serial write failed for command" % command)
            return False

        response_data = self.serial.read(3)
        if len(response_data) == 0:
            self.logger.debug("empty response for command %s" % (command))
            return False

        self.logger.debug("%s %i" % (response_data.hex(), len(response_data)))
        return struct.unpack('>H x', response_data)[0]

    def get_cell_voltages(self):
        max_cells = 11
        x = 1
        cell_voltages = {}
        while x < max_cells:
            response_data = self._read("%02x" % x)
            if not response_data:
                break
            if response_data == 0:
                # last cell
                break

            cell_voltages[x] = response_data / 1000

            x += 1

        return cell_voltages

    def get_soc(self):
        response_data = self._read("b")
        if not response_data:
            return False
        return {
            "total_voltage": response_data / 1000
        }

    def get_status(self):
        return {}



