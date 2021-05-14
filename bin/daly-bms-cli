#!/usr/bin/python3
import argparse
import json
import logging
import sys

from dalybms import DalyBMS


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--device",
                    help="RS485 device, e.g. /dev/ttyUSB0",
                    type=str, required=True)

parser.add_argument("--status", help="show status", action="store_true")
parser.add_argument("--soc", help="show voltage, current, SOC", action="store_true")
parser.add_argument("--mosfet", help="show mosfet status", action="store_true")
parser.add_argument("--cell-voltages", help="show cell voltages", action="store_true")
parser.add_argument("--temperatures", help="show temperature sensor values", action="store_true")
parser.add_argument("--balancing", help="show cell balancing status", action="store_true")
parser.add_argument("--errors", help="show BMS errors", action="store_true")
parser.add_argument("--all", help="show all", action="store_true")
parser.add_argument("--check", help="Nagios style check", action="store_true")
parser.add_argument("--retry", help="retry X times if the request fails, default 5", type=int, default=5)
parser.add_argument("--verbose", help="Verbose output", action="store_true")

args = parser.parse_args()

log_format = '%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
if args.verbose:
    level = logging.DEBUG
else:
    level = logging.WARNING

logging.basicConfig(level=level, format=log_format, datefmt='%H:%M:%S')

logger = logging.getLogger()

bms = DalyBMS(request_retries=args.retry, logger=logger)
bms.connect(device=args.device)

result = False

def print_result(result):
    print(json.dumps(result, indent=2))

if args.status:
    result = bms.get_status()
    print_result(result)
if args.soc:
    result = bms.get_soc()
    print_result(result)
if args.mosfet:
    result = bms.get_mosfet_status()
    print_result(result)
if args.cell_voltages:
    if not args.status:
        bms.get_status()
    result = bms.get_cell_voltages()
    print_result(result)
if args.temperatures:
    result = bms.get_temperatures()
    print_result(result)
if args.balancing:
    result = bms.get_balancing_status()
    print_result(result)
if args.errors:
    result = bms.get_errors()
    print_result(result)
if args.all:
    result = bms.get_all()
    print_result(result)

if args.check:
    status = bms.get_status()
    status_code = 0  # OK
    status_codes = ('OK', 'WARNING', 'CRITICAL', 'UNKNOWN')
    status_line = ''

    data = bms.get_soc()
    perfdata = []
    if data:
        for key, value in data.items():
            perfdata.append('%s=%s' % (key, value))

    # todo: read errors

    if status_code == 0:
        status_line = '%0.1f volt, %0.1f amper' % (data['total_voltage'], data['current'])

    print("%s - %s | %s" % (status_codes[status_code], status_line, " ".join(perfdata)))
    sys.exit(status_code)

if not result:
    sys.exit(1)