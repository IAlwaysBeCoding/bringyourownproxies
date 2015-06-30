import requests
import uuid

old_https_connection = requests.packages.urllib3.connection.HTTPSConnection
old_http_connection = requests.packages.urllib3.connection.HTTPConnection

old_http_connection_pool = requests.packages.urllib3.poolmanager.pool_classes_by_scheme['http']
old_https_connection_pool = requests.packages.urllib3.poolmanager.pool_classes_by_scheme['https']

class InjectorHTTPConnectionPool(old_http_connection_pool):

    def urlopen(self,method,url,**kwargs):
        headers = kwargs.pop('headers',{})
        headers['InjectorID'] = str(uuid.uuid4())
        return super(InjectorHTTPConnectionPool,self).urlopen(method,url,headers=headers,**kwargs)

class InjectorHTTPSConnectionPool(old_https_connection_pool):

    def urlopen(self,method,url,**kwargs):
        headers = kwargs.pop('headers',{})
        headers['InjectorID'] = str(uuid.uuid4())
        return super(InjectorHTTPSConnectionPool,self).urlopen(method,url,headers=headers,**kwargs)

class InjectorHTTPSConnection(old_https_connection):


    def endheaders(self,message_body=None):
        print 'buffer:{s}'.format(s=self._buffer)
        print message_body
        super(InjectorHTTPSConnection,self).endheaders(message_body=message_body)


class InjectorHTTPConnection(old_http_connection):

    def endheaders(self,message_body=None):
        print message_body
        print 'buffer:{s}'.format(s=self._buffer)
        super(InjectorHTTPConnection,self).endheaders(message_body=message_body)

requests.packages.urllib3.connectionpool.HTTPConnectionPool.ConnectionCls = InjectorHTTPConnection
requests.packages.urllib3.connectionpool.HTTPSConnectionPool.ConnectionCls = InjectorHTTPSConnection
requests.packages.urllib3.poolmanager.pool_classes_by_scheme['http'] = InjectorHTTPConnectionPool
requests.packages.urllib3.poolmanager.pool_classes_by_scheme['https'] = InjectorHTTPSConnectionPool
