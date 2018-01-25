from __future__ import division
import sqlite3
from pickle import load
from manage_db import *
from numpy import *
from analyses import *
from scipy.stats import zscore

db_file = "data/CSHL_assignment_v1.db"

conn = sqlite3.connect(db_file)


x=get_behavior(conn).dropna()
error_to_target=circdist(x["stimulus"]/9.*2*pi,x["sacc_angle"])


cell_id = 3158
df_del=get_spikes_cell_interval(conn,cell_id,[1.5,4.5])
tc_del = df_del.groupby("stimulus").count()["spike_t"][:-1]


subplot(1,2,1)
title("error to target \n (unorrected for systematic biases)")
hist(error_to_target,bins=linspace(-pi,pi,20))
xlim([-pi,pi])

subplot(1,2,2)
title("tuning during delay of example cell")
plot(zscore(tc_del),label=str(cell_id))
plot(range(8),zeros(8),"k--")
legend()
ylabel("z-scored tuning")
xlabel("stimulus")

tight_layout()
