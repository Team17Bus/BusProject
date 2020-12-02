#!/bin/bash

#SBATCH --job-name=run_all_lines.job
#SBATCH --output=run.out                      
#SBATCH --error=run.err                       
#SBATCH --time=00:01:30                         
#SBATCH --mem=200                               
#SBATCH --qos=normal
#SBATCH --mail-type=ALL
#SBATCH --mail-user=evavanspam@gmail.com    
#SBATCH --partition=gpu2
#SBATCH -a 0-3

LINES=(182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,2,20,200,201 202,203,204,206,207,208,209 210,211,212,213,217,218,219,22,220,221,222,225,23,234)

arg=${LINES[`expr $SLURM_ARRAY_TASK_ID % ${#LINES[@]}`]}
python3 script_live.py 40 $arg
