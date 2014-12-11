#!/usr/bin/python

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

import datetime
import time

from python_htsp import htsp_session



session=htsp_session.HTSPSession('localhost',9982)


print "System Info"
print "-----------"

print "Protocol Version: %u"%(session.protocol_version)

diskspace=session.diskspace
print "Used : %d"%(diskspace.used_disk_space)
print "Free : %d"%(diskspace.free_disk_space)
print "Total: %d"%(diskspace.total_disk_space)

system_time=session.system_time
print "System Time : %s"%(system_time.datetime)

print
print "Tags"
print "----"

for tag in session.tags:
	print "%s: %s"%(tag.id,tag.name)

print
print "Channels"
print "--------"

for channel in sorted(session.channels,key=lambda channel:channel.number):
	print "%03d: %s"%(channel.number,channel.name)
	print "    services: %s"%(','.join(map(lambda service:"%s (%s)"%(service.name,service.type),channel.services)))
	print "        tags: %s"%(','.join(map(lambda tag:"%s (%s)"%(tag.name,tag.id),channel.tags)))

print
print "Recordings"
print "----------"

for entry in sorted(session.recorded,key=lambda entry:entry.start):
 	print "%s %-16s %s on %s (%s); retention %s"%(entry.start,entry.state,entry.title,entry.channel.name,entry.duration,entry.retention)

print
print "Scheduled"
print "---------"

for entry in sorted(session.scheduled,key=lambda entry:entry.start):
 	print "%s %-16s %s on %s (%s); retention %s; event %s"%(entry.start,entry.state,entry.title,entry.channel.name,entry.duration,entry.retention,entry.event.title if entry.event else None)

print
print "Auto Recordings"
print "---------------"

for entry in session.auto_record_entries:
 	print "%s on %s priority %d retention %d"%(entry.title,entry.channel.name if entry.channel else "N/A",entry.priority,entry.retention)

def handle_event(method,notification):
	print "Notified: %s; %s"%(method,notification)

print "Monitoring (^C to stop) ..."
session.monitor(handle_event)
