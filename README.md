# myBot
a simple irc scrypt. the scypt conect to a server then do a /list and use result to conect to.

Usage : python3 myBot.py [hostname] [port] [your_nick_name] [minuser] [outfile_path]
  hostanme : irc server adress , ex : irc.freenode.net
  port : the irc server port, ex : 6697
  you_nick_name : Obvious ;) only this nickname can manadge the bot 

OPTIONAL:
  minuser : the bot not go on channel with have less users than minuser, ex : 200
  outfile_path : the file name where the log will be saved.

admin command : 
to stop the scrypt: /msg botnickname !die 
to know how many chan is connected to the bot : /msg botnickname !info

Je ne serais pas contre une petite correction de mon franglais ;)
