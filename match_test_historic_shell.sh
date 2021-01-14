#!/bin/bash

#SBATCH --job-name=test_matching_historic.job
#SBATCH --output=test.out
#SBATCH --error=test.err
#SBATCH --time=00:15:00
#SBATCH --mem=10000
#SBATCH --qos=normal
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jurriaanberger98@gmail.com
#SBATCH --partition=gpu2
#SBATCH -a 0-1
#SBATCH --account=um_dke

DATES=(2020_09_01,2020_09_01 2020_09_02,2020_09_01)

myarg1=${DATES[`expr $SLURM_ARRAY_TASK_ID % ${#DATES[@]}`]}

python3 BusProject/main.py $myarg1