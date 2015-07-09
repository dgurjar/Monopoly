import property
import player_table
import cards
import os
import start_game

def options_menu(pl_table, prop_table, cards, whose_turn):
	print '\n' * 50
	choice = 'i'
	print '\n======================================================\n'
	print 'Welcome to the options menu! '
	while choice.lower() != 'menu':
		print '\nPlease select an option: \
		\n1. View Player Status\n2. View Unowned Properties\
		\n3. Save Game\n4. Load Game\n\nType "Menu" to return to main menu.\n'
		
		choice = raw_input('> ')
		if choice == '1':
			player_status(pl_table,prop_table)
		elif choice == '2':
			unowned_properties(prop_table)
		elif choice == '3':
			save_game(pl_table, prop_table, cards, whose_turn)
		elif choice == '4':
			load_game(pl_table, prop_table, cards, whose_turn)
		print '\n' * 50, '======================================================'
		
		
def player_status(pl_table,prop_table):
	print "\n======================================================\n"
	
	choice = 'i'
	while choice.lower() != 'menu':
		# Print list of players. If player isn't in game , ***ELIMINATED*** appears
		# next to their name.
		print "Please enter a number to view player status.\
				\nType Menu to return to options menu.\n"
		for i in range(pl_table.table_length):
			print str(i + 1) + '.', pl_table.name(i),
			if not pl_table.in_game(i):
				print '***ELIMINATED***',
			print ''
		choice = raw_input('\n> ').replace(' ','')
		# This takes ANY choice, even for players not in game.
		# If they aren't in game, a message is printed
		if choice in str(range(1,pl_table.table_length+1)):
			print '\n' * 50, '======================================================\n'
			if pl_table.in_game(int(choice)-1):
				pl_id = int(choice) - 1
				pl_name = pl_table.name(pl_id)
				pl_location = prop_table.get_value(pl_table.location(pl_id), 'name')
				pl_cash = pl_table.cash(pl_id)
				pl_get_out_of_jail = pl_table.get_out_of_jail(pl_id)
				pl_properties = prop_table.player_properties(pl_id)
				
				# print player information
				print '%s has $%d in cash, and is currently at %s.'\
					% (pl_name,pl_cash,pl_location)
				if pl_get_out_of_jail:
					print "%s has %d 'Get Out of Jail Free' card" \
						% (pl_name, pl_get_out_of_jail)
				if len(pl_properties) == 0:
				# if player owns no property
					print "\n%s does not own any property." % (pl_name)
				else:
					print "\nHere is a list of properties owned by %s.\n" % (pl_name)
					# print headers for property table
					print ' ' * (25-len('property name')), 'Property Name', \
					' ' * (8 - len('houses')), 'Houses', \
					' ' * (11 - len('Mortgaged')), 'Mortgaged'
					for i in len(pl_properties):
						prop_id = pl_properties[i][0]
						prop_name = prop_table.get_value(prop_id, 'name')
						if prop_table.get_value(prop_id, 'houses') == 5:
							# If 5 houses (aka hotel), use 'hotel' instead of value
							prop_houses = 'HOTEL'
						else:
							prop_houses = str(prop_table.get_value(prop_id, 'houses'))
						if prop_table.get_value(prop_id, 'mortgage'):
							prop_mortgage = 'Yes'
						else:
							prop_mortgage = 'No'
						print ' ' * (2 - len(str(i+1))), str(i + 1) + '.',\
						' ' * (23-len(prop_name)), prop_name, \
						' ' * (8 - len(prop_houses)), prop_houses, \
						' ' * (11 - len(prop_mortgage)), prop_mortgage
						
				
			else:
				# if player isn't in game
				print "%s has been eliminated from the game.\n" % pl_table.name(int(i-1))
			raw_input('Press Enter to return to Player Status menu.\n')
			
	

def unowned_properties(prop_table):
	print '\n======================================================\n'
	# Prints properties owned by bank. Also prints cost, color, and mortgage status
	bank_owned = prop_table.player_properties(9)
	print 'Here is a list of the properties currently owned by the bank:\n'
	# Print headers
	print ' ' * (26 - len('Property Name')), 'Property Name',\
	' ' * (11 - len('color')), 'Color', ' ' * (6 - len('cost')), 'Cost',\
	' ' * (11 - len('mortgaged')), 'Mortgaged'
	for i in range(len(bank_owned)):
		# go through list of bank properties one row at a time
		prop_id = bank_owned[i][0]
		prop_name = prop_table.get_value(prop_id, "name")
		prop_color = prop_table.get_value(prop_id, "color")
		if prop_table.get_value(prop_id, "mortgage"):
		# IF MORTGAGED, COST IS CUT IN HALF
			prop_mortgaged = 'Yes'
			prop_cost = '$' + str(prop_table.get_value(prop_id, "cost")/2)
		else:
			prop_mortgaged = 'No'
			prop_cost = '$' + str(prop_table.get_value(prop_id, "cost"))
		# Print row	
		print ' ' * (2  - len(str(i + 1))), str(i+1)+ '.', ' ' * (21 - len(prop_name)), prop_name,\
	' ' * (11 - len(prop_color)), prop_color, ' ' * (6 - len(prop_cost)), prop_cost,\
	' ' * (11 - len(prop_mortgaged)), prop_mortgaged
	
	raw_input('\nPress Enter to continue.')
	
def save_game(pl_table, prop_table, cards, whose_turn):
	# Saves all game data into a file
	save_folder_contents = os.listdir((os.getcwd() + "\saves"))
	choice = 'i'
	while choice.lower() != 'menu':
		print '\nPlease enter a name to save this game as.\
				\nType Menu to go back to Options Menu'
		# Compare entry vs. entry with illegal characters removed.
		# If they are NOT equal, user has entered illegal characters
		choice = raw_input('> ')
		if choice != choice.replace('<','').replace('>','').replace(':','')\
		.replace('"','').replace('/','').replace('\\','').replace('|','')\
		.replace('?','').replace('*',''):
			print '\nThe following characters are not allowed: < > : " / \\ | ? *\
			\nPlease enter a valid game name.\n'
		elif len(choice.replace(' ','')) == 0:
			# Make sure they didn't enter all space characters
			print '\nName can not be blank. Please enter a valid name.\n.'
		else:
			if choice in save_folder_contents:
				# Ensure the name they entered doesn't match any files already in
				# the save folder
				print "\nThat file already exists. Please enter a different name."
			elif choice.lower() != 'menu' :
				# Write file as a .csv
				pl_data = pl_table.data
				prop_data = prop_table.all_property_data()
				community_data = cards.all_cards("community")
				chance_data = cards.all_cards("chance")
				turn = whose_turn
				file_name = os.getcwd() + "\saves\\" + choice + '.txt'
				file1 = open(file_name, 'w')
				
				# Ititerate through each item in every table/database.
				# Insert comma after each item, \n after each line
				print 
				for item in range(len(pl_data)):
					# Only iterate through the 2nd to last item with commas,
					# We will insert the last item on its own without trailing comma.
					for i in range(len(pl_data[item])-1):
						file1.write('%s,' % pl_data[item][i])
						
					# Insert last item without comma
					file1.write('%s' % pl_data[item][len(pl_data[item])-1])
					file1.write('\n')
					
				# the 'END*****' lines will help us during reading.
				file1.write('ENDPLAYER\n')
				
				# Write property data
				for item in range(len(prop_data)):
					for i in range(len(prop_data[item]) - 1):
						file1.write('%s,' % str(prop_data[item][i]))
					file1.write('%s' % str(prop_data[item][len(prop_data[item])-1]))
					file1.write('\n')
				file1.write('ENDPROPERTY\n')
				
				# Write community chest data
				for item in range(len(community_data) - 1):
					file1.write('%s,' % str(community_data[item][5]).replace('\n',''))
				file1.write('%s' % str(community_data[len(community_data) - 1][5]))
				file1.write('\n')
				file1.write('ENDCOMMUNITY\n')
				
				# Write chance data
				for item in range(len(chance_data) - 1):
					file1.write('%s,' % str(chance_data[item][5]))
				file1.write('%s' % str(chance_data[len(chance_data)-1][5]))
				file1.write('\n')
				file1.write('ENDCHANCE\n')
				
				#Write whose turn it is
				file1.write('%d\n' % turn)
				#File always ends with 'ENDFILE'
				file1.write('ENDFILE')
				#Close file so changes are committed
				file1.close()
				raw_input('\nFile saved successfully. Press Enter to return.\n')
				choice = 'menu'
			
def load_game(pl_table, prop_table, cards, whose_turn):
	choice = 'i'
	successful_load = False
	while choice.lower() != 'menu':
		file_location = os.getcwd() + "\saves\\"
		save_folder_contents = os.listdir((os.getcwd() + "\saves"))
		if len(save_folder_contents) == 0:
			# If saves folder is empty
			print "\nNo saved games available."
		else:
			# Print list of saved games. Remove .txt extension
			print '\nHere is the list of saved games: '
			for i in range(len(save_folder_contents)):
				print str(i + 1) + '.', save_folder_contents[i].replace('.txt','')
			print "\nEnter number to load game. To go back, type 'Menu'."
			choice = raw_input('\n> ')
			
			# Ensure the input matches a file name in the folder
			if choice in str(range(1,len(save_folder_contents)+1)):
				file_name = os.getcwd() + "\saves\\" + save_folder_contents[int(choice)-1]
				file1 = open(file_name, 'r')
				lines = file1.readlines()
				 
				#Clear data from player table
				pl_table.clear_data()
				 
				# Load data for player_table
				i = 0
				while str(lines[i]) != 'ENDPLAYER\n':
					pl_table.load_game(lines[i])
					i += 1
				i += 1
				
				# Clear property table data
				prop_table.clear_data()
				while str(lines[i]) != 'ENDPROPERTY\n':
					prop_table.load_game(lines[i].replace('\n',''))
					i += 1
				i += 1
				
				# Since only one column (drawn) changes in chance + community
				# chest, we will not delete the table. Instead, we provide a list
				# of 1s and 0s and set draw status.
				while str(lines[i]) != 'ENDCOMMUNITY\n':
					cards.load_game('community',lines[i].replace('\n',''))
					i += 1
				i += 1
				
				# Do the same thing with chance that we did with community
				while str(lines[i]) != 'ENDCHANCE\n':
					cards.load_game('chance',lines[i].replace('\n',''))
					i += 1
				i += 1
				
				# Read whose turn it is, set value
				whose_turn = int(lines[i].replace('\n',''))
				
				print 'Load complete. Press enter to continue.'
				raw_input()
				choice = 'menu'
				successful_load = True
			else:
				raw_input ("\nFile not found. Press Enter to continue: \n")
	# Return True if load is successful - else return False
	return successful_load		
			
