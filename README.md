# myBot
a simple irc scrypt. the scypt conect to a server then do a /list and use result to conect to.

Usage : python3 myBot.py [hostname] [port] [your_nick_name] [minuser] [outfile_path]
  hostanme : irc server adress , ex : irc.freenode.net
  port : the irc server port, ex : 6697
  you_nick_name : Obvious ;) only this nickname can manadge the bot 

OPTIONAL:
  minuser : the bot not go on channel with have less users than minuser, ex : 200
  outfile_path : the file name where the log will be saved.
  
	commande du bot :
	!die : deconnecte le bot
	!info : retourne le nombre de chan auquel est connecté le bot
	!msg nickname text: envoyer un msg a travers le bot
	!join #canal : rejoindre un canal
	!join_all miniusers : rejoin tout les canaux avec plus de minusers utilisateurs
	!part #canal : quiter un canal
	!part_all : quite tout les cannaux 
