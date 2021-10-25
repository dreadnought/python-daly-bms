#!/usr/bin/python3
import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="dalybms",
    version="0.3.0",
    description="Client for Daly BMS",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/dreadnought/python-daly-bms",
    author="Patrick Salecker",
    author_email="mail@salecker.org",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["dalybms"],
    scripts=["bin/daly-bms-cli"],
)
