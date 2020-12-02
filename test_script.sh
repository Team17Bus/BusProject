#!/bin/bash
#SBATCH --job-name=test_script.job
#SBATCH --output=test.out
#SBATCH --error=test.err
#SBATCH --time=00:02:00
#SBATCH --mem=200
#SBATCH --qos=normal
#SBATCH --mail-type=ALL
#SBATCH --mail-user=evavanspam@gmail.com
python3 script_live.py 70 1,10,102,103,104,105,106,107,108,109,11,110 
