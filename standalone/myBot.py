from operator import itemgetter
import irc.client
import irc.bot
import os
import time
import sys
import string
import random
import sys
import irc.bot
import irc.buffer
import pdb
import ssl
import os
import time


class myBot(irc.bot.SingleServerIRCBot):
	"""
	Se connecte au serveur, fait un /LIST puis rejoins les canaux avec 
	plus de minusers de connectés.
	Une fois le bot connecté, tout les evenement sont enregistré dans 
	log_file et les message privés sont traité par self.process_private_msg
	et les commandes qu'ils contiennent sont exécutées.
	
	[start]
	on_welcome.
	on_list jusqu'à on_listend
	filterlist
	joinlist(	mise en place d'une répétion toute les 4 seconde jusqua connection
				avec tout les cannaux)
	on_all
	
	"""
	def __init__(self, server, admin, nickname= "", realname= "", password= "", minusers=0, outfile= None):
		if outfile == None : 
			self.log_file = self.openfile("./" + server[0][0] + "-log.txt")
		else:
			self.log_file = self.openfile(outfile)
		self.admin = admin
		self.minusers = minusers
		self.chanlist = []
		self.nickname = lambda: "".join([string.ascii_letters[random.randint(0,len(string.ascii_letters)-1)]for x in range(10)]) if nickname == "" else nickname
		self.realname = lambda: "".join([string.ascii_letters[random.randint(0,len(string.ascii_letters)-1)]for x in range(10)]) if realname == "" else realname
		self.password = lambda: "".join([string.ascii_letters[random.randint(0,len(string.ascii_letters)-1)]for x in range(10)]) if password == "" else paswword
		self.quit_msg = [	"""Ho i'm not gonna kill you, noo,"""
							"""i'm gonna hurt you sooo baad !""",
							"""you borred me so much, i'm gonna kill myself !""",
							""" Ho you kill me dude !""",
							"""don't kill me dude, i'am aliv...beep...beep..."""]				 
		irc.bot.SingleServerIRCBot.__init__(self,
			server, 
			self.nickname(),
			self.realname(), 
			connect_factory=irc.connection.Factory(wrapper=ssl.wrap_socket,ipv6=False))
			
		irc.client.ServerConnection.buffer_class = irc.buffer.LenientDecodingLineBuffer
		
	
	def on_welcome(self,serv, ev):
		""" 
		Connection au serveur :
			Le bot evois un message privé a l'administrateur
		"""
		serv.privmsg(self.admin," is online")
		serv.list()	# envoi d'une requette /list au serveur
		
	def on_list(self, serv, ev):
		"""
		Lors de la reception d'un evènement 'list' on récupère :
			le nom du canal, le nombre d'utilisateurs et la description
			et on ajoute ces 3 information a la liste des cannaux
		"""
		chan = [ev.arguments[0], int(ev.arguments[1]), ev.arguments[2]]
		self.chanlist.append(chan)
		print(chan[0] + ": " + str(chan[1]))
		
	def on_listend(self, serv, ev):
		"""
			Quand le serveur a finis de nous envoyer la liste des salon
			on appele la fonction filtre pour ne garder que ceux de plus
			de minusers utilisateur
			add_global_handler permet ensuite de rediriger tout les 
			événements vers la methode on_all
			et on fini par appeler la methode joinlist
		"""
		self.chanlist = self.filterlist(self.chanlist, self.minusers)
		self.connection.add_global_handler("all_events", self.on_all)
		self.joinlist(serv)			

	def joinlist(self, serv):
		"""
		Cette méthode est appelée une première fois par on_listend
		Si le nombre maximal de salon a été joins ou si il n'y a plus 
		de salon dans la liste de salon a joindre alors on quitte la
		methode.
		Sinon on retire le premier élément de la liste de salon pour
		le mettre dans chan. evois le nom du salon qui va etre joins
		a l'administrateur puis on rejoins le salon et on fini par mettre
		en place un appel a interval régulier de la fonction join
		"""
		if len(self.channels) < 120 and len(self.chanlist) > 0:
			chan = self.chanlist.pop()
			chan, users_number = (chan[0], chan[1])
			serv.privmsg(self.admin,chan + ": " + str(users_number))
			serv.join(chan)
			self.reactor.execute_delayed(4,self.joinlist,[serv])			
		
	def filterlist(self, chanlist,minusers):
		""" 
		on ajoute a tmp.end uniquement les salon avec plus de minuser
		et on retourne la liste trié
		
		"""
		tmp = []
		for chan in chanlist:
			if int(chan[1]) >= minusers :
				#print (chan[0] + ": " + str(chan[1]))
				tmp.append(chan)
		return sorted(tmp, key=itemgetter(1))
		
	def join_all(self,serv):
		"""
		Cette méthode est appelée pour traiter la commande !join_all
		on commence par effacer la liste de cannaux, puis on retire le
		dernier global_handler de la pile d'appel et du coup les évenements
		seront de nouveau dispatché dans les fonction par defaut
		on_événement
		puis pour finir on fait un /LIST
		a ce moment la on se retrouve dans la configuration de départ
		et le script va faire :
			on_list
			on_listend
			filterlist
			joinlist
			on_all
		"""
		self.chanlist = []
		self.reactor.remove_global_handler("all_events",self.on_all)
		serv.list()
		
	def write_log(self,ev):
		"""
		cette methode est appelé sur tout les évenement. elle prend skip
		tout les message du type 'all_raw_message' et enregistre les autres
		dans le fichier self.log_file
		de plus tout les message public sont redirigé sur la sortie standard.
		"""
		if ev.type !="all_raw_messages":
			msg = "{} {} ".format(time.time(),ev.type)
			if ev.source : msg += ev.source + " "
			if ev.target : msg += ev.target + " "
			if ev.arguments : msg += ev.arguments[0] + " "
			msg += '\n'
			nmS = irc.client.NickMask(ev.source)
			nmT = irc.client.NickMask(ev.target)
			
			if ev.type == "pubmsg": print(nmS.nick + " > " + nmT.nick + ":\n  " + ev.arguments[0]+"\n")
			
			if self.log_file != None : 
				self.log_file.write(msg)
				self.log_file.flush()
										
	def openfile(self,outfile):
		"""
		Ouvre le fichier outfile. Si le chemin n'existe pas l'arboréscence
		complètte est crée
		retourne le handle du fichier ouvert en mode append
		"""
		print(outfile)	
		path = "/".join(outfile.split('/')[:-1])
		if not os.path.exists(path):
			os.makedirs(path)
		return open(outfile,'a')
		
	def process_private_msg(self, serv, ev):
		"""
		Lorsqu'un message privé est reçu cette methode vérifie la source
		si c'est l'administrateur du bot alors la commande est traitée
		sinon le message est transmi a l'administrateur
		commande du bot :
		!die : deconnecte le bot
		!info : retourne le nombre de chan auquel est connecté le bot
		!msg nickname text: envoyer un msg a travers le bot
		!join #canal : rejoindre un canal
		!join_all miniusers : rejoin tout les canaux avec plus de minusers utilisateurs
		!part #canal : quiter un canal
		!part_all : quite tout les cannaux 
		
		"""
		nm = irc.client.NickMask(ev.source)
		if nm.nick == self.admin :
			if ev.arguments[0] == "!die":
				serv.privmsg(self.admin,self.quit_msg[random.randint(0,len(self.quit_msg)-1)])
				self.die()
			if ev.arguments[0] == "!info":
				msg = "i'm connected to {} chan(s).".format(len(self.channels))
				serv.privmsg(self.admin, msg)
			if ev.arguments[0][0:4] == "!msg":
				msg = ev.arguments[0].split(" ")
				if len(msg) < 3 : serv.privmsg(self.admin,"error : !msg [nick] [text]")
				else : serv.privmsg(msg[1],msg[2])
			if ev.arguments[0][0:5] == "!join":
				msg = ev.arguments[0].split("#")
				if len(msg) == 2: serv.join('#'+ msg[1])
				elif ev.arguments[0][0:9] == "!join_all":
					msg = ev.arguments[0].split(" ")
					try:
						self.minusers = int(msg[1])
						self.join_all(serv)
					except:
						serv.privmsg(self.admin,"Error: Can't join_all")
				else: serv.privmsg(self.admin, "Error: !join #channel or !join_all")
			if ev.arguments[0][0:5] == "!part":
				msg = ev.arguments[0].split("#")
				if len(msg) == 2: serv.part('#'+ msg[1])
				elif ev.arguments[0][0:9] == "!part_all":
					serv.part(self.channels)
				else : serv.privmsg(self.admin,"Error : !part [chan] or !part_all")
					
				
			
		else:
			serv.privmsg(self.admin,"{} say > {}".format(ev.source, ev.arguments[0]))
		
	def on_all(self, serv, ev):	
		#print("on_all")
		self.write_log(ev)
		
		if ev.type == "privmsg":
			self.process_private_msg(serv, ev)
		
					
def main():
	"""
	Récupère les arguments de la ligne de commandes et les passe a l'objet myBot
	argv[1] l'adresse du serveur
	argv[2] le port
	argv[3] le nombre minimal d'utilisateur sur les chan a joindre
	#argv[4] le chemin du fichier de sortie
	"""
	if len(sys.argv) < 5:
		print("command line error: [host] [port] [admin] /optional [minuser] [outfile]")
		return False

	if len(sys.argv) > 4:
		host = sys.argv[1]
		port = int(sys.argv[2])
		admin = sys.argv[3]
		minusers = int(sys.argv[4])
		outfile = False
		nickname = False
	
	if len(sys.argv) > 5:
		outfile = sys.argv[5]
		nickname = False
	
	#if len(sys.argv) > 6:
	#	nickname = sys.argv[6]

	#if nickname:
	#	bot = myBot([(host,port)],admin ,nickname= nickname, minusers= minusers,outfile= outfile)
	
	if outfile:
		bot = myBot([(host,port)],admin ,minusers= minusers,outfile= outfile)
		
	else:
		bot = myBot([(host,port)],admin ,minusers= minusers)

	bot.start()
	return True
			
if __name__ == "__main__":
	main()
		
