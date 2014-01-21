#!/usr/bin/python

###
#  Copyright (c) corbamico 01/2014 <corbamico@163.com>
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
#  


###
# GPL from gupload.py
# Copyright (c) David Lotton 01/2012 <yellow56@gmail.com>
#
# All rights reserved.
#
# License: GNU General Public License (GPL)
#
# THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM 
# 'AS IS' WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR 
# IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE 
# ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM 
# IS WITH YOU. SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME 
# THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
#
#
# Name: gupload.py
#
#   Brief:  gupload.py is a utility to upload Garmin fitness
#       GPS files to the connect.garmin.com web site.  
#       It requires that you have a user account on that
#       site.  See help (-h option) for more information.
###

# Make sure you have MultipartPostHandler.py in your path as well


def downloader():

	import gdownload
	import argparse
	import os
	import os.path
	import ConfigParser
	import logging
	import platform
	import string
	import sys

	out_directory = "./workouts"

	parser= argparse.ArgumentParser(
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description='A script to download .TCX files from the Garmin Connect web site.',
		epilog="""
		Output:
			The script will output files into ./workouts as filename({datetime}-{activityid}.tcx): 

		Credentials:
			Username and password credentials may be placed in a configuration file 
			located either in the current working directory, or in the user's home
			directory.  WARNING, THIS IS NOT SECURE. USE THIS OPTION AT YOUR OWN
			RISK.  Username and password are stored as clear text in a file
			format that is consistent with Microsoft (r) INI files. 
		
			The configuration file must contain a [Credentials] section containing 
			'username' and 'password' entries.

			The name of the config file for non-windows platforms is '.guploadrc'
			for windows platforms the config file is named 'gupload.ini'.


			Example \'.guploadrc\' (or \'gupload.ini\' for windows):
				[Credentials]
				username=<myusername>
				password=<mypassword>

			Replace <myusername> and <mypassword> above with your own login 
			credentials.

		Priority of credentials:
			Command line credentials take priority over config files, current 
			directory config file takes priority over a config file in the user's
			home directory.

		Examples:
			Upload file and set activty name:
				gupload.py -l myusername mypassword --download_all
		""")

	parser.add_argument('--download_all', action='store_true', required=True,help='Download activities from Garmin Connect.')
	parser.add_argument('-l', type=str, nargs=2, help='Garmin Connect login credentials \'-l username password\'')
	parser.add_argument('-v', type=int, nargs=1, default=[3], choices=[1, 2, 3, 4, 5] , help='Verbose - select level of verbosity. 1=DEBUG(most verbose), 2=INFO, 3=WARNING, 4=ERROR, 5= CRITICAL(least verbose). [default=3]')

	myargs = parser.parse_args()

	logging.basicConfig(level=(myargs.v[0]*10))

	if platform.system() == 'Windows':
		configFile='gupload.ini'
	else:
		configFile='.guploadrc'


	# ----Login Credentials for Garmin Connect----
	# If credentials are given on command line, use them.
	# If no credentials are given on command line, look in 
	# current directory for a .guploadrc file (or gupload.ini
	# for windows).  If no .guploadrc/gupload.ini file exists
	#  in the current directory look in the user's home directory.
	configCurrentDir=os.path.abspath(os.path.normpath('./' + configFile))
	configHomeDir=os.path.expanduser(os.path.normpath('~/' + configFile))


	if myargs.l:
		logging.debug('Using credentials from command line.')
		username=myargs.l[0]
		password=myargs.l[1]
	elif os.path.isfile(configCurrentDir):
		logging.debug('Using credentials from \'' + configCurrentDir + '\'.')
		config=ConfigParser.RawConfigParser()
		config.read(configCurrentDir)
		username=config.get('Credentials', 'username')
		password=config.get('Credentials', 'password')
	elif os.path.isfile(configHomeDir):
		logging.debug('Using credentials from \'' + configHomeDir + '\'.')
		config=ConfigParser.RawConfigParser()
		config.read(configHomeDir)
		username=config.get('Credentials', 'username')
		password=config.get('Credentials', 'password')
	else:
		cwd = os.path.abspath(os.path.normpath('./'))
		homepath = os.path.expanduser(os.path.normpath('~/'))
		logging.critical('\'' + configFile + '\' file does not exist in current directory (' + cwd + ') or home directory (' + homepath + ').  Use -l option.')
		exit(1)

	def obscurePassword(password):
		length=len(password)
		if length==1:
			return('*')
		elif length == 2:
			return(password[1] + '*')
		else:
			obscured=password[0]
			for letter in range(1, length-1):
				obscured=obscured+'*'
			obscured=obscured+password[length-1]
			return(obscured)

	yes = raw_input("Download All Activities from Garmin Connect\n[Download Garmin]Connect to Garmin Connect&Download all[Y|y]:")

	if yes != "Y" and yes != 'y' :
		exit(1)

	def print_screen_line(string):
		sys.stderr.write("\r")
		sys.stderr.write(string)

	# Check directory of output
	if os.path.isdir(out_directory):
		pass
	else:
		os.mkdir(out_directory)	
		
	logging.debug('Username: ' + username)
	logging.debug('Password: ' + obscurePassword(password))

	# Create object
	g = DownloadGarmin.DownloadGarmin()

	# LOGIN
	print_screen_line ("[Download Garmin]login trying...")
	if not g.login(username, password):
		logging.critical('LOGIN FAILED - please verify your login credentials')
		print_screen_line ("[Download Garmin]login failed.")
		exit(1)
	else:
		logging.info('Login Successful.')
		print_screen_line ("[Download Garmin]login OK.\n")

	# Download All
	counter = 0;
	print_screen_line ("[Download Garmin]try to get all activities id.")
	for activityid,time,tzinfo in g.get_workouts():
		counter += 1
		print_screen_line ("[Download Garmin]downloading file:(%d) total(%d)." %(counter, g.totalFound))
		g.download_activity(activityid,time,tzinfo,out_directory)

	exit()

if __name__ == '__main__':
	downloader()
