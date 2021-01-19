import numpy as np
import pandas as pd

AS_BS_dist = pd.read_csv("/Volumes/KESU/Project_Bus/arrival_estimations/2020_09_03.csv_asbs_distances")

x = AS_BS_dist.iloc[:, 0]
y = AS_BS_dist.iloc[:, 1]

ratio = x / y
diff = np.abs(x - y)

greater_than_one_ratio = ratio[ratio > 1]
smaller_than_one_ratio = 1 / np.array(ratio[ratio <= 1])

ratio = np.concatenate([greater_than_one_ratio, smaller_than_one_ratio])

print(f'median ratio: {np.median(ratio)}')
print(f'average ratio: {np.average(ratio)}')
print(f'median diff: {np.average(diff)}')
print(f'average diff: {np.median(diff)}')
