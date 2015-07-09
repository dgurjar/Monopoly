import random

import property
import player_table
import cards


# Covers most of the functions that occur in the flow of a single turn

def roll():
	# Roll dice. returns a tuple length 3 - first two elements are dice values,
	# 3rd element is whether or not doubles have been rolled
	die_1 = random.randint(1,6)
	die_2 = random.randint(1,6)
	doubles = False
	if die_1 == die_2:
		doubles = True
	return ([die_1, die_2, doubles])
	
def location_action(pl_table, prop_table, card_table, player_id, dice_value):
	# Takes player's current location and performs action.
	# Depending on space type, sends to appropriate function
	space = pl_table.location(player_id)
	space_type = prop_table.get_value(space, "type")
	if space_type == "prop":
		property_action(pl_table,prop_table,player_id,space, dice_value)
	elif space_type == "community" or space_type == "chance":
		card_table.draw_card(pl_table, prop_table, space_type, player_id, dice_value)
	elif (space_type == "go" or space_type == "jail" or space_type == "free"):
		nothing_action(prop_table,space)
	elif space_type == "goto":
		goto_jail_action(pl_table,player_id, dice_value)
	elif space_type == "inco":
		income_tax_action(pl_table,prop_table,player_id)
	elif space_type == "luxu":
		luxury_tax_action(pl_table, prop_table, player_id)
	else:
		print "This is an error. 'type' value in property table isn't recognized"
		
def property_action(pl_table,prop_table,player_id, space_id, dice_value):
	# Action for own-able properties
	# If owned by player who landed on it, they don't pay rent
	if prop_table.get_value(space_id, "owner") != 9:
		owner = prop_table.get_value(space_id, "owner")
		if owner == player_id:
			print "You own this property! Enjoy your free stay."
		else:
			# Pay rent to player. Calls rent_amount fn from property table
			rent_owed = prop_table.rent_amount(space_id,dice_value)
			print "This property is owned by %s. Pay $%d in rent." % (pl_table.name(owner), rent_owed)
			pl_table.money_transfer(prop_table, player_id, -rent_owed, owner)
	else:
		# Property is unowned. Gives player option to buy from bank.
		property_cost = prop_table.get_value(space_id, "cost")
		if prop_table.get_value(space_id, "mortgage") == 1:
			#If prop is mortgaged, cost is half
			property_cost = property_cost / 2
			print "This property is mortgaged and owned by the bank."
		print "This property is unowned. It costs $%s." % (property_cost)
		if property_cost > pl_table.cash(player_id):
			# Player doesn't have enough cash to buy property
			print "You do not have enough cash to purchase this property."
		else:
			# If player has enough cash to purchase, gives them option
			print "You have $%d. Would you like to purchase it?" % (pl_table.cash(player_id))
			option = ''
			while option.lower() not in ['yes','no']:  
				print '\n======================================================'
				option = raw_input('\nPlease enter Yes or No\n> ')
			if option.lower() == 'yes':
				# If purchased, changes owner in prop table to player, takes money from player
				# equal to property cost.
				print "\nYou are now the proud owner of %s!" % (prop_table.get_value(space_id, "name"))
				pl_table.money_transfer(prop_table, player_id, -property_cost, 9)
				prop_table.set_value(space_id, "owner", player_id)
			else:
				print "\nOkay, this property remains unowned and available for purchase"
	
def nothing_action(prop_table,property_id):
	# For corner spaces (not go to jail) where nothing happens
	print "You are visiting %s. Nothing happens." % (prop_table.get_value(property_id, "name"))

def goto_jail_action(pl_table,player_id, dice_value):
	# Sends player to jail, changes doubles to False
	pl_table.location(player_id, -20)
	print "\nYou are now in Jail. Do not pass go, do not collect $200"
	pl_table.in_jail(player_id,True)
	dice_value[2] = False
	
def income_tax_action(pl_table, prop_table, player_id):
	# Income tax: pay %10 or $200.
	print "Income tax. You must choose to pay 10% of your total net worth or $200"
	option = ''
	while option not in ['1','2']:  
		print "\n1. 10% of total net worth (cash, plus 1/2 value of houses, hotels, and unmortgaged property)\n2. $200"
		option = raw_input('\nPlease enter 1 or 2"\n> ')
	if option == '1':
		# Finds player's total liquidation value + cash, takes 10 percent of that (rounded down)
		tot_assets = prop_table.liquidate_player(player_id) + pl_table.cash(player_id)
		amount = tot_assets / 10
		print "\nYour total assets are $%d. You owe $%d to the bank" % (tot_assets, amount)
		pl_table.money_transfer(prop_table,player_id,-amount,9)
	else:
		# Player pays $200 to bank
		print "\n%s, pay $200 to the bank." % pl_table.name(player_id)
		
def luxury_tax_action(pl_table, prop_table, player_id):
	# Action if player lands on luxury tax. They pay $75 to bank
	print "Luxury tax. Pay $75 to the bank."
	pl_table.money_transfer(prop_table,player_id,-75,9)
	
	
def look_ahead(pl_table, prop_table, player_id):
	# Takes player's current position and prints a table of the next 12 spaces.
	# Includes spaces_away, prop_name, rent, and owner
	
	print '\n======================================================\n'
	print 'Here are the spaces you can land on in your next roll:\n'
	
	# Take player's current position as reference point
	pl_location = pl_table.location(player_id)
	#print headers
	print '\nSpaces Away', ' ' * (21 - len('Property Name')), 'Property Name', \
			' ' * (10 - len('rent')), 'Rent', ' ' * (16 - len('Owner')), 'Owner'
	# Loop through and print values. If owner is bank, replace with 'BANK'
	# If non-ownable property (chance, etc), leave owner blank
	# If owned by bank or mortgaged, rent is 0. If unownable, blank. 
	# Otherwise, rent is rent amount.
	for i in range(1,13):
		prop_name = prop_table.get_value(pl_location + i, "name")
		owner_value = prop_table.get_value(pl_location + i, "owner")
		# Assign positive rent value ONLY IF ownable AND owned by player (not bank)
		if owner_value == 9:
			rent = '$0'
			owner = 'BANK'
		elif owner_value == -1:
			rent = ' '
			owner = ' '
		# go through 'else' if owned by a player in game
		else:
			owner = pl_table.name(owner_value)
			if prop_table.get_value(pl_location + i, "mortgage"):
				# print 'Mortgage' if mortgaged
				rent = 'Mortgage'
			# exception for utilities
			elif prop_table.get_value(pl_location + i, "color") == 'Utility':
				if prop_table.check_monopoly(pl_location +i):
					rent = '10x Dice'
				else:
					rent = '4x Dice'
			else:
				rent = '$' + str(prop_table.rent_amount(pl_location + i,roll()))
		# Print table, 1 row at a time
		print ' ' * (10 - len(str(i))), i, ' ' * (21 - len(prop_name)), prop_name, \
			' ' * (10 - len(rent)), rent, ' ' * (16 - len(owner)), owner
	raw_input('\nPress Enter to return to the main menu.')
	print '\n======================================================\n'
		
