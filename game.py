#! python2
import start_game
import player_table
import property
import turn
import cards
import options
import os

#### INITIALIZE GAME #####

# Create blank player_table, which holds all info about players
pl = player_table.player_table()
# Initialize property database
prop = property.property_table()
# Initialize cards database
cards = cards.cards()
# Initialize whose turn it is - if a game is loaded, this may change
whose_turn = 0

print '\n' * 50
print '======================================================\n'
print "Welcome to Monopoly: The game of unadulterated capitalism.\n\n"

start_game.new_or_load(pl,prop,cards,whose_turn)
print '\n======================================================'

raw_input("\nWe're all set to play! Press enter to continue.\n")
print '\n' * 50
print '======================================================'
while pl.player_count > 1:
	doubles = True
	doubles_count = 0
	if pl.in_game(whose_turn):
		while doubles == True:
			# doubles is always True at beginning of player's turn. Actions that put player in jail
			# also change doubles value to False
			
			# refresh hotel_eligibe column - which says if hotels can be built on property this turn
			prop.hotel_eligible()
			
			if pl.in_jail(whose_turn) > 0:
				# Checks if player is in jail.
				print "This is turn %d for you in Jail. You may choose to pay $50 to exit.\
				\nIf you are in jail for 3 turns without rolling doubles, you will be forced to leave."\
				% (pl.in_jail(whose_turn)),
			option = 'ioi'
			while option != '1':  
				# 'choices' var is number of options allowable. If player is in jail,
				# option to pay is available. If player also has GOOJ free card,
				# then that option is also available.
				choices = 4
				print '\n======================================================\n'
				print "%s, it is your turn. You are at %s."\
				% (pl.name(whose_turn), prop.get_value(pl.location(whose_turn), "name"))
				print "\nPlease choose an option.\n1. Roll\n2. Buy/Sell Houses\
					\n3. Mortgage/Unmortgage Property \n4. Look Ahead at Board" 
				if pl.in_jail(whose_turn) > 0:
					choices += 1
					print "5. Pay $50 to exit Jail"
					if pl.get_out_of_jail(whose_turn) > 0:
						print '6. Use "Get out of Jail Free" Card'
						choices += 1
				print "\n0. Game Options"
				option = raw_input('\n> ')
				if option == '0' or option.lower() == 'o':
					# Send player to options menu
					options.options_menu(pl,prop,cards,whose_turn)
				elif option == '6' and choices >= 6:
					# Use GOOJ free card, gets out of jail, takes away one GOOJ free card
					print 'You have used your "Get out of Jail Free" card. Enjoy your freedom!'
					pl.get_out_of_jail(whose_turn,-1)
					pl.in_jail(whose_turn,False)
				elif option == '5' and choices >= 5:
					# If player has $50, takes $50 from player and takes them out of jail
					if pl.cash(whose_turn) < 50:
						print "Insufficient funds. You do not have $50"
					else:
						print "You have paid $50 and are no longer in jail. Enjoy your freedom!"
						pl.in_jail(whose_turn,False)
						pl.money_transfer(prop , whose_turn, -50, 9)
				elif option == '4':
					# Call function to print board information
					turn.look_ahead(pl, prop, whose_turn)
				elif option == '3':
					# Send player to mortgage menu
					prop.mortgage_menu(pl, whose_turn)
				elif option == '2':
					# Send player to house builder menu
					prop.house_menu(pl, whose_turn)
			# rolls dice
			dice_roll = turn.roll()
			
			print '\n' * 50, '\n======================================================\n'
			print "You rolled a %d and a %d." % (dice_roll[0], dice_roll[1])
			if pl.in_jail(whose_turn) > 0 and dice_roll[2] == True:	
				# If player rolls doubles in jail, they don't get to roll again
				# so we change dice_roll[2] to False
				print "Congratulations! You rolled doubles."
				pl.in_jail(whose_turn, False)
				dice_roll[2] = False
			elif pl.in_jail(whose_turn) == 3 and dice_roll[2] == False:
				# Takes player out of jail if they don't roll doubles 3 turns in a row
				# Also charges $50
				print "You failed to roll doubles 3 times. Pay $50"
				dice_roll[2] = False
				pl.in_jail(whose_turn, False)
				pl.money_transfer(prop , whose_turn, -50, 9)
			elif pl.in_jail(whose_turn) in range(1,3) and dice_roll[2] == False:
				# If player doesn't roll doubles in jail
				print "Remain in Jail another turn."
				pl.in_jail(whose_turn, True)
				dice_roll[2] = False
			
			# Add to doubles_count if doubles were rolled
			doubles = dice_roll[2]
			doubles_count += dice_roll[2]
			
			if doubles_count == 3:
				# If player rolls doubles 3x in a row, sends them to jail
				move_amount = 30 - pl.location(whose_turn)
				pl.location(whose_turn,move_amount)
				turn.goto_jail_action(pl,whose_turn,dice_roll)
				dice_roll[2] = False
				
			# This elif block happens when player isn't in jail
			elif pl.in_jail(whose_turn) == 0:
				# Move player's location by roll amount
				pl.location(whose_turn,(dice_roll[0] + dice_roll[1]))
				property_name = prop.get_value(pl.location(whose_turn),"name")
				print "\nYou moved %d spaces and are now at %s." \
				% ((dice_roll[0] + dice_roll[1]), property_name) 
				# Takes action on space
				turn.location_action(pl, prop, cards, whose_turn, dice_roll)
				print 'Cash for %s: $%d' % (pl.name(whose_turn),pl.cash(whose_turn))
				# We set doubles at END because go to jail space modifies turn.roll()[2]
				doubles = dice_roll[2]
			print '\n======================================================'
			# If player died on this turn, don't let them roll again
			if not pl.in_game(whose_turn):
				doubles = False
			if doubles and doubles_count > 0:
				print "Congratulations %s, you rolled doubles! Go again." % (pl.name(whose_turn))
	print "\n%s, your turn is over. %s is up next. Press Enter to advance."\
			% (pl.name(whose_turn), pl.name((whose_turn + 1) % pl.table_length))
	raw_input()
	# Print blank lines to clear output
	print '\n' * 50
	whose_turn = (whose_turn + 1) % pl.table_length

# When only one player is left, determine who the winner is and
# liquidate their assets to find winning net worth
winner_net = 0
for i in range(number_of_players):
		if pl.in_game(i) == True:
			winner = pl.name(i)
			winner_net = pl.cash(i) + prop.liquidate_player(i)
			
print "End game. %s wins with net worth of $%d. Congraulations!!!!!" % (winner, winner_net)

#Close database connection
prop.end_game()
raw_input()