This is a Python module for reading data from Daly BMS devices. It supports serial as well as Bluetooth connections. Not all commands that the BMS supports are implemented yet, please take a look at the examples below to see if it serves your needs.

## Compatibility

There are two different types of devices sold under the Daly Brand, which use different communication protocols. 
This module was initially written for BMS supported by the Windows program BMS monitor.
Later (in #1) the support for BMS supported by the BMStool, also known as Sinowealth, was added. They don't support all commands of the first protocol, but still provide valuable information.

There are two ways to check if your BMS is supported:
1. First run `daly-bms-cli` normally and see if `--soc` returns data. If not, run it again while adding `--sinowealth`, which switches to the other protocol.
2. Connect the BMS to a Windows computer, run the PC tools provided by Daly ([Download](https://www.dalyelec.cn/newsshow.php?cid=25&id=77&lang=1)) and see which one works.

If you make it work with the Windows software, but not with `daly-bms-cli`, feel free to create a [bug report](https://github.com/dreadnought/python-daly-bms/issues).

## Installation

### From PyPI

```
pip3 install dalybms
```

### From Git

```
git clone https://github.com/dreadnought/python-daly-bms.git
cd python-daly-bms
sudo python3 setup.py install
```

### Dependencies

For *serial* connections:
```
pip3 install pyserial
```

For *bluetooth* connections:
```
pip3 install bleak
```

## CLI

`daly-bms-cli` is a reference implementation for this module, but can also be used to test the connection or use it in combination with other programming languages. The data gets returned in JSON format. It doesn't support Bluetooth connections yet.

### Usage
```
# daly-bms-cli --help
usage: daly-bms-cli [-h] -d DEVICE [--uart] [--sinowealth] [--status] [--soc] [--mosfet] [--cell-voltages] [--temperatures] [--balancing] [--errors] [--all] [--check] [--set-discharge-mosfet SET_DISCHARGE_MOSFET] [--retry RETRY] [--verbose] [--mqtt]
                    [--mqtt-hass] [--mqtt-topic MQTT_TOPIC] [--mqtt-broker MQTT_BROKER] [--mqtt-port MQTT_PORT] [--mqtt-user MQTT_USER] [--mqtt-password MQTT_PASSWORD]

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        RS485 device, e.g. /dev/ttyUSB0
  --uart                UART instead of RS485
  --sinowealth          BMS with Sinowealth chip
  --status              show status
  --soc                 show voltage, current, SOC
  --mosfet              show mosfet status
  --cell-voltages       show cell voltages
  --temperatures        show temperature sensor values
  --balancing           show cell balancing status
  --errors              show BMS errors
  --all                 show all
  --check               Nagios style check
  --set-discharge-mosfet SET_DISCHARGE_MOSFET
                        'on' or 'off'
  --retry RETRY         retry X times if the request fails, default 5
  --verbose             Verbose output
  --mqtt                Write output to MQTT
  --mqtt-hass           MQTT Home Assistant Mode
  --mqtt-topic MQTT_TOPIC
                        MQTT topic to write to. default daly_bms
  --mqtt-broker MQTT_BROKER
                        MQTT broker (server). default localhost
  --mqtt-port MQTT_PORT
                        MQTT port. default 1883
  --mqtt-user MQTT_USER
                        Username to authenticate MQTT with
  --mqtt-password MQTT_PASSWORD
                        Password to authenticate MQTT with
```

### Examples:

Get the State of Charge:
```
# daly-bms-cli  -d /dev/ttyUSB0 --soc
{
  "total_voltage": 57.7,
  "current": -11.1,
  "soc_percent": 99.1
}
```

Get everything possible:
```
# daly-bms-cli  -d /dev/ttyUSB0 --all
{
  "soc": {
    "total_voltage": 52.5,
    "current": 0.0,
    "soc_percent": 18.9
  },
  "cell_voltage_range": {
    "highest_voltage": 3.78,
    "highest_cell": 14,
    "lowest_voltage": 3.728,
    "lowest_cell": 1
  },
  "temperature_range": {
    "highest_temperature": 15,
    "highest_sensor": 1,
    "lowest_temperature": 15,
    "lowest_sensor": 1
  },
  "mosfet_status": {
    "mode": "stationary",
    "charging_mosfet": true,
    "discharging_mosfet": true,
    "capacity_ah": 5.67
  },
  "status": {
    "cells": 14,
    "temperature_sensors": 1,
    "charger_running": false,
    "load_running": false,
    "states": {
      "DI1": false,
      "DI2": true
    },
    "cycles": 21
  },
  "cell_voltages": {
    "1": 3.728,
    "2": 3.734,
    "3": 3.734,
    "4": 3.736,
    "5": 3.736,
    "6": 3.742,
    "7": 3.757,
    "8": 3.766,
    "9": 3.768,
    "10": 3.761,
    "11": 3.744,
    "12": 3.78,
    "13": 3.749,
    "14": 3.78
  },
  "temperatures": {
    "1": 15
  },
  "balancing_status": {
    "error": "not implemented"
  },
  "errors": [
    "SOC is too low. level one alarm"
  ]
}
```

## Notes

### Bluetooth

- It's also recommended to have a recent BlueZ installed (>=5.53).

  The Bluetooth connection uses `asyncio` for the connection, so the data is received asynchronous.  

- It seems like the Bluetooth BMS Module goes to sleep after 1 hour of inactivity (no load or charging), while the serial connection responds all the time. Sending a command via the serial interface wakes up the Bluetooth module.
