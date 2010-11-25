backend=getattr(__import__('backends.async'),'async')
class module():
    def __init__(self,address):
        self.__address__=address
    def privmsg(self,nick,data,channel):
        '''Called every time a PRIVMSG is recieved'''
        print '* Go Message: (%s,%s,%s)'%(nick,data,channel)
    def append(self,channel,data=' '):
        print 'Use the NEW way to send things, msg(channel,data)'
    def msg(self,channel,data=' '):
        '''Send a message, data, to channel'''
        print 'PRIVMSG %s :%s'%(channel,data)
        backend.connections[self.__address__].push('PRIVMSG %s :%s\r\n'%(channel,data))
    def notice(self,channel,data):
        backend.connections[self.__address__].push('NOTICE %s :5s'%(channel,data))
    def get_notice(self,nick,data,channel):
        '''Called every time a notice is recieved'''
        pass
    def raw(self,data):
        print '%s'%(data)
        backend.connections[self.__address__].push('%s\r\n'%(data))
