#!/usr/bin/python3
from pprint import pprint
from dalybms import DalyBMS
import argparse
import json
import logging

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--device",
                    help="RS485 device, e.g. /dev/ttyUSB0",
                    type=str, required=True)

parser.add_argument("--status", help="show status", action="store_true")
parser.add_argument("--soc", help="show state of charge", action="store_true")
parser.add_argument("--cell-voltages", help="show cell voltages", action="store_true")
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

if args.status:
    result = bms.get_status()
    print(json.dumps(result, indent=2))
if args.soc:
    result = bms.get_soc()
    print(json.dumps(result, indent=2))
if args.cell_voltages:
    if not args.status:
        bms.get_status()
    result = bms.get_cell_voltages()
    print(json.dumps(result, indent=2))
if args.all:
    result = bms.get_all()
    print(json.dumps(result, indent=2))
