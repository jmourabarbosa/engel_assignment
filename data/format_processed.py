from __future__ import division
from numpy import *
from matplotlib.pylab import *
from pickle import load,dump
from scipy.io import savemat
from math import atan2

f=open("behavior_sessions.pickle")
beh=load(f)


## original dataset of delay neurons
f=open("neural_data.pickle","r")
data_d=load(f)
f.close()

## all neurons
f=open("all_neurons.pickle","r")
data_all_d=load(f)
f.close()

sacc_session_d = loadtxt("EyeStat.TXT",usecols=(0,),dtype='|S15')
sacc_data_d = loadtxt("EyeStat.TXT",usecols=(1,2,3,4,5,6,7))
sacc_session_nd = loadtxt("EyeStatNonDelay.TXT",usecols=(0,),dtype='|S15')
sacc_data_nd = loadtxt("EyeStatNonDelay.TXT",usecols=(1,2,3,4,5,6,7))


d_neurons = array([d["neuron"] for d in data_d])
d_sessions = array([d["session"] for d in data_d])

all_neurons = array([d["neuron"] for d in data_all_d])
all_sessions = array([d["session"] for d in data_all_d])
all_beh = array([d["INDX"] for d in data_all_d])

all_monkey = amap(lambda x: x[:3],all_sessions)

delay_idx = []
for n,session in enumerate(d_sessions):
    neuron=d_neurons[n]
    if int(session[-1:])>1:
        session = session[:-1]+"1"
    delay_idx += intersect1d(find(all_sessions == session),find(all_neurons == neuron)).tolist()



# no -2,-3
odr_idx = array([int(s[-1:]) for s in all_sessions])==1

# remove any session that has more than 8 cues
cues_8_idx=find(array([max(b[:,0]) for b in all_beh])<9)
odr_idx = intersect1d(find(odr_idx),cues_8_idx)

# all neurons
final_all =array(data_all_d)[odr_idx]

# only non delay
final_non_delay = array(data_all_d)[setdiff1d(odr_idx,delay_idx)]

#only delay
final_delay = array(data_all_d)[intersect1d(odr_idx,delay_idx)]


delay_vector = [i in intersect1d(odr_idx,delay_idx) for i in odr_idx]

behavior_header = ["cue","repeat","STRT","FIXON","CUEON","CUEOFF","FIXOFF","SACON","TRLEND","SPIKE","sacc_x","sacc_y","sacc_ang"]        

spikes = [d["D"] for d in final_all]
behavior = [d["INDX"] for d in final_all]
sessions = [d["session"] for d in final_all]

def xy_to_ang(xy):
	return amap(lambda x,y: atan2(y,x),xy[:,0],xy[:,1])


def sort_by_col(data,col):
	data=array(data)
	data=data[np.argsort(data[:,col])]
	return data

sacc_diff_d=[[] for _ in range(len(sessions))]
sacc_diff_nd=[[] for _ in range(len(sessions))]

for s,session in enumerate(sessions):
	session_d_idx = find(sacc_session_d==session)
	session_nd_idx = find(sacc_session_nd==session)
	if (len(behavior[s])- len(session_d_idx))==0:
		#sacc_diff_d.append(sum(sort_by_col(behavior[s],2)[:,:2] - sort_by_col(sacc_data_d[session_d_idx],2)[:,:2]))
		sacc_diff_d[s].append(session_d_idx)
		if shape(behavior[s])[1] == 10:
			behavior[s] = column_stack([behavior[s],sacc_data_d[session_d_idx,3:5],xy_to_ang(sacc_data_d[session_d_idx,3:5])])
	if (len(behavior[s])- len(session_nd_idx))==0:
		#sacc_diff_nd.append(sum(sort_by_col(behavior[s],2)[:,:2] - sort_by_col(sacc_data_nd[session_nd_idx],2)[:,:2]))
		sacc_diff_nd[s].append(session_nd_idx)
		if shape(behavior[s])[1] == 10:
			behavior[s] = column_stack([behavior[s],sacc_data_nd[session_nd_idx,3:5],xy_to_ang(sacc_data_nd[session_nd_idx,3:5])])

## find neuron(s) without any match
no_match_idx =amap(lambda x: shape(x)[1],behavior)<13

for i in no_match_idx:
	beh=zeros([shape(behavior[i])[0],3])
	behavior[i] = column_stack([behavior[i],beh])
	
savemat("christos_ODR.mat",{"spiketimes": spikes, "behavior": behavior, "session_ID": sessions, "delay_neurons": delay_vector, "monkey_ID": all_monkey, "behavior_header": behavior_header})
