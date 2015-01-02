# Copyright (c) 2014 d.charlton (https://github.com/dpcharlton)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
# and associated documentation files (the "Software"), to deal in the Software without restriction, 
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial 
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT 
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Object oriented Tvheadend HTSP protocol wrapper for python"""

# Original example code at <https://github.com/tvheadend/tvheadend/blob/master/lib/py/tvh/htsp.py>

import datetime
import hashlib
import logging
import socket
import time

from tvh import htsmsg

HTSP_PROTO_VERSION = 17

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

_logger = logging.getLogger(__name__)
_logger.addHandler(NullHandler())


class ProtocolVersionException(Exception):
	"""Raised when an operation is requested that is not supported by the protocol version"""

class RequestError(Exception):
	"""Raised when an HTSP request fails"""	

class HTSPResponse(object):
	"""Base class for HTSPResponse classes"""
	def __init__(self,session,message):
		self._session=session
		self._message=message if message else {}

	# seq              int  optional   Sequence number. Same as in the request.
	@property
	def sequence(self):
		"""The response's sequence number"""
		return self._message.get('seq',None)

	# error            str  optional   If present an error has occurred and the text describes the error.
	@property
	def error(self):
		"""If present an error has occurred and the text describes the error"""
		return self._message.get('error',None)

	# noaccess         int  optional   If present and set to '1' the user is prohibited from invoking the method due to 
	#                                  access restrictions. 		
	@property
	def access_denied(self):
		"""True if the user is prohibited from invoking the method due to access restrictions"""
		return True if 'noaccess' in self._message and self._message['noaccess']==1 else False

	def _checkProtocol(self,required_version):
		self._session._checkProtocol(required_version)

	def _datetime_from_timestamp(self,timestamp):
		# TODO: Adjust for server timezone?
		return datetime.datetime.fromtimestamp(timestamp)

	def _timestamp_from_datetime(self,datetime):
		# TODO: Adjust for server timezone?
		return int(time.mktime(datetime.timetuple()))


class HTSPHello(HTSPResponse):
	"""Represents an HTSP 'hello' reply message"""
	def __init__(self,session,message):
		super(HTSPHello, self).__init__(session,message)

     # htspversion        u32   required   The server supports all versions of the protocol up to and including this number.
	@property
	def htspversion(self):
		"""The highest htsp protocol version supported by the server """
		return self._message['htspversion']

	# servername         str   required   Server software name.
	@property
	def servername(self):
		"""Server software name"""
		return self._message['servername']

	# serverversion      str   required   Server software version.
	@property
	def serverversion(self):
		"""Server software version"""
		return self._message['serverversion']

	# servercapability   str[] required   Server capabilities (Added in version 6)
	@property
	def servercapabilities(self):
		"""Server capabilities, as an array of strings"""
		self._checkProtocol(6)
		return self._message['servercapability']

	# challenge          bin   required   32 bytes randomized data used to generate authentication digests
	@property
	def challenge(self):
		"""32 bytes randomized challenge issued by the server"""
		return self._message['challenge']

	# webroot            str   optional   Server HTTP webroot (Added in version 8)
    #                    Note: any access to TVH webserver should include this at start of URL path
	@property
	def webroot(self):
		"""Server HTTP webroot"""
		self._checkProtocol(8)
		return self._message.get('webroot',None)


class HTSPDiskSpace(HTSPResponse):
	"""Represents an HTSP 'getDiskSpace' reply message"""
	def __init__(self,session,message):
		super(HTSPDiskSpace, self).__init__(session,message)

	# freediskspace      s64   required   Bytes available.
	@property
	def free_disk_space(self):
		"""Disk storage Bytes available"""
		return self._message['freediskspace']

	# totaldiskspace     s64   required   Total capacity.
	@property
	def total_disk_space(self):
		"""Disk storage Bytes total"""
		return self._message['totaldiskspace']

	@property
	def used_disk_space(self):
		"""Disk storage Bytes used"""
		return self.total_disk_space-self.free_disk_space


class HTSPSystemTime(HTSPResponse):
	"""Represents an HTSP 'getSysTime' reply message"""

	def __init__(self,session,message):
		super(HTSPSystemTime, self).__init__(session,message)

	# time               s64  required   UNIX time.
	@property
	def time(self):
		return self._message['time']

	# timezone           s32  required   Minutes west of GMT.
	@property
	def timezone(self):
		return self._message['timezone']

	@property
	def datetime(self):
		return self._datetime_from_timestamp(self.time)

class HTSPService(HTSPResponse):
	"""Represents an HTSP service"""

	# Note: HTSP gives limited information about services, the code
	# here attempts to infer additional information, but this is
	# based on incomplete and quite possibly incorrect knowledge
	# of tvheadend internals

	def __init__(self,session,message):
		super(HTSPService, self).__init__(session,message)

	@property
	def type(self):
		"""Get the type of the service (.g. SDTV)"""
		return self._message['type']

	@property
	def name(self):
		"""Get the full name of the service (e.g. Gloucestershire/530/BBC TWO)"""
		return self._message['name']

	@property
	def network(self):
		"""Get the network name of the service (e.g. Gloucestershire)"""
		# based on possibly dodgy assumptions
		try:
			parts=self._message['name'].split("/")		
			return parts[0]
		except:
			return None

	@property
	def mux(self):
		"""Get the multiplex name of the service (e.g. 530)"""
		# based on possibly dodgy assumptions
		try:
			parts=self._message['name'].split("/")		
			return parts[1]
		except:
			return None

	@property
	def resource(self):
		"""Get the resouce name of the service (e.g. Gloucestershire/530/)"""
		# based on possibly dodgy assumptions
		try:
			parts=self._message['name'].split("/")		
			return "/".join(parts[:2])
		except:
			return None



class HTSPChannel(HTSPResponse):
	"""Represents an HTSP 'channelAdd' reply message"""

	def __init__(self,session,message):
		super(HTSPChannel, self).__init__(session,message)


	# channelId          u32   required   ID of channel.
	@property
	def id(self):
		"""ID of channel"""
		return self._message['channelId']

	# channelNumber      u32   required   Channel number, 0 means unconfigured.
	@property
	def number(self):
		"""Channel number, 0 means unconfigured"""
		return self._message['channelNumber']

	# channelNumberMinor u32   optional   Minor channel number (Added in version 13).
	@property
	def minor_number(self):
		"""Minor channel number"""
		self._checkProtocol(13)
		return self._message.get('channelNumberMinor',0)

	# channelName        str   required   Name of channel.
	@property
	def name(self):
		"""Name of channel"""
		return self._message['channelName']

	# channelIcon        str   optional   URL to an icon representative for the channel
	#                                     (For v8+ clients this could be a relative /imagecache/ID URL
	#                                      intended to be fed to fileOpen() or HTTP server)
	#                                     (For v15+ clients this could be a relative imagecache/ID URL

	#                                      intended to be fed to fileOpen() or HTTP server)
	# eventId            u32   optional   ID of the current event on this channel.
	@property
	def now(self):
		"""Current event on this channel"""
		if 'eventId' in self._message:
			return self._session._get_event(self._message['eventId'])



	# nextEventId        u32   optional   ID of the next event on the channel.
	@property
	def next(self):
		"""Next event on the channel"""
		if 'nextEventId' in self._message:
			return self._session._get_event(self._message['nextEventId'])
	
	# tags               u32[] optional   Tags this channel is mapped to.
	@property
	def tags(self):
		"""Tags this channel is mapped to, as an array of HTSPTag instances"""
		result=[]
		for tag_id in self._message['tags']:
			tag=self._session._tags[tag_id]
			result.append(tag)

		return result
	
	# services           msg[] optional   List of available services (Added in version 5)
	@property
	def services(self):
		self._checkProtocol(5)
		messages=self._message['services']
		return map(lambda message:HTSPService(self,message),messages)


	@property
	def events(self):
		return self._session._get_events(self.id)

	def __str__(self):
		return "HTSPChannel: {0} {1}; now={2}; next={3}".format(self.number,self.name,self.now,self.next)


class HTSPTag(HTSPResponse):
	"""Represents an HTSP 'tagAdd' reply message"""

	def __init__(self,session,message):
		super(HTSPTag, self).__init__(session,message)


	# tagId              u32   required   ID of tag.
	@property
	def id(self):
		"""ID of tag"""
		return self._message['tagId']

	# tagName            str   required   Name of tag.
	@property
	def name(self):
		"""Name of tag"""
		return self._message['tagName']

	# tagIcon            str   optional   URL to an icon representative for the channel.
	# tagTitledIcon      u32   optional   Icon includes a title
	
	# members            u32[] optional   Channel IDs of those that belong to the tag
	@property
	def channels(self):
		"""Channel that belong to the tag"""
		if 'members' in self._message:
			return map(lambda channel_id:self._session._get_channel(channel_id),self._message['members'])

class HTSPDVREntry(HTSPResponse):
	"""Represents an HTSP 'dvrEntryAdd' reply message"""

	def __init__(self,session,message):
		super(HTSPDVREntry, self).__init__(session,message)

	# id                 u32   required   ID of dvrEntry.
	@property
	def id(self):
		"""ID of dvr entry"""
		return self._message['id']


	# channel            u32   required   Channel of dvrEntry.
	@property
	def channel(self):
		"""Channel of dvr entry"""
		return self._session._get_channel(self._message['channel'])

	@channel.setter
	def channel(self,value):
		self._message['channel']=value.id

	# start              s64   required   Time of when this entry was scheduled to start recording.
	@property
	def start(self):
		"""Start time of this entry"""
		return self._datetime_from_timestamp(self._message['start'])

	@start.setter
	def start(self,value):
		self._message['start']= self._timestamp_from_datetime(value)

	# stop               s64   required   Time of when this entry was scheduled to stop recording.
	@property
	def stop(self):
		"""End time of this entry"""
		return self._datetime_from_timestamp(self._message['stop'])

	@stop.setter
	def stop(self,value):
		self._message['stop']=self._timestamp_from_datetime(value)


	@property
	def duration(self):
		"""Duration of this entry"""
		return self.stop-self.start


	# startExtra         s64   required   Extra start time (pre-time) in minutes (Added in version 13).
	@property
	def start_extra(self):
		"""Extra start time (pre-time) in minutes"""
		self._checkProtocol(13)
		return self._message['startExtra']

	# stopExtra          s64   required   Extra stop time (post-time) in minutes (Added in version 13).
	@property
	def stop_extra(self):
		"""Extra stop time (post-time) in minutes"""
		self._checkProtocol(13)
		return self._message['stopExtra']

	# retention          s64   required   DVR Entry retention time in days.
	@property
	def retention(self):
		"""Retention of this entry"""
		return self._message['retention']


	# priority           u32   required   Priority (0 = Important, 1 = High, 2 = Normal, 3 = Low, 4 = Unimportant, 5 = Not set) (Added in version 13).
	
	# eventId            u32   optional   Associated EPG Event ID (Added in version 13).
	@property
	def event(self):
		"""Associated EPG Event"""
		self._checkProtocol(13)
		event_id=self._message.get('eventId',None)
		if event_id:
			return self._session._get_event(event_id)

	@event.setter
	def event(self,value):
		self._message['eventId']=value.id


	# autorecId          u32   optional   Associated Autorec ID (Added in version 13).
	# contentType        u32   optional   Content Type (like in the DVB standard) (Added in version 13).
	
	# title              str   optional   Title of recording
	@property
	def title(self):
		"""Title of entry"""
		return self._message.get('title',None)

	@title.setter
	def title(self,value):
		self._message['title']=value


	# summary            str   optional   Short description of the recording (Added in version 6).
	@property
	def summary(self):
		"""Short description of the recording"""
		self._checkProtocol(6)
		return self._message.get('summary',None)

	# description        str   optional   Long description of the recording.
	@property
	def description(self):
		"""Long description of the recording"""
		return self._message.get('description',None)


	# state              str   required   Recording state
	@property
	def state(self):
		""" Recording state"""
		return self._message.get('state',None)



	# error              str   optional   Plain english error description (e.g. "Aborted by user").

	def __str__(self):
		return "HTSPDVREntry: {0} {1}".format(self.title,self.state)

	def _as_cancel_dvr_entry_command(self):
		command={
			'id':self._message['id']
		}		
		return command

	def _as_add_dvr_entry_command(self):
		"""Map this HTSPDVREntry into a HTSP addDvrEntry request message """

		# -------------------------------------------------------------------
		# Note: There are inconsistencies between the HTSP dvrEntryAdd 
		# response message and the HTSP addDvrEntry request message.
		# Rather than have two separate classes for the response and request
		# we take the dvrEntryAdd reponse to bet he canonical version and
		# provide this method to convert to a request message
		# -------------------------------------------------------------------

		# eventId            u32   optional   Event ID (Optional since version 5).
		# channelId          u32   optional   Channel ID (Added in version 5)
		# start              s64   optional   Time to start recording (Added in version 5)
		# stop               s64   optional   Time to stop recording (Added in version 5)
		# retention          u32   optional   Retention time in days (Added in version 13)
		# creator            str   optional   Name of the event creator (Added in version 5)
		# priority           u32   optional   Recording priority (Added in version 5)
		# startExtra         s64   optional   Pre-recording buffer in minutes (Added in version 5)
		# stopExtra          s64   optional   Post-recording buffer in minutes (Added in version 5)
		# title              str   optional   Recording title, if no eventId (Added in version 6)
		# description        str   optional   Recording description, if no eventId (Added in version 5)
		# configName         str   optional   DVR configuration name or UUID		

		command={
			'retention' 	: self._message.get('retention',0),
			#'creator' 		: self._message.get('creator'),
			#'priority' 		: self._message.get('priority'),
			#'startExtra' 	: self._message.get('startExtra'),
			#'stopExtra' 	: self._message.get('stopExtra'),
			'title' 		: self._message.get('title'),
			#'description' 	: self._message.get('description'),
			#'configName' 	: self._message.get('configName'),
		}

		if 'eventId' in self._message:
			event=self._session._get_event(self._message.get('eventId'))
			command['eventId']=event.id
			if not 'title' in command or not command['title']:
				command['title']=event.title
		else:
			command['channelId']=self._message.get('channel')
			command['start']=self._message.get('start')
			command['stop']=self._message.get('stop')

		return command

class HTSPAutoRecordEntry(HTSPResponse):
	"""Represents an HTSP 'autorecEntryAdd ' reply message"""

	def __init__(self,session,message):
		super(HTSPAutoRecordEntry, self).__init__(session,message)

	# id                 str   required   ID (string!) of dvrAutorecEntry.
	@property
	def id(self):
		"""ID of this entry"""
		return self._message['id']


	# enabled            u32   required   If autorec entry is enabled (activated).
	@property
	def enabled(self):
		return self._message['enabled']


	# minDuration        u32   required   Minimal duration in seconds (0 = Any).
	# maxDuration        u32   required   Maximal duration in seconds (0 = Any).
	# retention          u32   required   Retention time (in days).

	@property
	def retention(self):
		"""Retention of this entry"""
		return self._message['retention']

	# daysOfWeek         u32   required   Bitmask - Days of week (0x01 = Monday, 0x40 = Sunday, 0x7f = Whole Week, 0 = Not set).
	
	# priority           u32   required   Priority (0 = Important, 1 = High, 2 = Normal, 3 = Low, 4 = Unimportant, 5 = Not set).
	@property
	def priority(self):
		return self._message['priority']

	

	# approxTime         u32   required   Minutes from midnight (up to 24*60).
	# startExtra         s64   required   Extra start minutes (pre-time).
	# stopExtra          s64   required   Extra stop minutes (post-time).
	
	# title              str   optional   Title.
	@property
	def title(self):
		return self._message['title']


	# channel            u32   optional   Channel ID.
	@property
	def channel(self):
		if 'channel' in self._message:
			return self._session._get_channel(self._message['channel'])
		return None

	def __str__(self):
		return "HTSPAutoRecordEntry: {0} ".format(self.title)


class HTSPEvent(HTSPResponse):
	"""Represents an HTSP 'eventAdd' reply message"""

	def __init__(self,session,message):
		super(HTSPEvent, self).__init__(session,message)

	# eventId            u32   required   Event ID
	@property
	def id(self):
		
		return self._message['eventId']

	# channelId          u32   required   The channel this event is related to.
	@property
	def channel(self):
		return self._session._get_channel(self._message['channelId'])

	# start              u64   required   Start time of event, UNIX time.
	@property
	def start(self):
		return self._datetime_from_timestamp(self._message['start'])

	# stop               u64   required   Ending time of event, UNIX time.
	@property
	def stop(self):
		return self._datetime_from_timestamp(self._message['stop'])

	@property
	def duration(self):
		"""Duration of this event"""
		return self.stop-self.start


	# title              str   optional   Title of event.
	@property
	def title(self):
		return self._message['title']

	# summary            str   optional   Short description of the event (Added in version 6).
	@property
	def summary(self):
		self._checkProtocol(6)
		return self._message['summary']

	# description        str   optional   Long description of the event.
	@property
	def description(self):
		return self._message.get('description',None)

	# serieslinkId       u32   optional   Series Link ID (Added in version 6).
	@property
	def series_link_id(self):
		self._checkProtocol(6)
		return self._message.get('serieslinkId',None)

	# episodeId          u32   optional   Episode ID (Added in version 6).
	@property
	def episode_id(self):
		self._checkProtocol(6)
		return self._message.get('episodeId',None)

	# seasonId           u32   optional   Season ID (Added in version 6).
	@property
	def season_id(self):
		self._checkProtocol(6)
		return self._message.get('seasonId',None)

	# brandId            u32   optional   Brand ID (Added in version 6).
	@property
	def brand_id(self):
		self._checkProtocol(6)
		return self._message.get('brandId',None)



	# contentType        u32   optional   DVB content code (Added in version 4, Modified in version 6*).
	# ageRating          u32   optional   Minimum age rating (Added in version 6).
	# starRating         u32   optional   Star rating (1-5) (Added in version 6).
	# firstAired         s64   optional   Original broadcast time, UNIX time (Added in version 6).
	# seasonNumber       u32   optional   Season number (Added in version 6).
	# seasonCount        u32   optional   Show season count (Added in version 6).
	# episodeNumber      u32   optional   Episode number (Added in version 6).
	# episodeCount       u32   optional   Season episode count (Added in version 6).
	# partNumber         u32   optional   Multi-part episode part number (Added in version 6).
	# partCount          u32   optional   Multi-part episode part count (Added in version 6).
	# episodeOnscreen    str   optional   Textual representation of episode number (Added in version 6).
	# image              str   optional   URL to a still capture from the episode (Added in version 6).
	
	# dvrId              u32   optional   ID of a recording (Added in version 5).
	@property
	def dvr_id(self):
		return self._message['dvrId']
	

	# nextEventId        u32   optional   ID of next event on the same channel.

	# not documented
	# episodeUri
	@property
	def episode_uri(self):
		return self._message.get('episodeUri',None)

	# serieslinkUri
	@property
	def series_link_uri(self):
		return self._message.get('serieslinkUri',None)

	def __str__(self):
		return "HTSPEvent: {0} {1}-{2} ({3})".format(self.title,self.start,self.stop.time(),self.duration)



class HTSPSession:
		
 	def __init__ (self, host='localhost',port=9982, addr=None,name = 'python-htsp' ):
 		if addr:
 			self._addr=addr
 		else:
			self._addr=(host,port)
			
		self._name = name
		self._sock = None

		self._auth = None
		self._user = None
		self._digest = None

		self._hello=None

		self._sequence=0
		self._command_pending=False

		self._initial_data=False
		self._tags={}
		self._channels={}
		self._events=None
		self._dvr_entries={}
		self._auto_record_entries={}

		self._callbacks=[]

	def hello (self):
		"""Issue an htsp 'hello' command to the server and return an HTSPHello response instance"""
		if not self._sock:
			self._sock = socket.create_connection(self._addr)

		message=self._invoke_command('hello', {
			'htspversion' : HTSP_PROTO_VERSION,
			'clientname'  : self._name
		})

		self._hello=HTSPHello(self,message)
		return self._hello

	def authenticate ( self, user, password = None ):
		
		self._check_connection()

		self._user = user
		if password:
			self._digest = HTSPSession._htsp_digest(user, password, self._hello.challenge)

		message=self._invoke_command('authenticate')
		response=HTSPResponse(self,message)
		if response.access_denied:
			raise Exception('Authentication failed')


	def fetch_initial_data(self,events=False):
		"""Issue an htsp 'enableAsyncMetadata' command to the server and collect the initial data"""
		

		self._events={} if events else None
		self._check_connection()		
		self._enable_async_metadata(events)
		while not self._initial_data:
			message = self._recv()
			self._handleMessage(message)


	@property
	def protocol_version(self):
		"""The highest htsp protocol version supported by the server"""
		
		self._check_connection()
		
		return self._hello.htspversion

	@property 
	def diskspace(self):
		"""Issue an htsp 'getDiskSpace' command to the server and return an HTSPDiskSpace response instance"""
		
		self._check_connection()

		self._checkProtocol(3)

		message=self._invoke_command('getDiskSpace')
		return HTSPDiskSpace(self,message)

	@property 
	def system_time(self):
		"""Issue an htsp 'getSysTime' command to the server and return an HTSPSystemTime response instance"""

		self._check_connection()

		self._checkProtocol(3)

		message=self._invoke_command('getSysTime')
		return HTSPSystemTime(self,message)

	@property
	def tags(self):
		"""The set of tags defined on the server, as an array of HTSPTag instances"""
		
		self._check_connection()

		if not self._initial_data:
			self.fetch_initial_data()

		return self._tags.values()


	@property
	def channels(self):
		"""The set of channels defined on the server, as an array of HTSPChannel instances"""
		
		if not self._initial_data:
			self.fetch_initial_data()

		return self._channels.values()

	@property
	def recorded(self):
		"""The set of recorded items on the server, as an array of HTSPDVREntry instances"""
		
		if not self._initial_data:
			self.fetch_initial_data()

		return filter(lambda entry:entry.state=='completed',self._dvr_entries.values())

	@property
	def scheduled(self):
		"""The set of scheduled items on the server, as an array of HTSPDVREntry instances"""
		
		if not self._initial_data:
			self.fetch_initial_data()

		return filter(lambda entry:entry.state=='scheduled' or entry.state=='recording',self._dvr_entries.values())


	@property
	def failed(self):
		"""The set of failed items on the server, as an array of HTSPDVREntry instances"""
		
		if not self._initial_data:
			self.fetch_initial_data()

		return filter(lambda entry:entry.state=='missed',self._dvr_entries.values())


	@property
	def auto_record_entries(self):
		"""The set of auto record items on the server, as an array of HTSPAutoRecordEntry instances"""
		
		if not self._initial_data:
			self.fetch_initial_data()

		return self._auto_record_entries.values()

	def create_dvr_entry(self):
		"""Create a new HTSPDVREntry instance"""
		return HTSPDVREntry(self,None)

	def add_dvr_entry(self,entry):
		"""Create a new DVR entry, wraps HTSP addDvrEntry"""
		message=self._invoke_command('addDvrEntry',entry._as_add_dvr_entry_command())
		HTSPSession._check_response(message)
		return self._dvr_entries[message["id"]]

	def cancel_dvr_entry(self,entry):
		"""Cancels a DVR entry, wraps HTSP cancelDvrEntry"""
		message=self._invoke_command('cancelDvrEntry',entry._as_cancel_dvr_entry_command())
		HTSPSession._check_response(message)
		return entry



	def monitor(self,callback):

		if not self._initial_data:
			self.fetch_initial_data()

		self._callbacks.append(callback)

		try:
			while True:
				message=self._recv()
				n=self._handleMessage(message)
				self._notify(message,n)
		except KeyboardInterrupt: 
			self._callbacks.remove(callback)
		except Exception as e:
			print e
			pass


	def _get_channel(self,channel_id):
		"""Get the channel with the given id, as an HTSPChannel instance"""

		if channel_id in self._channels.keys():
			return self._channels[channel_id]
		else:
			self._check_connection()
			self._checkProtocol(14)

			message=self._invoke_command('getChannel',{
				'channelId':int(channel_id)
				})

			return self._handle_channelAdd(message)

	def _get_events(self,channel_id):
		"""Get the list of events on the channel identified by channel_id"""

		self._checkProtocol(4)

		if self._events!=None:
			events=filter(lambda event:event.channel.id==channel_id,self._events)
		else:
			messages=self._invoke_command('getEvents',{
				'channelId':channel_id
				})

			events=map(lambda message:self._handle_eventAdd(message),messages['events'])

		return events

	def _get_event(self,event_id):
		"""Get the event with the given id, as an HTSPEvent instance"""

		if self._events!=None:
			event=self._events[event_id]
		else:
			message=self._invoke_command('getEvent',{
				'eventId':event_id
				})

			event=self._handle_eventAdd(message)

		return event


	def _check_connection(self):
		if not self._sock:
			self.hello()


	def _enable_async_metadata(self,events):
		_logger.info('Fetching initial data')
		self._invoke_command('enableAsyncMetadata',{
			'epg':1 if events else 0
			})


	def _invoke_command(self,method,args={}):

		_logger.debug('> {0}:{1}'.format(method,args))

		if self._command_pending:
			raise Exception("A command is already pending: {0}".format(method))

		self._command_pending=True

		args['seq']=self._sequence
		self._send(method,args)

		message=self._recv()
		_logger.debug('< {0}'.format(message))

		notify_queue=[]
		while not 'seq' in message:
			notify_queue.append(message)
			message=self._recv()

		if message['seq'] != self._sequence:
			raise Exception("Message out of sequence")

		self._sequence+=1

		self._command_pending=False

		for queued_message in notify_queue:
			n=self._handleMessage(queued_message)
			self._notify(queued_message,n)


		return message


	def _send ( self, method, args = {} ):
		args['method'] = method
		if self._user: 
			args['username'] = self._user
		if self._digest: 
			args['digest']   = htsmsg.hmf_bin(self._digest)
		self._sock.send(htsmsg.serialize(args))

	def _recv ( self ):
		return  htsmsg.deserialize(self._sock, False)

	def _checkProtocol(self,required_version):
		if (self.protocol_version<required_version):
			raise ProtocolVersionException("HTSP version %s required, but the server only supports version %s"%(required_version,self.protocol_version))

	def _handle_initialSyncCompleted(self,message):
		self._initial_data=True

	def _handle_tagAdd(self,message):
		tag=HTSPTag(self,message)
		self._tags[tag.id]=tag
		return tag

	def _handle_tagUpdate(self,message):
		new=HTSPTag(self,message)
		old=self._tags[new.id]
		HTSPSession._update_reponse(old,new)
		return old

	def _handle_channelAdd(self,message):
		channel=HTSPChannel(self,message)
		self._channels[channel.id]=channel
		return channel

	def _handle_channelUpdate(self,message):
		new =HTSPChannel(self,message)
		old=self._channels[new.id]
		HTSPSession._update_reponse(old,new)
		return old


	def _handle_eventAdd(self,message):
		event=HTSPEvent(self,message)
		if self._events!=None:
			self._events[event.id]=event
		return event

	def _handle_eventDelete(self,message):
		if self._events!=None:
			event=HTSPEvent(self,message)
			if event.id in self._events:
				return self._events.pop(event.id,None)
			else:
				_logger.warning("eventDelete rxed for an unknown event")	
		else:
			_logger.warning("eventDelete rxed but no event map")

	def _handle_dvrEntryAdd(self,message):
		entry=HTSPDVREntry(self,message)
		#print "_handle_dvrEntryAdd: id=%s"%(entry.id)
		self._dvr_entries[entry.id]=entry
		return entry

	def _handle_dvrEntryDelete(self,message):
		entry=HTSPDVREntry(self,message)
		if entry.id in self._dvr_entries:
			return self._dvr_entries.pop(entry.id,None)

	def _handle_dvrEntryUpdate(self,message):

		new=HTSPDVREntry(self,message)
		old=self._dvr_entries[new.id]
		HTSPSession._update_reponse(old,new)
		return old

	def  _handle_autorecEntryAdd(self,message):
		entry=HTSPAutoRecordEntry(self,message)
		self._auto_record_entries[entry.id]=entry
		return entry

	def _handle_autorecEntryUpdate(self,message):
		new=HTSPAutoRecordEntry(self,message)
		old=self._auto_record_entries[new.id]
		HTSPSession._update_reponse(old,new)
		return old

	def _handleMessage(self,message):
		if 'method' in message:
			method='_handle_'+message['method']
			if hasattr(HTSPSession,method):
				fn=getattr(HTSPSession,method)
				return fn(self,message)
			else:
				pass
				print "Not handled: %s: %s"%(method,message)

	@staticmethod
	def _htsp_digest ( user, passwd, chal ):
		return hashlib.sha1(passwd + chal).digest()

	@staticmethod
	def _update_reponse(old,new):
		for (key,value) in new._message.items():
			if value:
				#print "update key=%s old value=%s new value=%s"%(key,old._message[key] if key in old._message else "N/A",new._message[key])
				old._message[key]=new._message[key]

	@staticmethod
	def _check_response(message):
		if not message['success']:
			raise RequestError(message['error'])

	def _notify(self,message,notification):
		method=message['method']

		for callback in self._callbacks:
			callback(method,notification)
		


