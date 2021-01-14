#!/bin/bash

#SBATCH --job-name=test_matching_historic.job
#SBATCH --output=run.out
#SBATCH --error=run.err
#SBATCH --time=24:00:00
#SBATCH --mem=10000
#SBATCH --qos=normal
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jurriaanberger98@gmail.com
#SBATCH --partition=gpu2
#SBATCH -a 0-3
#SBATCH --account=um_dke

DATES=(2020_09_01,2020_09_01 2020_09_02,2020_09_01 2020_09_03,2020_09_02 2020_09_04,2020_09_03)

myarg1=${DATES[`expr $SLURM_ARRAY_TASK_ID % ${#DATES[@]}`]}

python3 BusProject/main.py $myarg1