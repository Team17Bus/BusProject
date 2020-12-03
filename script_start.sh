#!/bin/bash
#SBATCH --job-name=script_start.job
#SBATCH --output=start.out
#SBATCH --error=start.err
#SBATCH --time=09:00:00
#SBATCH --mem=1G
#SBATCH --qos=normal
#SBATCH --mail-type=ALL
#SBATCH --mail-user=evavanspam@gmail.com
python3 script_start.py
