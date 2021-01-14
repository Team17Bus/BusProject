#!/bin/bash

#SBATCH --job-name=schedule_online.job
#SBATCH --output=schedule.out
#SBATCH --error=schedule.err
#SBATCH --time=00:30:00
#SBATCH --mem=10000
#SBATCH --qos=normal
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jurriaanberger98@gmail.com
#SBATCH --account=um_dke


python3 BusProject/online_schedules_with_stop_seq.py 16dec