#!/usr/bin/python
"""
import arrow 


from gevent import monkey; monkey.patch_all()
from gevent.greenlet import Greenlet
from gevent.event import AsyncResult 
import gevent
from errors import UnknownUploadEvent

class UploadEvent(AsyncResult):
    
    def __init__(self,upload):
        self.upload = upload
        self.date = None
        super(UploadEvent,self).__init__()
    
    def set(self,value):
        self.date = self._timestamp()
        super(UploadEvent,self).set(value=value)
        
        
    def _timestamp(self):
        now = arrow.utcnow()
        return now.timestamp

class Waiting(UploadEvent):
    pass

class Started(UploadEvent):
    pass

class Running(UploadEvent):
    pass

class UpdatingVideoSettings(Running):
    pass

class Stopped(UploadEvent):
    pass

class Finished(Stopped):
    pass

class Cancelled(Stopped):
    pass

class Failed(Stopped):
    pass


class Upload(Greenlet):
    

    def __init__(self,callbacks):
        pass
        #for callback_type = 
            
    '''       
    def _create_event(self,event_type):
        if event_type.upper() not in self.EVENTS:
            raise UnknownEvent('Unknown upload event')
        
        self.EVENTS[event_type.upper()](
    '''     
    
class PreparedUpload(object):
    
    EVENTS_KLAZZY = {'WAITING':Waiting,
                    'STARTED':Started,
                    'RUNNING':Running,
                    'STOPPED':Stopped,
                    'FINISHED':Finished,
                    'CANCELLED':Cancelled,
                    'FAILED':Failed}


def hey(*args,**kwargs):
    print 'args***'
    print args 
    print 'args***'
def bro(wtf,dfdf):
    print wtf 
    print dfdf
    print 'wtf'
    #raise Exception('dfddfdfdfdfd')
    return True
result = AsyncResult()
#result.set_exception(RuntimeError('failure'))
#result.set('sss')
t = gevent.spawn(bro,wtf='lol',dfdf='lol').link(hey)
print vars(result) 
gevent.sleep(1)
#print result.get(block=False)
"""