import sqlite3
import csv
import player_table

database_file = 'monopoly.db'
csv_file_name = 'Monopoly_Board.csv '

class property_table:
# class that, when instantiated, creates table containing all property information
# get_value(property_id, attribute) takes id and attribute and returns value of attribute
# set_value(id, attribute, value) takes id, attr, and value and sets attr to that value
# check_monopoly takes a property_id and returns a bool, for whether or not
# property is in a monopoly
# player_monopolies takes a player number and returns a list of property_id'seek
# owned by that player that are in monopolies. Useful for house building
# maximum_houses takes a property number and returns the maximum number of houses
# that can be built on that property
# also contains functions for mortgage menu, house builder menu, and player liquidation
	def __init__(self):
		# Per monopoly rules, a maximum of 32 houses and 12 hotels may be used in a game
		# This is updated if player buys houses/hotels
		self._houses_in_bank = 32
		self._hotels_in_bank = 12
		#start database connection, initialize table
		self.con = None
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		self.cur.executescript(
		"""DROP TABLE IF  EXISTS property;
		CREATE TABLE property(
		id INTEGER PRIMARY KEY,
		type TEXT,
		color TEXT,
		name TEXT,
		cost INTEGER,
		rent INTEGER,
		rent_1_house INTEGER,
		rent_2_house INTEGER,
		rent_3_house INTEGER,
		rent_4_house INTEGER,
		rent_hotel INTEGER,
		house_cost INTEGER,
		owner INTEGER,
		houses INTEGER,
		mortgage INTEGER,
		hotel_eligible INTEGER);""")
		
		#read csv, populate database table with values
		with open(csv_file_name, 'rt') as f:
			for line in f:
				self.cur.execute("""INSERT INTO property VALUES (?,?,?,?,?,?,?,?,
				?,?,?,?,?,?,?,0);""",line.replace('\n','').split(','))
		self.con.commit()
		self.con.close()
				
	def get_value(self, property_id, attribute):
		# Takes property id and string for attribute, returns value for player_id from that column
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		_statement = "SELECT %s FROM property WHERE id = %d" % (attribute, property_id)
		self.cur.execute(_statement)
		b=self.cur.fetchall()
		self.con.close()
		return(b[0][0])
		
	def set_value(self, property_id, attribute, value):
		# Tales prop_id, str for attribute, and value
		# Changes attribute at prop_id to value
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		if isinstance(value,str):
			_statement = "UPDATE property SET %s = %s WHERE id = %s"\
			% (attribute,value,property_id)
		else:
			_statement = "UPDATE property SET %s = %d WHERE id = %s"\
			% (attribute,value,property_id)
		self.cur.execute(_statement)
		self.con.commit()
		self.con.close()
	
	def hotel_eligible(self):
		# This is called at beginning of every turn.
		# Rule in monopoly is that you can't build a hotel on a property the same
		# turn you build 4 houses. This updates column to 0 for properties with 
		# less than 4 houses at beginnign of turn.
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		_statement = """UPDATE property SET hotel_eligible = 0 WHERE houses < 4;"""
		self.cur.execute(_statement)
		_statement = """UPDATE property SET hotel_eligible = 1 WHERE houses >= 4;"""
		self.cur.execute(_statement)
		self.con.commit()
		self.con.close()
		
	def check_monopoly(self, property_id):
	#takes a property value, returns whether or not that property is part of monopoly
		# check for number of owners
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		_statement = """SELECT COUNT(DISTINCT owner) FROM property a 
				WHERE a.color = (SELECT b.color FROM property b 
				WHERE b.id = %d)""" % (property_id)
		self.cur.execute(_statement)
		owner_count = self.cur.fetchall()[0][0]
		#ensure it isn't a bank owned monopoly
		player_owned = (self.get_value(property_id , 'owner') != 9)
		# if owned by only one entity AND entity is a player, return True
		self.con.close()
		if (player_owned) and (owner_count == 1):
			return True
		else:
			return False
	
	def player_monopolies(self, player_id):
	# takes a player_id as arg, returns all properties that that player owns that
	# are also monopolies
		_statement = """ SELECT b.color FROM 
		(SELECT a.color, count(a.id) owner_count FROM property a 
		WHERE a.owner = %s AND type = 'prop' AND color NOT IN ('Railroad','Utility') GROUP BY a.color) b
		JOIN (SELECT c.color, count(c.id) total_count FROM property c GROUP BY c.color) d
		ON b.color = d.color WHERE b.owner_count = d.total_count;""" % (player_id)
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		self.cur.execute(_statement)
		_raw_monopoly_array_color=self.cur.fetchall()
		_monopoly_array_color = []
		for i in range(len(_raw_monopoly_array_color)):
			_monopoly_array_color.append(str(_raw_monopoly_array_color[i][0]))
		
		_statement = """ SELECT a.id FROM property a WHERE a.color IN (%s);"""\
						% str(_monopoly_array_color).replace('[','').replace(']','')
		self.cur.execute(_statement)
		_raw_monopoly_array_id = self.cur.fetchall()
		_monopoly_array_id = []
		for i in range(len(_raw_monopoly_array_id)):
			_monopoly_array_id.append(_raw_monopoly_array_id[i][0])
		return _monopoly_array_id
	
	def liquidate_player(self, player_id, kill = None):
		# Performs 2 key functions. If 'kill' equals any number,
		# player's houses and properties are returned to bank, mortgaged.
		# If no 'kill' arg specified, provides a player's liquidation value (houses, properties)
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		if isinstance(kill, int):
			_statement = """UPDATE property  SET houses = 0, owner = 9, mortgage = 1
			WHERE owner = %d""" % (player_id)
			self.cur.execute(_statement)
			self.con.commit()
		else:
			_statement = """SELECT SUM(house_cost*houses/2) + SUM(cost/2) FROM property WHERE
						 mortgage = 0 AND owner = %d""" % (player_id)
			self.cur.execute(_statement)
			_liquidation_value = self.cur.fetchall()[0][0] 
			if not _liquidation_value:
				_liquidation_value = 0
			return _liquidation_value
		self.con.close()	
		
	def rent_amount(self, property_id, dice_roll):
		# Takes property_id and returns rent amount
		property_color = self.get_value(property_id,"color")
		houses_on_property = self.get_value(property_id,"houses")
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		if property_color == "Railroad":
			# Railroads and utilities have special rules. Count railroads.
			_statement = """SELECT count(id) FROM property WHERE owner = 
					(SELECT owner FROM property WHERE id = %d)
					AND color = 'Railroad';""" \
					% (property_id)
			self.cur.execute(_statement)
			number_owned_rails = self.cur.fetchall()[0][0]
			# Railroad amount can be 25, 50, 100, or 200 depending on # of RR's owned
			owed_amount = (2 ** (number_owned_rails - 1)) * 25
		elif property_color == "Utility":
			# Utility gets special call
			_statement = """SELECT count(id) FROM property WHERE owner = 
					(SELECT owner FROM property WHERE id = %d)
					AND color = 'Utility';""" \
					% (property_id)
			self.cur.execute(_statement)
			number_owned_utilities = self.cur.fetchall()[0][0]
			# Takes dice roll and returns either 4x amount or 10x amount
			# depending on whether owner owns both utils or not
			if number_owned_utilities == 1:
				owed_amount = 4 * (dice_roll[0] + dice_roll[1])
			else:
				owed_amount = 10 * (dice_roll[0] + dice_roll[1])
		# If regular property with no houses, returns rent.
		# Multiplies by 2 if owner has a monopoly on that color
		elif houses_on_property == 0:
			monopoly_multiplier = 1
			if self.check_monopoly(property_id):
				monopoly_multiplier = 2
			owed_amount = self.get_value(property_id, "rent") * monopoly_multiplier
		# Give value for 1,2,3,4,5(hotel) houses
		elif houses_on_property ==1:
			owed_amount = self.get_value(property_id, "rent_1_house")
		elif houses_on_property ==2:
			owed_amount = self.get_value(property_id, "rent_2_house")
		elif houses_on_property ==1:
			owed_amount = self.get_value(property_id, "rent_3_house")
		elif houses_on_property ==1:
			owed_amount = self.get_value(property_id, "rent_4_house")
		else:
			owed_amount = self.get_value(property_id, "rent_hotel")
		self.con.close()
		return owed_amount
	
	def mortgage_menu(self, pl_table, player_id):
		# Mortgage menu. Asks if player is mortgaging or un, and sends choice
		# as argument to mortgage_prop function
		choice = 'ii'
		print '\n' * 50, '\n======================================================\n'
		print 'Welcome to the mortgage menu, %s.' % (pl_table.name(player_id))
		while choice.lower() != 'menu':
			print 'Please select an option.\n1. Mortgage Property\
			\n2. Unmortgage Property\n\nType "Menu" to return to main menu\n'
			choice = raw_input('> ')
			if choice == '1':
				self.mortgage_prop(pl_table, player_id, "Mortgage")
			if choice == '2':
				self.mortgage_prop(pl_table,player_id, "Unmortgage")
		print '\n' * 50
	
	def mortgage_prop(self, pl_table, player_id, action):
		# Allows player to mortgage or unmortgage property, depending on 'action' arg
		print '\n======================================================\n'
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		if action == "Mortgage":
			# If mortgaging, value of mortgaged property is half property value
			mort_index = 0
			multiplier = 1
		else:
			# If unmortgaging, pay 10% upcharge
			mort_index = 1
			multiplier = 1.1
		_statement = "SELECT a.id, a.name, a.cost FROM property a WHERE a.owner = %d\
					AND a.mortgage = %d AND a.color NOT IN \
					(SELECT b.color FROM property b WHERE b.houses > 0 GROUP BY color)"\
					% (player_id, mort_index)
		self.cur.execute(_statement)
		mortgage_list = self.cur.fetchall()
		if len(mortgage_list) == 0 and mort_index == 0:
			# If no properties are avail to mortgage
			print '\n' * 50, '======================================================\n'
			print "You have no properties available to mortgage.\
			\nYou can only mortgage a property if you own it, \
			\nit is unmortgaged, and no properties in its color \
			\ngroup have houses or hotels.\n"
			choice = 'menu'
		elif len(mortgage_list) == 0 and mort_index == 1:
			print '\n' * 50, '======================================================\n'
			print "All of your properties are unmortgaged.\n"
			choice = 'menu'
		else:
			# This happens if mortgage_list isn't blank
			choice = 'ii'
			while choice.lower() != 'menu':
				# Print available properties. Headers first
				print "Here are the properties available to %s:\n" % action.lower()
				print ' ' * (25 - len('property name')), 'Property Name', \
				' ' * (16 - len(action + 'value')), action,'Value'
				for i in range(len(mortgage_list)):
					# Print values (with correct spacing)
					print str(i+1) + '.' + (' ' * (2-len(str(i+1)))),
					print ' ' * (21 - len(str(mortgage_list[i][1]))), mortgage_list[i][1],
					print ' ' * (16 - len(str(int(((mortgage_list[i][2])/2)*multiplier)))), '$' + str((int((mortgage_list[i][2]/2)*multiplier)))
				print '\nSelect which property you would like to %s.\
				\nType Menu to go back.' % (action.lower())
				choice = raw_input('> ')
				if len(choice.replace(' ','')) > 0  and choice in str(range(1,len(mortgage_list)+1)):
					# If choice is made, that property is (un)mortgaged,
					# removed from list, and amount of money is credited to player.
					property_id = mortgage_list[int(choice) - 1][0]
					property_name = mortgage_list[int(choice) - 1][1]
					amount = ((mortgage_list[int(choice) - 1][2])/2) * multiplier
					if action == "Unmortgage":
						amount *= -1
					if pl_table.cash(player_id) < -amount:
						# Called if player tries to unmortgage property but doesn't have $$
						print "Insufficient funds. You only have %d." % pl.cash(player_id)
					else:
						pl_table.money_transfer(self,player_id,amount,9)
						self.set_value(property_id,"mortgage",1)
						del mortgage_list[int(choice) - 1]
						print '\n======================================================\n'
						print '%s is now %sd. \
						\nA change of $%d has been applied to your account.'\
						% (property_name,action.lower(),amount)
						print 'CASH FOR PLAYER: %d' % pl_table.cash(player_id)
				elif choice.lower() != "menu":
					print "You must enter a number or type menu, dude"
		self.con.close()
	
	def house_menu(self, pl_table, player_id):
		# Menu for building houses. If no properties eligible for building,
		# print message
		print '\n' * 50
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		monopolies = self.player_monopolies(player_id)
		_statement = "SELECT id, name, color, houses, 0 FROM property\
					WHERE id IN %s" % (tuple(monopolies),)
		self.cur.execute(_statement)
		monopoly_data = self.cur.fetchall()
		if len(monopoly_data) == 0:
			print '\n======================================================\n'
			print 'You do not have any improvable properties.\
			\nYou must own every property (unmortgaged) in a color \
			\ngroup to build houses and hotels.'
		else:
			print '\nWelcome to the house builder menu!'
			choice = 'i'
			while choice.lower() !='menu':
				# Depending on choice, sends to house_builder fn with appropriate args
				print '\nPlease select an option.\n1. Buy Houses\
				\n2. Sell Houses\n3. Buy Hotels\n4. Sell Hotels\
				\n\nType "Menu" to return to main menu\n'
				choice = raw_input('> ')
				if choice == '1':
					self.house_builder(monopolies, pl_table, player_id, 'Buy', 'House')
				elif choice == '2':
					self.house_builder(monopolies, pl_table, player_id, 'Sell', 'House')
				elif choice == '3':
					self.house_builder(monopolies, pl_table, player_id, 'Buy', 'Hotel')
				elif choice == '4':
					self.house_builder(monopolies, pl_table, player_id, 'Sell', 'Hotel')
		self.con.close()
			
	def house_builder(self, monopolies, pl_table, player_id, buy_sell, house_hotel):
	# Builds/sells houses. Checks if move is legal and ensures player has cash to do it
		# This sets the max number of houses (hotels) that can go on a property.
		# Since they're all stored as one value (0-5), this is necessary
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		if house_hotel == 'House':
			less_greater = '<= 4'
			hotel_adjust = 0
		else:
			less_greater = 'BETWEEN 4 AND 5 AND hotel_eligible = 1'
			hotel_adjust = -4
		
		_statement = "SELECT id, name, color, house_cost, houses FROM property\
					WHERE id IN (%s) AND houses %s" % (str(monopolies).replace('[','').replace(']',''),less_greater)

		self.cur.execute(_statement)
		builder_data = self.cur.fetchall()
		
		#Create to_build list, initialized at 0 for every property in list
		to_build = [0] * len(builder_data)
			
		if len(builder_data) == 0:
			# If no properties eligible for build/sell ing
			print '\nNone of your properties are eligible for %s %sing.'\
			% (house_hotel.lower(),buy_sell.lower())
			if house_hotel == "Hotel" and buy_sell == "Buy":
				print "\nKeep in mind that a property must have 4 houses for \
				\none turn before hotels can be built."
		else:
			# Initialize house and hotel balances from global variables. 
			# If change is made, global variables are updated accordingly.
			house_balance = self._houses_in_bank
			hotel_balance = self._hotels_in_bank
			choice = 'i'
			if buy_sell == 'Buy':
				multiplier = 1
			else:
				# houses/hotels only worth half as much if sold
				multiplier = .5
			print "Here are the properties available:"
			total_cost = 0
			while not choice.lower() in ('commit','menu'):
				# print list. headers first
				print ' ' * (25 - len('property name')), 'Property Name', \
				' ' * (8 - len(buy_sell + 'cost')), buy_sell,'Cost',\
				' ' * (11 - len('# of houses')), '# of %ss' % house_hotel,\
				' ' * (12 - len('Build amount')), 'Build Amount'
				for i in range(len(builder_data)):
					# print values in list
					print str(i+1) + '.' + (' ' * (2-len(str(i+1)))),
					print ' ' * (21 - len(str(builder_data[i][1]))), builder_data[i][1],
					print ' ' * (8 - len(str(int(((builder_data[i][3])* multiplier))))), \
					'$' + str((int((builder_data[i][3])* multiplier))),
					print ' ' * (11 - len(str(builder_data[i][4] + hotel_adjust))), (builder_data[i][4] + hotel_adjust),
					print ' ' * (12 - len(str(to_build[i]))), to_build[i]
					
				if house_hotel == "House":
					# Print house/hotel balance
					print '\nHouses left in bank: %d' % house_balance
				else:
					print '\nHotels left in bank: %d' % hotel_balance
					
				print 'Total cost: $%d\nSelect a property to add %ss to %s.\nTo confirm changes, type "Commit".\
				\nTo cancel changes and exit, type "Menu"' % (total_cost, house_hotel.lower(), buy_sell.lower())
				choice = raw_input('> ').replace(' ','')
				
				# Take choice from user. If 'menu' or 'commit', special actions.
				if choice in str(range(1,len(builder_data) + 1)) and len(choice) >0:			
					if buy_sell == "Buy" and house_hotel == "House":
						# If building a legal number of houses (4 or less for houses, 1 or less for hotel),
						# Add cost to total cost, subtract house from house balance
						if (builder_data[int(choice) - 1][4] + to_build[int(choice) - 1]) < 4\
							and house_balance > 0:
							to_build[int(choice) - 1] += 1
							house_balance -= 1
							total_cost += (builder_data[int(choice) - 1][3] * multiplier)
							print '\n1 house added to %s.\n' % (builder_data[int(choice)-1][1])
						elif house_balance == 0:
							# If no houses left
							print "No houses left in bank."
						else:
							# if they try to build too many houses
							print "\nA property may only contain 4 houses.\
							\nPlease select a different property, or build a hotel on this property.\n"
	
					elif buy_sell == "Buy" and house_hotel == "Hotel":
						# If building a legal number of houses (4 or less for houses, 1 or less for hotel),
						# Add cost to total cost, subtract hotel from hotel balance.
						# Add FOUR to house balance, since hotel creation MUST remove 4 houses
						if (builder_data[int(choice) - 1][4] + to_build[int(choice) - 1]) < 5\
							and house_balance > 0:
							to_build[int(choice) - 1] += 1
							hotel_balance -= 1
							house_balance += 4
							total_cost += (builder_data[int(choice) - 1][3] * multiplier)
							print '\n1 hotel added to %s.\n' % (builder_data[int(choice)-1][1])
						elif hotel_balance == 0:
							# If no hotels left
							print "No hotels left in bank."
						else:
							# If prop already has hotel
							print "\nThis property already has a hotel.\n"
							
					elif buy_sell == "Sell" and house_hotel == "House":
						# Subtract cost to total cost, add house to house balance.
						if (builder_data[int(choice) - 1][4] + to_build[int(choice) - 1]) > 0:
							to_build[int(choice) - 1] -= 1
							house_balance += 1
							print '\n1 house removed from %s.\n' % (builder_data[int(choice)-1][1])
							total_cost -= (builder_data[int(choice) - 1][3] * multiplier)
						else:
							print "\nThis property has no houses on it.\n"
							
					elif buy_sell == "Sell" and house_hotel == "Hotel":
						# Subtract cost to total cost, add hotel to hotel balance.
						# Subtract FOUR houses from house balance
						if (builder_data[int(choice) - 1][4] + to_build[int(choice) - 1]) > 4:
							to_build[int(choice) - 1] -= 1
							hotel_balance += 1
							house_balance -= 4
							print '\n1 hotel removed to %s.\n' % (builder_data[int(choice)-1][1])
							total_cost -= (builder_data[int(choice) - 1][3] * multiplier)
						else:
							print "\nThis property has no hotels on it.\n"
			if choice.lower() == 'commit':
				# If 'commit', Check if enough cash and if build is legal (i.e. not too
				# many houses on one property)
				enough_cash = pl_table.cash(player_id) >= total_cost
				if enough_cash and self.legal_house_build(builder_data, to_build):
					pl_table.money_transfer(self, player_id, -total_cost, 9)
					print '\n$%d applied to account. %s now has $%d' \
					% (-total_cost, pl_table.name(player_id), pl_table.cash(player_id))
					# Sets houses_in_bank amount if transaction is valid
					self._houses_in_bank = house_balance
					self._hotels_in_bank = hotel_balance
				
				elif not enough_cash:
					# If not enough cash
					print '\nNot enough cash for transaction. You only have $%d.' % pl_table.cash(player_id)
				else:
					# If illegal build
					print '\nIllegal house build. The maximum number of houses on a color group\
					\ncan be at most one more than the minimum.'
			else:
				# If menu selected
				print '\nNo changes have been made.\n'
		self.con.close()

	def legal_house_build(self, builder_data, to_build):
		# takes list of property ids and house counts, returns if it's a legal build True or False
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		
		for i in range(len(builder_data)):
			if to_build[i] != 0:
				# This kind of sucks due to SQLite limitations.
				# First we will change the entire table to new values,
				# THEN check if it is legal. If it is not, we UNDO the changes
				# at end of legal_house_build fn
				number_houses = to_build[i]
				new_house_number = builder_data[i][4] + to_build[i]
				self.set_value(builder_data[i][0], "houses", new_house_number)
		legal = True
		for i in range(len(builder_data)):
			# Goes through property table, color by color, and determines
			# if current configuration of houses is legal. It is ILLEGAL
			# if one property in color group has 2+ more than any other property
			_statement = "SELECT color FROM property WHERE id = %d;"\
						% builder_data[i][0]
			self.cur.execute(_statement)
			color = self.cur.fetchall()
			_statement = """SELECT MIN(houses), MAX(houses) FROM property 
			WHERE(color = '%s');""" % (color[0][0])
			self.cur.execute(_statement)
			_min_max_houses = self.cur.fetchall()
			
			if (_min_max_houses[0][1] - _min_max_houses[0][0]) > 1:
				# If any property in entire table is illegal, legal = false
				legal = False
		if legal == False:
			# If move is illegal, unroll ENTIRE build action
			for i in range(len(builder_data)):
				if to_build[i] != 0:
					self.set_value(builder_data[i][0], "houses", builder_data[i][4])
		#return True or False
		self.con.close()
		return legal
		
	def player_properties(self, player_id):
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		_statement = 'SELECT id FROM property WHERE owner = %d' % player_id
		self.cur.execute(_statement)
		pl_props = self.cur.fetchall()
		self.con.close()
		return pl_props
	
	def all_property_data(self):
		# Used for saving game. Gives all table data
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		_statement = 'SELECT * FROM property'
		self.cur.execute(_statement)
		all_props = self.cur.fetchall()
		self.con.close()
		return all_props
		
	def end_game(self):
	# call this ONCE at end of game - ends database connection
		if self.con:
			self.con.close()
		
	def load_game(self, property_info):
		# Inserts property data for a single property
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		split_info = property_info.split(',')
		for i in (0,4,5,6,7,8,9,10,11,12,13,14,15):
			split_info[i] = int(split_info[i])
		self.cur.execute("""INSERT INTO property VALUES (?,?,?,?,?,?,?,?,
				?,?,?,?,?,?,?,?);""",split_info)
		self.con.commit()
		self.con.close()
	
	def clear_data(self):
	# Call this before loading game. Deletes ALL data from table
	# except column names.
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		self.cur.executescript(
		"""DROP TABLE IF  EXISTS property;
		CREATE TABLE property(
		id INTEGER PRIMARY KEY,
		type TEXT,
		color TEXT,
		name TEXT,
		cost INTEGER,
		rent INTEGER,
		rent_1_house INTEGER,
		rent_2_house INTEGER,
		rent_3_house INTEGER,
		rent_4_house INTEGER,
		rent_hotel INTEGER,
		house_cost INTEGER,
		owner INTEGER,
		houses INTEGER,
		mortgage INTEGER,
		hotel_eligible INTEGER);""")
		self.con.close()
