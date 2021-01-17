from process_matched_data import edges_transform
from os import listdir
import sys

# input arguments
# 1. folder in which matched arrivals are located
# 2. folder to which output files should be written

kwargs = sys.argv  # provide lines as arguments
assert len(kwargs) == 3, "Please only provide 2 arguments (folder in which matched arrivals are located & folder to which output files should be written)"
FOLDER_IN, FOLDER_OUT = kwargs[1], kwargs[2]

files = listdir(FOLDER_IN)

files_done = listdir(FOLDER_OUT)

for f in files:
    if not 'delays_edges_' + f in files_done:
        edges_transform(f, FOLDER_IN, FOLDER_OUT)
