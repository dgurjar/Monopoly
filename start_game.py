import random
import options

def is_int(s):
# tests to see if a string is an integer, returns True if it is, False otherwise
	try:
		int(s)
		return True
	except ValueError:
		return False
		
def number_players():
# Function to determine number of players. First checks if number is in range(2,9)
# if it is, that's the number. If not, determines whether it is a number at all
# "Not a num..." or if it is too low "minimum 2..." or too high "maximum 8..."
# returns an integer between 2 and 8
	number_of_players = 'a'
	print "First things first: How many players to do we have today?\n"
	while number_of_players not in str(range(2,9)):
		number_of_players = raw_input('> ')
		while is_int(number_of_players) == False:
			print "\nThat's not a number, jabroni.\n\n" \
			"How many players will be playing today?"
			number_of_players = raw_input('> ')
		if int(number_of_players) < 2:
			print "\nYou need at least two players, ya bozo.\n\n" \
			"How many players will be playing today?"
		elif int(number_of_players) > 8:
			print "\nMaximum of 8 players in this game, chief.\n\n" \
			"How many players will be playing today?"
		if number_of_players in str(range(2,9)):
			return int(number_of_players)		

def name_gather(players, number_players):
# gathers the names of players and returns as an array. Does not append to master
# player table because random turn order hasn't been decided yet
	print "\n%i players! Excellent. Now we need to get your names." % int(number_players)
	player_name_array = []
	
	i=0
	# collect the number of names specified in number_players arg
	while i < number_players:
		print "\nPlayer %i, please enter your name: " %(i + 1)
		player_name = raw_input('> ')
		if len(player_name.replace(" ","")) > 0:
			# Ensure name isn't too long
			if len(player_name) > 15:
				print "\nName can't be more than 15 characters."
			
			# Ensure name doesn't have any commas or newlines in it
			# Commas and newlines will screw up file saving/loading
			elif player_name != player_name.replace(',','').replace('\\',''):
				print '\nName can not contain commas or backslashes.'
			
			elif player_name in player_name_array:
				print "\nYou must enter a unique name."
			else:
				player_name_array.append(player_name)
				i += 1
		else:
			print "\nYou can't have a blank name, doofus."
	print "\nGreat, so we have",
	for i in range(number_players - 1):
		print "%s," % player_name_array[i],
	print "and %s.\n\n" % player_name_array[number_players - 1]
	
	return player_name_array
	
def turn_order(players, names, number_players):
# Takes an array of strings (players names), draws random numbers to determine turn order
	order = range(number_players)
	print "Now we must decide the turn order via random drawing.\n\n" \
		"*boop boop beep dee boop* \n\nIt has been decided.\n"
	for i in range(number_players):
		drawing = random.randint(0,len(order) - 1)
		players.Create_Player(names[order[drawing]])
		del order[drawing]
		if i == 0:
			print "%s is rolling 1st." % players.name(i)
		elif i == 1:
			print "%s will be rolling after that." % players.name(i)
		elif i == 2:
			print "3rd will be %s." % players.name(i)
		else:
			print "%s will be rolling %ith." % (players.name(i), (i + 1))
	print ''
		
def new_or_load(pl_table, prop_table, cards, whose_turn):
	go = False
	while go == False:
		print "Enter 'New' to start a new game or 'Load' to load a game:\n"
		choice = raw_input('\n> ')
		if choice.lower() == "new":
			print '\n' * 50
			print '======================================================\n'
			print "Great! Let's get things started."
			# find valid integer for # of players
			number_of_players=number_players()
			# create 'name array' prior to drawing for turns
			name_array = name_gather(pl_table, number_of_players)
			print '======================================================\n'
			#randomly assign turn order and create players in players table
			turn_order(pl_table, name_array, number_of_players)
			go = True
		elif choice.lower() == 'load':
			go = options.load_game(pl_table, prop_table, cards, whose_turn)
	
		