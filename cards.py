import random
import sqlite3
import csv

import player_table
import property
import start_game
import turn

database_file = 'monopoly.db'
csv_chance = 'chance.csv'
csv_community = 'community_chest.csv'

class cards:
	def __init__(self):
		# Chance table creation
		self.con = None
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		self.cur.executescript(
		"""DROP TABLE IF  EXISTS chance;
		CREATE TABLE chance(
		id INTEGER PRIMARY KEY,
		type TEXT,
		description TEXT,
		flag INTEGER,
		amount INTEGER,
		drawn INTEGER);""")
		
		#define columns for easy referencing
		self._id = 0
		self._type = 1
		self._description = 2
		self._flag = 3
		self._amount = 4
		self._drawn = 5
		
		#read csv, populate database table with values
		with open(csv_chance, 'rt') as f:
			for line in f:
				self.cur.execute("""INSERT INTO chance VALUES 
				(?,?,?,?,?,?);""",line.replace('\n','').split(','))
				
		# Community Chest table creation
		self.cur.executescript(
		"""DROP TABLE IF  EXISTS community;
		CREATE TABLE community(
		id INTEGER PRIMARY KEY,
		type TEXT,
		description TEXT,
		flag INTEGER,
		amount INTEGER,
		drawn INTEGER);""")
		
		#read csv, populate database table with values
		with open(csv_community, 'rt') as f:
			for line in f:
				self.cur.execute("""INSERT INTO community VALUES(?,?,?,
				?,?,?);""",line.replace('\n','').split(','))
		self.con.commit()
		self.con.close()
				
	def draw_card(self, pl_table, prop_table, which_deck, player_id, dice_value):
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		if which_deck == 'chance':
			deck_name = 'Chance'
		else:
			deck_name = 'Community Chest'
		# Draw random card from deck 
		_statement = "SELECT * FROM %s WHERE drawn = 0" % (which_deck)
		self.cur.execute(_statement)
		undrawn_cards = self.cur.fetchall()
		deck_count = len(undrawn_cards)
		draw_id = random.randint(0,deck_count-1)
		print "Your card says: %s" % (undrawn_cards[draw_id][self._description])
		self.old_location = pl_table.location(player_id)
		_statement = "UPDATE %s SET drawn = 1 WHERE id = %d;" % (which_deck,draw_id)
		self.cur.execute(_statement)
		self.con.commit()
		# perform card action
		card_type = undrawn_cards[draw_id][self._type]
		
		# check if deck is empty, 'reshuffle' deck if it is
		if deck_count == 1:
			self.replenish_deck(which_deck,deck_name)
			print "You drew the last card in the deck! Deck has been reshuffled."
			
		if card_type == "cash_change":
			self.cash_change(pl_table,prop_table,undrawn_cards[draw_id],player_id)
		elif card_type == "set_spot":
			self.set_spot(pl_table,prop_table, undrawn_cards[draw_id],player_id, dice_value)
		elif card_type == "out_of_jail":
			self.out_of_jail(pl_table, player_id)
		elif card_type == "house_tax":
			self.house_tax(pl_table, prop_table, undrawn_cards[draw_id], player_id)
		elif card_type == "nearest_utility":
			self.nearest_utility(pl_table, prop_table, undrawn_cards[draw_id], player_id) #UNFINISHEDDDDD!!! 
		elif card_type == "nearest_railroad":
			self.nearest_railroad(pl_table, prop_table, undrawn_cards[draw_id], player_id)
		
		self.con.close()
		
		
	def replenish_deck(self,which_deck, deck_name):	
		# Called when last card in deck was just drawn. Updates database to
		# put all cards back into eligibility
		print "All cards have been drawn from the %s deck. Reshuffling..." \
				% (deck_name)
		_statement = "UPDATE %s SET drawn = 0" % (which_deck)
		self.cur.execute(_statement)
		self.con.commit()
		print "Shuffling complete."
	
	def cash_change(self,pl_table,prop_table,card,player_id):
		# takes player table, prop table, card(ROW) and 
		# player_id and performs cash transfer
		if card[self._flag] == 0:
			pl_table.money_transfer(prop_table, player_id, card[self._amount], 9)
		else:
			pl_table.money_transfer(prop_table, player_id, card[self._amount])
		
	def set_spot(self, pl_table, prop_table, card, player_id, dice_value):
		# sets player position. if flag == 0, ensures they don't pass go
		if card[self._flag] == 0:
			move_amount = 30 - pl_table.location(player_id)
		elif card[self._flag] == 1:
			if pl_table.location(player_id) < card[self._amount]:
				move_amount = card[self._amount] - pl_table.location(player_id)
			else:
				move_amount = card[self._amount] + 40 - pl_table.location(player_id)
		else:
			move_amount = -3
		pl_table.location(player_id, move_amount)
		# call turn.location_action from new location
		turn.location_action(pl_table, prop_table, self, player_id,dice_value)
			
	def out_of_jail(self, pl_table, player_id):
		# Adds 1 to get out of jail free card attribute for player
		pl_table.get_out_of_jail(player_id,1)
			
	def house_tax(self,pl_table,prop_table,card,player_id):
		# Calculates number of houses and hotels for player, multiplies by
		# amount on card (NOTE: 'flag' column is house amt, 'amount' column
		# is hotel amt.) Charges that amount to player
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		_statement = """SELECT SUM(houses * %d) FROM property 
					WHERE owner = %d AND houses BETWEEN 1 AND 4;""" \
					% (card[self._flag], player_id)
		prop_table.cur.execute(_statement)
		house_fee = prop_table.cur.fetchall()
		if len(house_fee) == 0:
			house_fee = 0
		elif house_fee[0][0] == None:
			house_fee = 0
		else:
			house_fee = house_fee[0][0]
		house_count = house_fee / card[self._flag]
		_statement = """SELECT (houses / 5) * %d FROM property
					WHERE owner = %d AND houses = 5;""" \
					% (card[self._amount], player_id)
		prop_table.cur.execute(_statement)
		hotel_fee = prop_table.cur.fetchall()
		if len(hotel_fee) == 0:
			hotel_fee = 0
		elif hotel_fee[0][0] == None:
			hotel_fee = 0
		else:
			hotel_fee = hotel_fee[0][0]
		hotel_count = hotel_fee / card[self._amount]
		total_fee = house_fee + hotel_fee
		print "%s, you own %d houses and %d hotels. Your total bill is $%d."\
			% (pl_table.name(player_id),house_count,hotel_count,total_fee)
		pl_table.money_transfer(prop_table, player_id, -total_fee, 9)
		self.con.close()
			
	def nearest_railroad(self,pl_table,prop_table,card,player_id):
		# Calculates where nearest railroad is, moves player to that location
		# If railroad is owned, uses special payment function to pay double
		# amount. If unowned, gives option to buy
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		move_amount = (5 - self.old_location) % 10
		pl_table.location(player_id,move_amount)
		print "\nThe nearest Railroad is the %s.\n" % (prop_table.get_value(pl_table.location(player_id), "name"))
		_statement = """SELECT count(id), owner FROM property WHERE owner = 
					(SELECT owner FROM property WHERE id = %d)
					AND type = 'rail' AND owner <> 9 GROUP BY owner;""" \
					% (pl_table.location(player_id))
		prop_table.cur.execute(_statement)
		number_owned_rails = prop_table.cur.fetchall()
		if len(number_owned_rails) == 0:
			railroad_owner = 9
			number_owned_rails = 0
		else:
			railroad_owner = number_owned_rails[0][1]
			number_owned_rails = number_owned_rails[0][0]
		if railroad_owner != 9:
			if railroad_owner == player_id:
				print "You own this property! Enjoy your free stay"
			else:
				owed_amount = (2 ** number_owned_rails) * 25
				print "This property is owned by %s. Pay $%d." \
				% (pl_table.name(railroad_owner), owed_amount)
				pl_table.money_transfer(prop_table, player_id, -owed_amount, railroad_owner)
		else:
			turn.location_action(pl_table, prop_table, self, player_id,1)
		self.con.close()
			
	def nearest_utility(self,pl_table,prop_table,card,player_id):
		# Calculates where nearest utility is, moves player to that location
		# If utility is owned, rolls dice and uses special payment function 
		# to pay 10x dice amount amount. If unowned, gives option to buy.
		if self.old_location >= 28 or self.old_location < 12:
			move_amount = (12 - self.old_location) % 40
			print "\nThe nearest utility is the Electric Company."
		else:
			move_amount = (28 - self.old_location) % 40
			print "\nThe nearest utility is Water Works."
		pl_table.location(player_id,move_amount)
		_statement = "SELECT owner FROM property WHERE id = %d" \
					% (pl_table.location(player_id))
		prop_table.cur.execute(_statement)
		utility_owner = prop_table.cur.fetchall()[0][0]
		if not utility_owner == 9:
			if utility_owner == player_id:
				print "You own this property! Enjoy your free stay."
			else:
				die_1 = random.randint(1,6)
				die_2 = random.randint(1,6)
				roll = die_1 + die_2
				owed_amount = roll * 10
				print "This property is owned by %s. You must roll \
				\nthe dice and pay ten times the amount shown.\
				\n\nPress Enter to roll:" \
				% (pl_table.name(utility_owner))
				raw_input()
				print "You rolled a %d and a %d. Pay $%d to %s." \
				% (die_1,die_2,owed_amount,pl_table.name(utility_owner))
				pl_table.money_transfer(prop_table, player_id, -owed_amount, utility_owner)
		else:
			turn.location_action(pl_table, prop_table, self, player_id,1)
	
	def all_cards(self, which_deck):
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		_statement = "SELECT * FROM %s" % (which_deck)
		self.cur.execute(_statement)
		card_data = self.cur.fetchall()
		self.con.close()
		return card_data
		
	def load_game(self, which_deck, draw_status):
		self.con = sqlite3.connect(database_file)		
		self.cur=self.con.cursor()
		split_draw_status = draw_status.split(',')
		for i in range(len(split_draw_status)):
			_statement = "UPDATE %s SET drawn = %d WHERE id = %d;" \
				% (which_deck,int(split_draw_status[i]),i)
			self.cur.execute(_statement)
			self.con.commit()
		self.con.close()
			