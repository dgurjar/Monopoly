import start_game
import property
import math
class player_table:
# In this class, each object is an entire player database.
# For each GAME, we initiate one instance of player_table.
# When instantiated, it creates a self.data array which holds all info.
# Also created are _variables, which are column indicators to improve readability.
# e.g. _in_jail = 4. Calling player_table[x][4] returns in_jail bool for player x.
# Finally, _player_count is created on instantiation, which is 
# used to assign player_id (PRIMARY KEY) to players.


	def __init__(self):
		# initialize 
		self.data = []
		self.player_count = 0
		
		self._player_id = 0
		self._name = 1
		self._cash = 2
		self._location = 3
		self._in_jail = 4
		self._get_out_of_jail = 5
		self._in_game = 6
		
	def Create_Player(self, name):
		# Creates a player with unique ID number, initializes position, cash, etc
		self.data.append([self.player_count, name, 1500, 0, 0, 0, True])
		self.player_count += 1
		
	def name(self, player_id):
		# Takes player id, returns name of player
		return self.data[player_id][self._name]
	
	def cash(self, player_id, new_amount = None):
		# if only player ID is provided, player's cash is returned
		# if new_amount also provided, player's cash is SET to that amount
		if isinstance(new_amount, int):
			self.data[player_id][self._cash] = new_amount
		else:
			return self.data[player_id][self._cash]
			
	def location(self, player_id, change = None):
		# if only player ID is provided, player's location is returned
		# if new_amount also provided, player's location is increased by that amount
		if isinstance(change, int):
			if self.data[player_id][self._location] + change >= 40:
				print '\nYou passed Go! Collect $200'
				a=self.cash(player_id)
				self.cash(player_id, a + 200)
			self.data[player_id][self._location] = \
			(self.data[player_id][self._location] + change) % 40
		else:
			return self.data[player_id][self._location]
		
	def in_jail(self, player_id, change = None):
		# if only player ID is provided, player's in jail status is returned
		# if change = False also provided, in_jail is set to 0
		# if change = True provided, in_jail is incremented by 1
		if isinstance(change, bool) and change == True:
			self.data[player_id][self._in_jail] += 1
			
		elif isinstance(change, bool) and change == False:
			self.data[player_id][self._in_jail] = 0
			
		else:
			return self.data[player_id][self._in_jail]
			
	def get_out_of_jail(self, player_id, change = None):
		# if only player ID is provided, number of player's GOOJ free cards is returned
		# if new_amount also provided, player's GOOJ free cards is increased by that amount
		if isinstance(change, int):
			self.data[player_id][self._get_out_of_jail] += change
		else:
			return self.data[player_id][self._get_out_of_jail]
	
	def in_game(self, player_id, change = None):
		# if only player ID is provided, player's status (True if in game, False if not) is returned
		# if change (T,F) also provided, player's in_game status is set
		if isinstance(change, bool):
			self.data[player_id][self._in_game] = change
		else:
			return self.data[player_id][self._in_game]
		
	def money_transfer(self, prop_table, player_1, amount, player_2 = None):
	# takes property table, player_1, amount, and (optional) player_2 as args
	# Handles debts. If player_2 = 9, player_1 pays/receives money from bank.
	# if player_2 = another player, player_1 pays/receives money from player_2.
	# if NO player_2 arg, player_1 pays/receives money from ALL players
	# use POSITIVE amount value to receive money from bank/player_2/everyone
	# use NEGATIVE amount value to give money to bank/player_2/everyone
		if isinstance(player_2, int):
			if player_2 == 9:
				amount_to_bank = self.debt_resolve(prop_table, player_1,(-1 * amount))
				self.data[player_1][self._cash] -= amount_to_bank
			else:
				#passes amount to debs_resolve, which returns the amount to be transferred
				a = int(math.fabs(self.debt_resolve(prop_table, player_1, (-1 * amount))))
				b = int(math.fabs(self.debt_resolve(prop_table, player_2, amount)))
				amount_to_player = min([a,b])
				if self.in_game(player_1):
					self.data[player_1][self._cash] -= amount_to_player
				if self.in_game(player_2):
					self.data[player_2][self._cash] += amount_to_player
		else:
			for i in range(self.player_count):
				if (player_1 != i) and (self.in_game(i)):
					self.money_transfer(prop_table,player_1, amount, i)
				
	def debt_resolve(self, prop_table, player_id, amount):
	# handles situations where player has insufficient funds to pay debt
	# allows player to sell houses or mortgage properties
	# if the player doesn't have enough net worth to pay, player's assets are
	# liquidated and total net worth is returned
		if amount <= self.cash(player_id):
			return amount
		else:
			debt_amount = amount - self.cash(player_id)
			while self.in_game(player_id) and (self.cash(player_id) < amount):
				# This updates each time an asset is liquidated (sold)
				print "\n%s, you have a $%d debt and are $%d short of paying it."\
						% (self.name(player_id),amount,debt_amount)
				# liquidation_value is a players total "ability to pay". If they don't have
				# enough assets, 'else' portion of statement is called,
				# their assets are liquidated and player is removed from game.
				liquidation_value = prop_table.liquidate_player(player_id) + self.cash(player_id)
				if liquidation_value >= amount:
					print '\nWhat would you like to do?\n'
					# display options menu
					choice = '_'
					print "1. Sell houses\
					\n2. Sell hotels\
					\n3. Mortgage properties\
					\n\nPlease enter a number.\n"
					while choice not in str(range(1,4)):
						# If player has enough assets to pay, they will liquidate until their cash
						# is greater than the amount owed
						choice = raw_input('> ')
						while start_game.is_int(choice) == False:
							print "\nEnter a number, bromosapien.\n\
							\n1. Sell houses\
							\n2. Sell hotels\
							\n3. Mortgage properties\
							\n\nPlease enter a number.\n"
							choice = raw_input('> ')
						if int(choice) not in range(1,4):
							print "\nSelect a number between 1 and 3.\n\
							\n1. Sell houses\
							\n2. Sell hotels\
							\n3. Mortgage properties\
							\n\nPlease enter a number.\n"
						else:
							# Takes choice - 1 to sell houses, 2 to sell hotels, 3 to mortgage properties,
							# and pulls up corresponding menu.
							if choice == '1':
								prop_table.house_builder(prop_table.player_monopolies(player_id), self, player_id, "Sell", "House")
							if choice == '2':
								prop_table.house_builder(prop_table.player_monopolies(player_id), self, player_id, "Sell", "Hotel")
							elif choice == '3':
								prop_table.mortgage_menu(self,player_id)
							debt_amount = amount - self.cash(player_id)
				else:
					# Player doesn't have enough assets to pay debt. return their total liquidation value
					print "\n%s, you have a $%d debt and are $%d short of paying it."\
					% (self.name(player_id),amount,debt_amount)
					print "%s, you do not have enough assets to pay your debt.\
					\nYou owe $%d, but your total net worth is only $%d.\
					\n\nThanks for playing, we're sorry to see you go!!!!" \
					% (self.name(player_id),amount, liquidation_value)
					prop_table.liquidate_player(player_id,1)
					self.in_game(player_id,False)
					self.player_count -= 1
					return liquidation_value
							
				
				
		
		
		
		