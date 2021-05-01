# python-daly-bms

This is a Python module for reading data from Daly BMS devices. It supports serial as well as Bluetooth connections. Not all commands that the BMS supports are implemented yet, please take a look at the examples below to see if it serves your needs.

## CLI

`./daly-bms-cli.py` is a reference implementation for this module, but can also be used to test the connection or use it in combination with other programming languages. The data gets returned in JSON format. It doesn't support Bluetooth connections yet.

### Usage
```
# ./daly-bms-cli.py --help
usage: daly-bms-cli.py [-h] -d DEVICE [--status] [--soc] [--cell-voltages]
                       [--all] [--check] [--retry RETRY] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        RS485 device, e.g. /dev/ttyUSB0
  --status              show status
  --soc                 show state of charge
  --cell-voltages       show cell voltages
  --all                 show all
  --check               Nagios style check
  --retry RETRY         retry X times if the request fails, default 5
  --verbose             Verbose output
```

### Examples:

Get the State of Charge:
```
# ./daly-bms-cli.py  -d /dev/ttyUSB0 --soc
{
  "total_voltage": 57.7,
  "current": -11.1,
  "soc_percent": 99.1
}
```

Get everything possible:
```
# ./daly-bms-cli.py  -d /dev/ttyUSB0 --all
{
  "soc": {
    "total_voltage": 57.7,
    "current": -12.0,
    "soc_percent": 99.1
  },
  "cell_voltage_range": {
    "highest_voltage": 4.172,
    "highest_cell": 6,
    "lowest_voltage": 4.061,
    "lowest_cell": 14
  },
  "temperature_range": {
    "highest_temperature": 17,
    "highest_sensor": 1,
    "lowest_temperature": 17,
    "lowest_sensor": 1
  },
  "mosfet_status": {
    "error": "not implemented"
  },
  "status": {
    "cells": 14,
    "temperature_sensors": true,
    "charger_running": false,
    "load_running": false,
    "states": {
      "DI1": false,
      "DI2": true
    },
    "cycles": 21
  },
  "cell_voltages": {
    "1": 4.085,
    "2": 4.122,
    "3": 4.12,
    "4": 4.17,
    "5": 4.146,
    "6": 4.171,
    "7": 4.154,
    "8": 4.141,
    "9": 4.17,
    "10": 4.087,
    "11": 4.094,
    "12": 4.068,
    "13": 4.115,
    "14": 4.061
  },
  "temperatures": {
    "error": "not implemented"
  },
  "balancing_status": {
    "error": "not implemented"
  },
  "errors": {
    "error": "not implemented"
  }
}
```

## Notes

### Bluetooth

Of Bluetooth connections you need to have `bleak` installed. It's also recommended to have a recent BlueZ installed (>=5.53).

```
pip3 install bleak
```
