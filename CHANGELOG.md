# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

-

### Fixed

-

## [0.5.0] - 2024-01-24

### Added

-  Add charge mosfet switch and restart action (#45)

### Fixed

- MQTT adjustments for voltage and capacity (#38)

## [0.4.0] - 2022-12-30

### Added

- Add `set_soc` command (#35)

### Fixed

- Don't crash if the Pack Status response is empty
- Call serial.close() before exiting
- Correct error messages of Sinowealth BMS (resolves #34)

## [0.3.0] - 2021-10-25

### Added

- Added `--set-discharge-mosfet` parameter to turn the mosfet on and off (#3)
- Added cycle count to `--status` for Sinowealth BMS 
- Implemented `--all` for Sinowealth BMS
- Added MQTT support (#13)
- Implemented capacity, pack status, errors commands for Sinowealth BMS (#14)

### Fixed

- Fixed cell voltage command for 3S BMS (#5)

## [0.2.0] - 2021-06-28

### Added

- Support for 3S-4S Daly BMS with Sinowealth chip (#2)
- Added `--uart` parameter for using UART instead of RS485 interfaces

## [0.1.0] - 2021-05-14

### Added

- Initial support for Daly BMS devices