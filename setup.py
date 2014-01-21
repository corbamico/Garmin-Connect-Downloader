#!/usr/bin/env python

from setuptools import setup

setup(
    name = "gdownload",
    version = "0.1.1",
    author = "corbamico",
    author_email = "corbamico@163.com",
    description = "Tools for download activities from Garmin Connect.",
    url = "http://github.com/corbamico/Garmin-Connect-Downloader",
    license = "GPL",
    keywords = "Garmin Connect",
    packages = ["gdownload"],
    entry_points = {
        'console_scripts': ['gdownload = gdownload.main:downloader']
    },
    install_requires = [
        "GcpUpLoader"
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License (GPL)"
    ]
)

