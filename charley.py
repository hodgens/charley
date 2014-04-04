# charley is a skype bot
# he will use a database of a chat history
# he will scan incoming messages
# periodically, he will respond to a message
# he will randomly choose a word in the incoming message, then get all matches from the database
# he will randomly choose several of them
# randomly chosen substrings from each will be taken and added together
# key phrases will be used to control the bot

import Skype4Py
import random
import sys

PERMISSIBLE_CHATS = [] # the list of chats it's okay to respond to
MESSAGES_TO_FETCH_PER_ROUND = 5 # how many messages do you query each time
PARSED_MESSAGES = [str(num) for num in range(MESSAGES_TO_FETCH_PER_ROUND)] # to store messages charley has already responded to
SPEECH_SETTINGS = {}
CHARLEY_RESPONSES = [str(num) for num in range(MESSAGES_TO_FETCH_PER_ROUND)]

# ok database interface works
import sqlite3, re
database = sys.argv[1]
conn = sqlite3.connect(database)
cursor = conn.cursor()

forbidden_words = ["a","an","the","he","she","it","you","in","out","is","to","for","there","here","where","why","what","how","that","this","some","many","few"]

charley_signal = re.compile("charley")
charley_control_flag = re.compile("!cc") # for controlling charley

apostrophe_search = re.compile("&apos;")

# i'm using a dict for the commands because if i start rolling these into a class i'll just end up rolling everything else into it too and end up with a god class
die_command = re.compile(r"!cc die")
sleep_command = re.compile(r"!cc sleep")
wakeup_command = re.compile(r"!cc wakeup")
commands = { 'die': die_command, 'sleep': sleep_command, 'wakeup': wakeup_command }

forbidden_strings = re.compile('http|gyazo|!cc|charley:')

def evaluate_rand_message(message):
	# check the message to make sure it doesn't contain funky stuff
	if forbidden_strings.search(str(message)):
		return 1
	else:
		return 0
		
def get_rand_message(chat_id,message_word_seed):
	# MAKE IT ONLY LOOK AT CHATS
	#WHERE [convo id is in parameter list]
	command_to_execute = 'SELECT body_xml FROM Messages WHERE body_xml LIKE "% ' + str(message_word_seed) + ' %" AND chatname="' +str(chat_id) +  '" ORDER BY RANDOM() LIMIT ' + str(MESSAGES_TO_FETCH_PER_ROUND) + ';'
	
	alternative_command_to_execute = 'SELECT body_xml FROM Messages WHERE body_xml LIKE "%' + str(message_word_seed) + '%" AND chatname="' +str(chat_id) +  '" ORDER BY RANDOM() LIMIT ' + str(MESSAGES_TO_FETCH_PER_ROUND) + ';'
	
	okay_flag = 0
	fail_flag = 0
	count = 0
	while okay_flag is 0:
		
		while fail_flag == 0:
			try:
				print "fetching line"
				line = cursor.execute(command_to_execute)
				result = line.fetchall()
				if result == []:
					print "searching for improper message"
					line = cursor.execute(alternative_command_to_execute)
					result = line.fetchall()
				fail_flag = 1
			except:
				print "something failed getting rand, " + str(count)
				count += 1
				continue
		print str(result)
		result = str(result[0][0])
		message_to_send =  str(result)
		validity_check = evaluate_rand_message(result)
		#print result
		if result is not None:
			if validity_check is 0:
				okay_flag = 1
		if okay_flag is 1:
			return message_to_send
		else:
			return None

def send_message_to_chat(message, chat):
	# make it do what it says
	for element in skype.Chats:
		if element.Name == chat:
			element.SendMessage(message)
			CHARLEY_RESPONSES.insert(0,message)
			del CHARLEY_RESPONSES[-1]
			#print CHARLEY_RESPONSES

def read_control_command(message):
	# reads the control signal
	# thanks! http://stackoverflow.com/questions/597476/how-to-concisely-cascade-through-multiple-regex-statements-in-python
	for key, pattern in commands:
		present_control = pattern.search(message)
		if present_control:
			#execute control statement
			break
	
def close_bot():
	conn.close()

def get_recent_messages():
	# i need to split this off so it returns the recent message list and the other stuff is a separate function
	failstate = 0
	count = 0
	while failstate == 0:
		try:
			recent_messages = cursor.execute('select  body_xml,chatname from Messages order by timestamp desc limit ' + str(MESSAGES_TO_FETCH_PER_ROUND) + ';'  )
			recent_message_list = recent_messages.fetchall()
			failstate = 1
			#print "messages retrieved"
		except:
			print "something went weird with getting messages, " + str(count)
			count += 1
			continue
	return recent_message_list

def choose_message_seed(message):
	word_list = re.split(" ",message)
	word_to_find = word_list[random.randint(0,len(word_list)-1)]
	return word_to_find

def charley_main(recent_message_list):
	for message in recent_message_list:
		message_text = str(message[0])
		#print message_text
		chatname = message[1]
		#print "checking for signal"
		if charley_signal.search(message_text, re.IGNORECASE):
			print "signal seen"
			#if SPEECH_SETTINGS[chatname] == 1:
			#if message_text not in PARSED_MESSAGES and message_text not in CHARLEY_RESPONSES: 
			#print message_text
			#print PARSED_MESSAGES
			if message_text not in PARSED_MESSAGES and message_text not in CHARLEY_RESPONSES: 
				print "new signal detected"
				first_word_to_find = choose_message_seed(message_text)
				second_word_to_find = choose_message_seed(message_text)
				third_word_to_find = choose_message_seed(message_text)
				ignore_count = 0
				while first_word_to_find in forbidden_words:
					print "it's a bad word, finding a new one"
					first_word_to_find = choose_message_seed(message_text)
					ignore_count += 1
					if ignore_count >= 20:
						print "ignoring this signal"
						first_word_to_find = "lol"
						break
				while second_word_to_find in forbidden_words:
					print "it's a bad word, finding a new one"
					second_word_to_find = choose_message_seed(message_text)
					ignore_count += 1
					if ignore_count >= 20:
						print "ignoring this signal"
						second_word_to_find = "lol"
						break
				while third_word_to_find in forbidden_words:
					print "it's a bad word, finding a new one"
					third_word_to_find = choose_message_seed(message_text)
					ignore_count += 1
					if ignore_count >= 20:
						print "ignoring this signal"
						third_word_to_find = "lol"
						break
				first_message_to_compose = get_rand_message(chatname, first_word_to_find) 
				second_message_to_compose = get_rand_message(chatname, second_word_to_find)
				third_message_to_compose = get_rand_message(chatname, third_word_to_find)
				try:
					first_message_to_compose = first_message_to_compose.split(" ")
				except:
					first_message_to_compose = "lol that didnt work".split(" ")
				try:
					second_message_to_compose = second_message_to_compose.split(" ")
				except:
					second_message_to_compose = "lol that didnt work".split(" ")
				try:
					third_message_to_compose = third_message_to_compose.split(" ")
				except:
					third_message_to_compose = "lol that didnt work".split(" ")
				message_to_send = " ".join(first_message_to_compose[0:int(round(len(first_message_to_compose)*1/3))])
				try:
					start_point = round(len(second_message_to_compose)*1/3)
					end_point = round(len(second_message_to_compose)*2/3)
					message_to_send += " " + " ".join(second_message_to_compose[start_point:end_point])
				except:
					print("second message good splitting failed")
					message_to_send += " " + " ".join(second_message_to_compose[2:5])
				try:
					message_to_send += " " + " ".join(third_message_to_compose[round(range(len(third_message_to_compose)*2/3)):len(third_message_to_compose)])
				except:
					print("third message good splitting failed")
					message_to_send += " " + " ".join(third_message_to_compose[-3:])
				
				message_to_send = apostrophe_search.sub("'",message_to_send)
				
				send_message_to_chat("charley: " + message_to_send, chatname)
				
				print("charley: " + message_to_send)
			else:
				print "ignoring signal"
				x=1
		if charley_control_flag.search(message_text, re.IGNORECASE):
			read_control_command(message_text)
		PARSED_MESSAGES.insert(0,message_text)
		del PARSED_MESSAGES[-1]

# now for the main loop
exit_status = 0
skype = Skype4Py.Skype()
skype.Attach()
print "it attached"
print "charley is running"

print "grabbing first messages"
first_messages = get_recent_messages()
for element_num in range(MESSAGES_TO_FETCH_PER_ROUND):
	PARSED_MESSAGES[element_num] = first_messages[element_num]
print "complete"
	
for elem in skype.Chats:
	SPEECH_SETTINGS[elem.Name] = 0

print "beginning loop"
while exit_status == 0:
	#print "fetching messages"
	message_list = get_recent_messages()
	charley_main(message_list)

close_bot()


#for elem in skype.Chats:
	##print(elem.Topic)
	#if elem.Topic == "Gibson Guitars http://puu.sh/64T0W.jpg http://bombch.us/S0k | Pudd http://bit.ly/191W1Gm Sock http://bit.ly/16SrhaQ Chev http://bit.ly/17ka0Kl | we ate a lot of taco bell and died |  http://bit.ly/Wou3wM":
	#	elem.SendMessage("charley: responses aren't online but i can write to the chat")
	#else:
	#	print("didn't work")



#for row in cursor.execute('SELECT body_xml  FROM Messages ORDER BY RANDOM() LIMIT 4;'):
	#print(row)


#reference pages 
#http://stackoverflow.com/questions/4536146/need-an-python-script-that-uses-skype4py-to-send-an-instant-message
#https://github.com/awahlig/skype4py/blob/master/examples/SkypeBot.py
#http://stackoverflow.com/questions/17176009/how-can-i-send-a-message-to-a-group-conversation-with-skype4py-in-python