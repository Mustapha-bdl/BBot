import q,api,re,config
import bbot as BBot
import time,thread,sqlite3
dict=sqlite3.connect('bbot.sqlite3')
class module(api.module):
	commands=['help','goog','wiki','pb','upb','kb','hit','?<query>','add','del','writedict','load','reload','version','connect','py']
	goog_str='https://encrypted.google.com/search?q=%s'
	wiki='https://secure.wikimedia.org/wikipedia/en/wiki/%s'
	pb='http://www.pastebin.com/%s'
	upb='http://paste.ubuntu.com/%s'
	kb='http://www.kb.aj00200.heliohost.org/index.py?q=%s'
	def get_command_list(self):
		try:
			time.sleep(5)
			for module in BBot.networks[config.network]:
				for command in module.commands:
					self.command_list.append(command)
		except Exception,e:
			print 'Error: %s; with args: %s;'%(type(e),e.args)
	def __init__(self,server):
		self.command_list=[]
		thread.start_new_thread(self.get_command_list,())
		self.read_dict()
		self.info_bots=api.getConfigStr('BBot','infobots').split()
		self.ttl=api.getConfigInt('BBot','ttl')
		self.q=''
		self.funcs={
				'hit':self.hit,
				'version':self.version,
				'goog':self.goog
		}
		self.sufuncs={
				'join':self.su_join,
				'writedb':self.su_writedb,
				'raw':self.su_raw,
				'part':self.su_part,
				'add':self.su_add,
				'load':self.su_load,
				'reload':self.su_reload,
				'py':self.su_py,
				'connect':self.su_connect,
				'del':self.su_del
		}
		api.module.__init__(self,server)
	def __destroy__(self):
		self.notice(('#spam','<<BBot __destroyed__!>>'))
		dict.close()
	def go(self,nick,data,channel):
		if 'SG #' not in data: #Detect if the message is a PM
			channel=nick.lower()
		ldata=data.lower()
		if api.checkIfSuperUser(data,config.superusers):
			if ':'+config.cmd_char in data:
				command=data[data.find(':'+config.cmd_char)+len(config.cmd_char)+1:]
				if ' ' in command:
					command=command[:command.find(' ')]
				if command in self.sufuncs:
					self.sufuncs[command](nick,data,channel)
		if re.search(':'+config.mynick.lower()+'(:|,) ',ldata):
			self.q=ldata[ldata.find(':'+config.mynick.lower())+3+len(config.mynick):]
			self.query(self.q,nick,channel)
			return 0
		ldata=ldata.replace('whats','what is').replace('what\'s','what is')
		if re.search('(what|who|where) (is|was|are|am) ',ldata):
			self.ldata=ldata.replace(' was ',' is ')
			self.ldata=self.ldata.replace(' a ',' ')
			self.ldata=self.ldata.replace(' the ',' ')
			self.ldata=self.ldata.replace(' was ',' ')
			self.ldata=self.ldata.replace(' an ',' ')
			self.ldata=self.ldata.replace(' are ',' is ')
			self.ldata=self.ldata.replace(' am ',' is ')
			self.q=self.ldata[self.ldata.find(' is ')+4:].strip('?.\r\n:')
			self.query(self.q,nick,channel)
			return 0
		elif ':\x01VERSION\x01' in data:
			self.notice((nick,'\x01VERSION BBot Version %s\x01'%BBot.version))
		elif ':?' in data:
			if ':?help' in data and ':?help ' not in data:
				w=''
				for cmd in self.command_list:
					w+='%s, '%cmd
				self.append((nick,'%s: %s'%(nick,w[0:-2])))
				self.append((channel,'%s: Please see the PM I sent you'%nick))
			elif ':?wiki ' in data:
				w=data.split(':?wiki ')[-1].replace(' ','_')
				self.append((channel,self.wiki%w))
				return 0
			elif ':?pb ' in data:
				w=data.split(':?pb ')[-1]
				self.append((channel,self.pb%w))
				return 0
			elif ':?upb ' in data:
				w=data.split(':?upb ')[-1]
				self.append((channel,self.upb%w))
				return 0
			elif ':?kb 'in data:
				w=data[data.find(':?kb ')+5:]
				self.append((channel,self.kb%w))
				return 0
			self.q=data[data.find(':?')+2:]
			if ' ' in self.q:
				self.q2=self.q[:self.q.find(' ')]
			else:
				self.q2=self.q
			if self.q2 in self.funcs:
				self.funcs[self.q2](nick,data,channel)
			if ' > ' in self.q:
				if ' | ' not in self.q:
					self.nick=self.q.split(' > ')
					self.q=self.nick[0].lower()
					channel=self.nick[1]
					nick='From %s'%nick
				else:
					self.notice((nick,'All abuse is logged: %s'%data))
					return 1
			elif ' | ' in data:
				nick=self.q.split(' | ')
				self.q=nick[0].lower()
				nick=nick[1]
			if self.q[:self.q.find(' ')] not in self.command_list:
				self.query(self.q,nick,channel)
#		elif ':INFOBOT:' in data:
#			if ':INFOBOT:DUNNO' in data:
#				pass
#			elif ':INFOBOT:REPLY' in data:
#				if nick in self.info_bots:
#					self.infobot_parse_reply(data)
#			elif ':INFOBOT:QUERY' in data:
#				self.infobot_reply(data,nick)
#	def send_infobot_query(self,query,nick,channel):
#		message='INFOBOT:QUERY '+str(self.ttl)+'%'+nick+';'+channel+': '+query
#		if 'infobot:dunno' in query.lower(): #Prevents looping
#			return
#		for each in self.info_bots:
#			self.append((each,message))
#	def infobot_parse_reply(self,data):
#		if re.search('INFOBOT:REPLY (.)+ (.)+ = [a-zA-Z0-9]+',data):
#			self.notice(('#spam','REPLY received'))
#			if re.search('INFOBOT:REPLY [0-9]+%(.)+:',data):
#				self.notice(('#spam','Advanced Query'))
##/////////////////////-Advanced Infobot Reply-/////////////////////////
##INFOBOT:REPLY 20%aj00200;#spam:bot@net:bot2@net2 blah = blah
#				ib=data[data.find('REPLY ')+6:]
#				ib=ib[:ib.find(' ')]
#				ttl=int(ib[:ib.find('%')])-1
#				if ttl<0:
#					return
#				id=ib[ib.find('%')+1:ib.find(':')]
#				return_path=ib[ib.find(':')+1:]
#				return_path=return_path.split(':')
#				return_to=return_path.pop()
#				if return_to in return_path:
#					return #loop protection
#				return_path=':'.join(return_path)
#				#/////^Does not contain leading ://////
#				address=return_to.split('@')
#				query=data[data.find('INFOBOT:REPLY ')+14:].split()
#				#^1:query, 2: = 3:factoid
#				message='INFOBOT:REPLY '+str(ttl)+'%'+id+':'+return_path+' '+query[1]+' = '+query[3]
#				try:
#					self.notice(('#spam','Network is: %s'%address[1]))
#					q.append(address[1],(address[0],message))
#				except Exception,e:
#					self.notice(('#spam','BBot crashed with error %s and args %s'%(type(e),e.args)))
#			else:
#				qu=data[data.find('INFOBOT:REPLY ')+14:]				#5%aj00200;#bots hi = hello world
#				qu=qu[qu.find(' ')+1:].replace('<ACTION>','\x01ACTION ')
#				qu=qu.replace(config.mynick,'%n')							#
#				if '\x01' in qu:
#					qu+='\x01'
#					self.add_factoid(qu.split(' = ',1))    
#	def infobot_reply(self,query,sender):
#		qu=query[query.find('INFOBOT:QUERY ')+14:]
#		id=qu[:qu.find(' ')]
#		self.q=qu[qu.find(' ')+1:]
#		self.c.execute('''select * from factoids where key=?''',(self.q,))
#		found=self.c.fetchall()
#		if len(found)>0:
#			self.append((sender,'INFOBOT:REPLY %s %s = %s'%(id,self.q,found[0][1])))
#		else:
#			self.append((sender,'INFOBOT:DUNNO %s %s'%(id,self.q)))
	def add_factoid(self,query,nick):
		tmp=query
		if '<ACTION>'in query[1]:
			tmp[1]=str(tmp[1].replace('<ACTION>','\x01ACTION ')+'\x01')
		self.c.execute('delete from factoids where key=?',(str(tmp[0]),))
		self.c.execute('insert into factoids values (?,?,?,?)',(tmp[0],tmp[1],nick,time.time()))
	def del_factoid(self,query):
		self.c.execute('delete from factoids where key=?',(str(query),))
	def write_dict(self):
		dict.commit()
	def read_dict(self):
		self.c=dict.cursor()
		self.c.execute('''create table if not exists factoids (key, value, "by", ts)''')
		dict.commit()
	def query_dict(self,query):
		'''Primarily for the unittester	'''
		self.c=dict.cursor()
		self.c.execute('''select * from factoids where key=?''',(query,))
		results=self.c.fetchall()
		if len(results)>0:
			return results[0][1]
	def query(self,query,nick,channel):
		'''Querys the database for the factoid 'query', and returns its value to the channel if it is found'''
		self.c.execute('''select * from factoids where key=?''',(query.lower(),))
		results=self.c.fetchall()[:]
		if len(results)>0:
			self.append((channel,str(results[0][1]).replace('%n',nick)))
#		else:
#			self.send_infobot_query(query,nick,channel)
	#////////Single Functions/////////
	def hit(self,nick,data,channel):
		'''Causes BBot to punch someone'''
		who=data[data.find('hit ')+4:]
		self.append((channel,'\x01ACTION punches %s\x01'%who))
	def version(self,nick,data,channel):
		'''Sends BBot's version number to the channel'''
		self.append((channel,'I am version %s'%BBot.version))
	def goog(self,nick,data,channel):
		if 'goog ' in data:
			w=str(data[data.find('goog ')+5:].replace(' ','+'))
			self.append((channel,self.goog_str%w))
		return 0
	def su_join(self,nick,data,channel):
		'''Makes BBot join the channel which is the param'''
		self.raw('JOIN %s'%data[data.find('join ')+5:])
	def su_writedb(self,nick,data,channel):
		'''Writes the factoids database to the harddrive'''
		thread.start_new_thread(self.write_dict,())
		self.notice((channel,'<<Writing Database>>'))
	def su_raw(self,nick,data,channel):
		self.raw(data[data.find('raw ')+4:])
	def su_part(self,nick,data,channel):
		self.raw('PART %s'%data[data.find('part ')+5:])
	def su_add(self,nick,data,channel):
		query=data[data.find(' :')+2:]
		query=query[query.find('add ')+4:].split(':::')
		self.add_factoid(query,nick)
		self.notice((channel,'<<Added %s>>'%query))
	def su_load(self,nick,data,channel):
		self.q=data[data.find('load ')+5:]
		if BBot.load_module(self.q,self.__server__):
			self.notice(('#spam','<<Loaded %s>>'%self.q))
	def su_py(self,nick,data,channel):
		self.q=data[data.find('py ')+3:]
		try:
			ret=str(eval(self.q))
		except Exception,e:
			ret='<<Error %s; %s>>'%(type(e),e.args)
		self.append((channel,ret))
	def su_connect(self,nick,data,channel):
		tmp=data[data.find('connect ')+8:]
		self.notice((channel,'<<Connecting to %s>>'%tmp))
		BBot.add_network(tmp)
		q.connections[tmp]=q.connection(tmp)
	def su_reload(self,nick,data,channel):
		tmp=data[data.find('reload ')+7:]
		BBot.reload_module(tmp,self.__server__)
		self.notice((channel,'<<Reloaded %s>>'%tmp))
	def su_del(self,nick,data,channel):
		tmp=data[data.find('del ')+4:]
		self.del_factoid(tmp)
		self.notice((channel,'<<Delete %s>>'%tmp))