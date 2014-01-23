#!/usr/bin/python
#  ant-delete-runs.py
#  
#  Copyright 2014 corbamico <corbamico@163.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

# antd/main.py
# Copyright (c) 2012, Braiden Kindt.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
# 
#   2. Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS
# ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

def delete_runs():
    import antd
    import antd.ant as ant
    import antd.antfs as antfs
    import antd.hw as hw
    import antd.garmin as garmin
    import logging
    import sys
    import time
    import struct
    import argparse
    import os
    import dbm
    import shutil
    import lxml.etree as etree
    import sys

    Host = antfs.Host
    Beacon = antfs.Beacon
    Core = ant.Core
    Session = ant.Session
    Channel = ant.Channel
    Network = ant.Network
    Device = garmin.Device

    AntError = ant.AntError
    AntTimeoutError = ant.AntTimeoutError
    AntTxFailedError = ant.AntTxFailedError
    AntChannelClosedError = ant.AntChannelClosedError
    DeviceNotSupportedError = garmin.DeviceNotSupportedError    
    
    # command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", nargs=1, metavar="f",
            help="use provided configuration, defaults to ~/.antd/antd.cfg")
    parser.add_argument("--verbose", "-v", action="store_const", const=True,
            help="enable all debugging output, NOISY: see config file to selectively enable loggers")
    parser.add_argument("--force", "-f", required=True,action="store_const", const=True,
            help="force a connection with device for delete all runs.")
    args = parser.parse_args()
    
    # load configuration
    cfg = args.config[0] if args.config else None
    if not antd.cfg.read(cfg):
        print "unable to read config file." 
        parser.print_usage()
        sys.exit(1)
    
    # enable debug if -v used
    if args.verbose: antd.cfg.init_loggers(logging.DEBUG)
    _log = logging.getLogger("antd")
    yes = raw_input("Delete All Activities in Garmin Device\n[Delete Activitis]Delete All Activities in Garmin Device(eg.Forerunner 410)[Y|y]:")
    if yes != "Y" and yes != 'y' :
		exit(1)  
    
    # create an ANTFS host from configuration
    host = antd.cfg.create_antfs_host()
    try:
        failed_count = 0
        while failed_count <= antd.cfg.get_retry():
            try:
                _log.info("Searching for ANT devices.")
                # in daemon mode we do not attempt to pair with unkown devices
                # (it requires gps watch to wake up and would drain battery of
                # any un-paired devices in range.)
                beacon = host.search(include_unpaired_devices=True,
                                     include_devices_with_no_data=args.force)
                if beacon and (beacon.data_available or args.force):
                    _log.info("Device has data. Linking.")
                    host.link()
                    _log.info("Pairing with device.")
                    client_id = host.auth(pair=True)
                    
                    _log.info("Delete runs in device.")
                    dev = antd.Device(host)
                    dev.delete_runs()
                    
                    _log.info("Closing session.")
                    host.disconnect()
                    break

#                elif not args.daemon:
#                    _log.info("Found device, but no data available for download.")
#                if not args.daemon: break
#                failed_count = 0
            except antd.AntError:
                _log.warning("Caught error while communicating with device, will retry.", exc_info=True) 
                failed_count += 1
    finally:
        try: host.close()
        except Exception: _log.warning("Failed to cleanup resources on exist.", exc_info=True)
    
if __name__ == "__main__" :
    delete_runs()
# vim: ts=4 sts=4 et
