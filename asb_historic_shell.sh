{\rtf1\ansi\ansicpg1252\cocoartf1671\cocoasubrtf600
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 \
#!/bin/bash\
\
#SBATCH --job-name=asb_historic.job\
#SBATCH --output=run.out\
#SBATCH --error=run.err\
#SBATCH --time=24:00:00\
#SBATCH --mem=5000\
#SBATCH --qos=normal\
#SBATCH --mail-type=ALL\
#SBATCH --mail-user=evavanspam@gmail.com\
#SBATCH --partition=gpu2\
#SBATCH -a 0-29\
\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0
\cf0 FILES = (2020_09_01.csv 2020_09_02.csv 2020_09_03.csv 2020_09_04.csv 2020_09_05.csv 2020_09_06.csv 2020_09_07.csv 2020_09_08.csv 2020_09_09.csv 2020_09_10.csv 2020_09_11.csv 2020_09_12.csv 2020_09_13.csv 2020_09_14.csv 2020_09_15.csv 2020_09_16.csv 2020_09_17.csv 2020_09_18.csv 2020_09_19.csv 2020_09_20.csv 2020_09_21.csv 2020_09_22.csv 2020_09_23.csv 2020_09_24.csv 2020_09_25.csv 2020_09_26.csv 2020_09_27.csv 2020_09_28.csv 2020_09_29.csv 2020_09_30.csv)\
\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0
\cf0 myarg=$\{FILES[`expr $SLURM_ARRAY_TASK_ID % $\{#FILES[@]\}`]\}\
python3 asb_historic.py <other_arg> $myarg\
\
\
\
}