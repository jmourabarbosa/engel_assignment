from __future__ import division
import sqlite3
from sqlite3 import Error
from numpy import *
import numpy as np
import pandas as pd


def init_db(conn):

	# create tables
	create_table(conn,sql_create_subjects_table)
	create_table(conn,sql_create_cells_table)
	create_table(conn,sql_create_sessions_table)
	create_table(conn,sql_create_trials_table)
	create_table(conn,sql_create_recordings_table)
	create_table(conn,sql_create_spikes_table)
	create_table(conn,sql_create_behavior_table)
	
## This is a very simple version of what would be the final manage_db
def my_isnan(var):
	if isinstance(var,float):
		return isnan(var)
	else:
		return False

def create_table(conn, create_table_sql):
	""" create a table from the create_table_sql statement
	:param conn: Connection object
	:param create_table_sql: a CREATE TABLE statement
	:return:
	"""
	try:
		c = conn.cursor()
		c.execute(create_table_sql)
	except Error as e:
		print(e)

def select_data_from_table(conn,data,table):
	"""
	Select data from tabel
	:param conn:
	:param data: list of columns
	:return:
	"""

	#values = str(data)[1:-1]
	sql = "select {0} from {1};".format(data,table)

	df = pd.read_sql_query(sql,conn)

	return df

def get_behavior(conn):

	df=pd.read_sql_query("select stimulus,sacc_angle,subject_id \
		from behavior as b \
		left join trials as t \
			on b.trial_id = t.id \
		left join sessions as s \
			on b.session_id == s.id;",conn)


	# don't like this at all, would need to implement better
	df[df["stimulus"]=="NULL"] = np.nan

	return df

def get_cells_id(conn):
	df=pd.read_sql_query("select cell_id from spikes;",conn)
	return df["cell_id"].unique()

def get_spikes_cell_interval(conn,cell_id,interval):

	beg,end = interval
	df=pd.read_sql_query("select spike_t, stimulus \
							from spikes as s \
							left join trials as t \
								on s.trial_id = t.id \
							where cell_id=={0} and s.spike_t between {1} and {2}".format(cell_id,beg,end),conn)

	return df
def insert_many_items(conn,table,data,commit=True):
	"""
	Insert many entries in table
	:param conn:
	:param data: dictionary of key values, each value is a list of values to insert
	:return:
	"""
	# TODO:
	# check if data is well structured 

	n_values = len(data.keys())
	n_transactions = len(data.values()[0])

	#import ipdb; ipdb.set_trace()


	keys = tuple(data.keys())
	values = [[data.values()[v][t] if ~my_isnan(data.values()[v][t]) else "NULL" for v in range(n_values)] for t in range(n_transactions)]

	sql_i = ""


	for t in range(n_transactions):
			sql_i += '''	INSERT INTO {0} {1}
					VALUES {2} ;'''.format(table,keys,tuple(values[t]))


	sql = "BEGIN TRANSACTION;" + sql_i + "COMMIT;"

	cur = conn.cursor()
	cur.executescript(sql)
	if commit:
		conn.commit()
	return cur


def insert_item(conn,table,data):
	"""
	Create a entry in table 
	:param conn:
	:param data:
	:return:
	"""

	# TODO:
	# check if data is well structured for table

	keys = tuple(data.keys())
	values = tuple(data.values())
	sql = '''	INSERT INTO {0} {1}
			VALUES {2} '''.format(table,keys,values)

	cur = conn.cursor()
	cur.execute(sql)
	return cur.lastrowid

sql_create_subjects_table = """ CREATE TABLE IF NOT EXISTS subjects (
									id text PRIMARY KEY,
									n_sessions integer
								); """

sql_create_cells_table = """ CREATE TABLE IF NOT EXISTS cells (
									id integer PRIMARY KEY,
									cell_type integer
								); """

sql_create_sessions_table = """ CREATE TABLE IF NOT EXISTS sessions (
									id text PRIMARY KEY,
									subject_id integer NOT NULL,
									n_cells integer NOT NULL,
									FOREIGN KEY (subject_id) REFERENCES subjects (id)
								); """

sql_create_trials_table = """ CREATE TABLE IF NOT EXISTS trials (
									id integer PRIMARY KEY,
									session_id integer NOT NULL,
									stimulus integer,
									FOREIGN KEY (session_id) REFERENCES sessions (id)
								); """


sql_create_recordings_table = """ CREATE TABLE IF NOT EXISTS recordings (
									id integer PRIMARY KEY,
									cell_id integer NOT NULL,
									session_id text NOT NULL,
									trial_id integer NOT NULL,
									FOREIGN KEY (cell_id) REFERENCES cell (id),
									FOREIGN KEY (session_id) REFERENCES session (id),
									FOREIGN KEY (trial_id) REFERENCES trial (id)
								); """

sql_create_spikes_table = """ CREATE TABLE IF NOT EXISTS spikes (
									id integer PRIMARY KEY,
									recording_id integer NOT NULL,
									trial_id integer NOT NULL,
									cell_id integer NOT NULL,
									spike_t real NOT NULL,
									FOREIGN KEY (recording_id) REFERENCES recordings (id),
									FOREIGN KEY (trial_id) REFERENCES trials (id),
									FOREIGN KEY (cell_id) REFERENCES cells (id)
								); """
								

sql_create_behavior_table = """ CREATE TABLE IF NOT EXISTS behavior (
									id integer PRIMARY KEY,
									trial_id integer NOT NULL,
									session_id integer NOT NULL,
									sacc_X real,
									sacc_Y real,
									sacc_angle integer,
									FOREIGN KEY (trial_id) REFERENCES trials (id),
									FOREIGN KEY (session_id) REFERENCES sessions (id)
								); """

