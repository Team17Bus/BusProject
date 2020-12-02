#!/bin/bash

#SBATCH --job-name=test_all_lines.job
#SBATCH --output=test.out
#SBATCH --error=test.err
#SBATCH --time=00:02:00
#SBATCH --mem=200
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --qos=normal
#SBATCH --mail-type=ALL
#SBATCH --mail-user=evavanspam@gmail.com

python3 script_live.py 20 1,10,102,103,104
python3 script_live.py 20 105,106,107,108,109
python3 script_live.py 20 11,110,111
wait
