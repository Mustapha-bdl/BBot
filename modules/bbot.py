import q
import api
import config
class bbot():
	def __init__(self):
		self.read_dict()
		self.q=''
	#database=sqlite3.connect('newdatabase.sql')
	def go(self,nick,data,channel):
		if channel.find('#')==-1:#Detect if the message is a PM to the Bot
			channel=nick.lower()
		ldata=data.lower()
		if api.checkIfSuperUser(data,config.superusers):
			if ldata.find('raw ')!=-1:
				q.queue.raw(data.split('raw ')[-1])
			elif ldata.find('leave')!=-1:
				words=ldata.split('leave ')
				irc.send('PART %s' % words)
			elif ldata.find('?add ')!=-1:
				self.q=ldata[ldata.find('?add ')+5:].strip('\r\n')
				self.q=self.q.split(':::')
				self.add_factoid(self.q)
			elif ldata.find('?writedict')!=-1:
				self.write_dict()
		if ldata.find(':'+config.mynick.lower()+': ')!=-1:
			self.q=ldata[ldata.find(':'+config.mynick.lower()+': ')+3+len(config.mynick):].strip('\r\n')
			print self.q
			if self.q in self.static:
				q.queue.append((channel,self.static[self.q]))
		if data.find(':?')!=-1:
			print 'q: %s'%self.q
			self.q=data[data.find(':?')+2:].strip('\r\n')
			if self.q in self.static:
				q.queue.append((channel,nick+': '+self.static[self.q]))
			elif data.find(':?hit ')!=-1:
				words=data.split(':?hit ')[-1].strip('\r\n')
				if words.lower().find(config.mynick.lower())!=-1 or words.lower()=='aj00200':
					words=nick
				q.queue.append((channel,u'\x01ACTION kicks %s\x01'%words))
	def add_factoid(self,query):
		self.static[query[0]]=query[1]
	def del_factoid(self,query):
		if quey in self.static:
			del elf.static[query]
	def write_dict(self):
		self.dict=open('bbot/dict','w')
		for each in self.static:
			self.dict.write('%s:::%s\n'%(each,self.static[each]))
		self.dict.close()
	def read_dict(self):
		self.static={}
		self.dict=open('bbot/dict','r')
		for line in self.dict.readlines():
			self.q=line.split(':::')
			self.static[self.q[0]]=self.q[1]
		self.dict.close()