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
import operator
import time
import os.path

from pytz import timezone
import pytz

import UploadGarmin

try:
    import simplejson
except ImportError:
    import json as simplejson
    

from datetime import datetime


workout_url = "http://connect.garmin.com/proxy/activity-search-service-1.2/json/activities?activityType=running"
page_url    = "http://connect.garmin.com/proxy/activity-search-service-1.2/json/activities?activityType=running&currentPage=%d"
tcx_url     = "http://connect.garmin.com/proxy/activity-service-1.2/tcx/activity/%d?full=true"


def generate_file_name(activityid,time,tzinfo):
	runtime = string_to_datetime(time).astimezone(timezone(tzinfo)).strftime("%Y%m%d%H%M")
	return "%s-%d.tcx" %(runtime,activityid) 

	
def string_to_datetime(string, time_format="%Y-%m-%dT%H:%M:%S.000Z"):
	#function to convert string to datetime
	#2014-01-09T21:31:40.000Z
	return datetime.strptime(string, time_format).replace(tzinfo=pytz.utc)
		
	

class DownloadGarmin(UploadGarmin.UploadGarmin):

	def get_current_page(self,currentPage):
		#print "[DownloadGarmin] Page %d Downloading " %currentPage

		output = self.opener.open( page_url % currentPage)
		if output.code != 200:
			raise Exception("Error while downloading current page %d" %currentPage)
		json = output.read()
		output.close()	
		
		activities = simplejson.loads(json)["results"]["activities"]	
		
		return map(lambda activity:\
						  (activity["activity"]["activityId"],\
						  activity["activity"]["activitySummary"]["BeginTimestamp"]["value"],
						  activity["activity"]["activityTimeZone"]["key"]),\
						  activities)
						  
						  	
	def get_workouts(self):
		output = self.opener.open(workout_url)
		if output.code != 200:
			raise Exception("Error while downloading")
		json = output.read()
		output.close()
		
		results = simplejson.loads(json)["results"]
		
		activities  = results["activities"]
		self.totalFound  = results["totalFound"]
		self.currentPage = results["currentPage"]
		self.totalPages  = results["totalPages"]
		
		#print "[DownloadGarmin] Activities %d ,Pages %d found" % (totalFound , totalPages)
		
		#Todo: Not so good, get first page twice,
		return reduce(operator.add, map(self.get_current_page,range(1,self.totalPages+1)))

		
	"""
	sample record as (427349739, u'2014-01-09T21:31:40.000Z', u'Asia/Hong_Kong')
	"""
	def download_activity(self,activityid,time,tzinfo,directory="./"):
		filename = generate_file_name(activityid,time,tzinfo)		
		filer = open(os.path.join(directory,filename),"w")
		
		#print "[DownloadGarmin] Downloading file(%s)" %filename
		
		output = self.opener.open(tcx_url % activityid)
		if output.code != 200:
			raise Exception("Error while downloading activity")
		
		filer.write(output.read())
		filer.close()
				
		
if __name__ == '__main__':
    g = DownloadGarmin()
    g.login("user", "pass")
    for activityid,time,tzinfo in g.get_workouts():
		g.download_activity(activityid,time,tzinfo,"./workouts")

