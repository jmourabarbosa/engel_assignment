import sqlite3
from pickle import load
from manage_db import *
from numpy import *

## This code speed/data use can be improved. 
## In general, I prefer to make this code easier to understand or didn't have time to do it, but possible improvements:
# - I do one or more passes through the original data for each table. One big pass through the data would improve dramatically
# - I create a dictionary for all the data, then submit/commit by calling insert_many_items()
#	* The data here is very tiny, but for real data I'd need to call insert_many_items() with smaller chunks several times per table
# - I use real values for floats (which yse 8bytes), but I could transform them in integers of fewer bytes. 
#	* E.g. an angle could be stored in 1byte integer


f=open("data/behavior_sessions.pickle")
beh_data=load(f)

f=open("data/neural_data.pickle")
neural_data=load(f)

db_file = "data/CSHL_assignment_v1.db"

# if there is no database, it creates one
conn = sqlite3.connect(db_file)

# for in memory database
# conn = sqlite3.connect(':memory:')


# initialize database
init_db(conn)

id_neuron_sessions_subj = array([[d["neuron"],d["session"],d["session"][:3]] for d in neural_data])

## POPULATE subjects table
table ="subjects"
data = {"id": [], "n_sessions": []}

for s in unique(id_neuron_sessions_subj[:,2]):
	n_sessions = sum(id_neuron_sessions_subj[:,2] == s)
	data["id"].append(s)
	data["n_sessions"].append(n_sessions)

cur =insert_many_items(conn,table,data)


## POPULATE cells table
table ="cells"
data = {"id": array(id_neuron_sessions_subj[:,0],dtype="int"), "cell_type": ones(len(id_neuron_sessions_subj))}

insert_many_items(conn,table,data)

## POPULATE sessions table
table ="sessions"
sessions = beh_data.keys()
data = {"id": sessions, "subject_id": [], "n_cells": []}

for session_id in sessions:
	n_cells = sum(id_neuron_sessions_subj[:,1] == session_id)
	data["subject_id"].append(session_id[:3])
	data["n_cells"].append(n_cells)

insert_many_items(conn,table,data)

## POPULATE trials table
table = "trials"
data = {"session_id": [], "stimulus": []}
data_rec= {"cell_id": [], "session_id": [], "trial_id": []}
data_beh = {"trial_id": [], "session_id": [], "sacc_x": [], "sacc_y": [], "sacc_angle": []}

i=1
for session_id,values in beh_data.items():
	stims = values["trials"][:,0].tolist()
	sessions = [session_id]*len(stims)
	data["session_id"]+=sessions
	data["stimulus"]+=stims

	# improve speed by preparing data for recordings
	all_idx=where(session_id  == id_neuron_sessions_subj[:,1])[0]
	if len(all_idx) > 0:
		for idx in all_idx:
			cells_id= [id_neuron_sessions_subj[idx,0]]*len(stims)
			data_rec["cell_id"]+=cells_id
			data_rec["session_id"]+=sessions
			data_rec["trial_id"]+=range(i,i+len(stims))

	# improve speed by preparing data for behavior
	data_beh["trial_id"]+=range(i,i+len(stims))
	data_beh["session_id"]+=sessions
	data_beh["sacc_x"]+= beh_data[session_id]["trials"][:,3].tolist()
	data_beh["sacc_y"]+= beh_data[session_id]["trials"][:,4].tolist()
	data_beh["sacc_angle"]+=beh_data[session_id]["trials"][:,6].tolist()
	i+=len(stims)

c=insert_many_items(conn,table,data)


## POPULATE recordings table
table = "recordings"
data = data_rec

insert_many_items(conn,table,data)


## POPULATE spikes table
table = "spikes"
data = {"recording_id": [], "trial_id": [], "cell_id": [], "spike_t": []}

for n,cell_id in enumerate(id_neuron_sessions_subj[:,0]):
	idx = array(data_rec["cell_id"]) == cell_id
	trials = array(data_rec["trial_id"])[idx].tolist()
	recs = where(idx)[0].tolist()
	cells = [cell_id]*len(trials)
	assert (len(trials) - neural_data[n]["D"].shape[0]) == 0
	for t,t_id in enumerate(trials):
		spikes = neural_data[n]["D"][t]
		spikes = spikes[spikes>0].tolist()
		trial_id = [t_id]*len(spikes)
		rec_id = [recs[t]]*len(spikes)
		cell_id = [cells[t]]*len(cells)
		data["spike_t"]+=spikes
		data["trial_id"]+=trial_id
		data["recording_id"]+=rec_id
		data["cell_id"]+=cell_id

insert_many_items(conn,table,data)

## POPULATE behavior table
table = "behavior"
data=data_beh
insert_many_items(conn,table,data)




