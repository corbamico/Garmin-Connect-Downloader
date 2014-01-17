"""
Download Garmin

Handle the operation to download to the Garmin Connect Website.

"""
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#  
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the  nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  


# 
# This file is derived from orignal work by Chmouel Boudjnah <chmouel@chmouel.com>
# Original Source: https://github.com/chmouel/python-garmin-upload
#
# Modifications Copyright (c) David Lotton 01/2012
#
# License: BSD
#
# Modified 01/2012 by David Lotton to allow all upload file formats (tcx, fit, gpx)
# supported by connect.garmin.com.  Renamed all incorrectly named references to
# 'ctx' as 'tcx'. Corrected URI in original 'upload_tcx' function, adding the file
# type extension to the URI.
#
import os.path
try:
    import simplejson
except ImportError:
    import json as simplejson
import UploadGarmin

workout_url = "http://connect.garmin.com/proxy/activity-search-service-1.2/json/activities?activityType=running"

class DownloadGarmin(UploadGarmin.UploadGarmin):
#	def __init__(self):
#		super.__init__(self)
	
	def get_workouts(self):
		output = self.opener.open(workout_url)
		if output.code != 200:
			raise Exception("Error while downloading")
		json = output.read()
		output.close()
		activity = simplejson.loads(json)["results"]["activities"][0]
		return {activity["activity"]["activityId"],activity["activity"]["activitySummary"]["BeginTimestamp"]["value"]}
	
	
if __name__ == '__main__':
    g = DownloadGarmin()
    g.login("user", "name")
    print g.get_workouts()


"""
referennce:

import time
from datetime import datetime

def string_to_datetime(string, time_format="%Y-%m-%d %H:%M:%S"):
    #function to convert string to datetime
    return datetime.fromtimestamp(
        time.mktime(time.strptime(string, time_format))
    )



"""
