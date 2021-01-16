import scipy.cluster.hierarchy as shc
from sklearn.cluster import AgglomerativeClustering
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler

normalize = True   # scale values to be in interval [0, 1]
standardize = False  # let data follow gaussian distr

data = pd.read_csv('delays_edges_2020_09_05.csv')
FEATURES = 'stop_to_loc', 'avg_delay_diff_sec', 'line', 'sched_time'    # if multiple days: include sched_date

features_used = ['avg_delay_diff_sec', 'sched_time']

def time_to_sec(t):
    t_split = t.split(':')
    h, m, s = t_split
    return int(h) * 3600 + int(m) * 60 + int(s)

if 'sched_time' in features_used:
    data.loc[:, 'sched_time'] = (data.loc[:, 'sched_time']).apply(time_to_sec)

data = data.loc[:, features_used].values

for i in range(data.shape[1]):
    data = data[abs(data[:, i]) != np.inf]


# normalize
if normalize:
    scaler_norm = MinMaxScaler()
    data = scaler_norm.fit_transform(data)

# standardize
if standardize:
    scaler_std = StandardScaler()
    data = scaler_std.fit_transform(data)



plt.figure(figsize=(10, 7))
plt.title("Delays Dendograms")
dend = shc.dendrogram(shc.linkage(data, method='ward'))
plt.show()
plt.savefig('dendrogram.png')

cluster = AgglomerativeClustering(n_clusters=5, affinity='euclidean', linkage='ward')
cluster.fit_predict(data)

plt.figure(figsize=(10, 7))
plt.scatter(data[:, 0], data[:, 1], c=cluster.labels_, cmap='rainbow')
plt.savefig('scatter.png')
plt.show()