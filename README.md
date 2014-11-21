python-htsp
===========

Tvheadend HTSP protocol wrapper for python

HTSP
----

See: <https://tvheadend.org/projects/tvheadend/wiki/Htsp>

Usage
-----

See example.py

Coverage
--------

### Client to Server (RPC) methods

+--------------------------+--------------------------------+
| hello                    | implemented                    |
+--------------------------+--------------------------------+
| authenticate             | implemented                    |
+--------------------------+--------------------------------+
| getDiskSpace             | implemented                    |
+--------------------------+--------------------------------+
| getSysTime               | implemented                    |
+--------------------------+--------------------------------+
| enableAsyncMetadata      | implemented                    |
+--------------------------+--------------------------------+
| getChannel               | implemented                    |
+--------------------------+--------------------------------+
| getEvent                 | not implemented                |
+--------------------------+--------------------------------+
| getEvents                | implemented                    |
+--------------------------+--------------------------------+
| epgQuery                 | not implemented                |
+--------------------------+--------------------------------+
| getEpgObject             | not documented by tvheadend    |
+--------------------------+--------------------------------+
| addDvrEntry              | pending                        |
+--------------------------+--------------------------------+
| updateDvrEntry           | pending                        |
+--------------------------+--------------------------------+
| cancelDvrEntry           | pending                        |
+--------------------------+--------------------------------+
| deleteDvrEntry           | pending                        |
+--------------------------+--------------------------------+
| getDvrCutpoints          | implementation not anticipated |
+--------------------------+--------------------------------+
| addAutorecEntry          | pending                        |
+--------------------------+--------------------------------+
| deleteAutorecEntry       | pending                        |
+--------------------------+--------------------------------+
| getTicket                | not implemented - beyond scope |
+--------------------------+--------------------------------+
| subscribe                | not implemented - beyond scope |
+--------------------------+--------------------------------+
| unsubscribe              | not implemented - beyond scope |
+--------------------------+--------------------------------+
| subscriptionChangeWeight | not implemented - beyond scope |
+--------------------------+--------------------------------+
| subscriptionSkip         | not implemented - beyond scope |
+--------------------------+--------------------------------+
| subscriptionSeek         | not implemented - beyond scope |
+--------------------------+--------------------------------+
| subscriptionSpeed        | not implemented - beyond scope |
+--------------------------+--------------------------------+
| subscriptionLive         | not implemented - beyond scope |
+--------------------------+--------------------------------+
| subscriptionFilterStream | not implemented - beyond scope |
+--------------------------+--------------------------------+
| getProfiles              | unknown                        |
+--------------------------+--------------------------------+
| getCodecs                | remove from tvheadend api      |
+--------------------------+--------------------------------+
| fileOpen                 | not implemented - beyond scope |
+--------------------------+--------------------------------+
| fileRead                 | not implemented - beyond scope |
+--------------------------+--------------------------------+
| fileClose                | not implemented - beyond scope |
+--------------------------+--------------------------------+
| fileStat                 | not implemented - beyond scope |
+--------------------------+--------------------------------+
| fileSeek                 | not implemented - beyond scope |
+--------------------------+--------------------------------+

 

### Server to Client methods

+----------------------+--------------------------------+
| channelAdd           | implemented                    |
+----------------------+--------------------------------+
| channelUpdate        | pending                        |
+----------------------+--------------------------------+
| channelDelete        | pending                        |
+----------------------+--------------------------------+
| tagAdd               | implemented                    |
+----------------------+--------------------------------+
| tagUpdate            | implemented                    |
+----------------------+--------------------------------+
| tagDelete            | pending                        |
+----------------------+--------------------------------+
| dvrEntryAdd          | implemented                    |
+----------------------+--------------------------------+
| dvrEntryUpdate       | pending                        |
+----------------------+--------------------------------+
| dvrEntryDelete       | pending                        |
+----------------------+--------------------------------+
| autorecEntryAdd      | implemented                    |
+----------------------+--------------------------------+
| autorecEntryUpdate   | pending                        |
+----------------------+--------------------------------+
| autorecEntryDelete   | pending                        |
+----------------------+--------------------------------+
| eventAdd             | implemented                    |
+----------------------+--------------------------------+
| eventUpdate          | pending                        |
+----------------------+--------------------------------+
| eventDelete          | pending                        |
+----------------------+--------------------------------+
| initialSyncCompleted | implemented                    |
+----------------------+--------------------------------+
| subscriptionStart    | not implemented - beyond scope |
+----------------------+--------------------------------+
| subscriptionGrace    | not implemented - beyond scope |
+----------------------+--------------------------------+
| subscriptionStop     | not implemented - beyond scope |
+----------------------+--------------------------------+
| subscriptionSkip     | not implemented - beyond scope |
+----------------------+--------------------------------+
| subscriptionSpeed    | not implemented - beyond scope |
+----------------------+--------------------------------+
| subscriptionStatus   | not implemented - beyond scope |
+----------------------+--------------------------------+
| queueStatus          | not implemented - beyond scope |
+----------------------+--------------------------------+
| signalStatus         | not implemented - beyond scope |
+----------------------+--------------------------------+
| timeshiftStatus      | not implemented - beyond scope |
+----------------------+--------------------------------+
| muxpkt               | not implemented - beyond scope |
+----------------------+--------------------------------+
