#SBATCH --job-name=edges_transform.job
#SBATCH --output=edges.out
#SBATCH --error=edgeserr
#SBATCH --time=00:45:00
#SBATCH --mem=2000
#SBATCH --qos=normal
#SBATCH --mail-type=ALL
#SBATCH --mail-user=evavanspam@gmail.com
#SBATCH --partition=gpu2
#SBATCH -a 0-3

FILES=(online_matched_data/2020_12_07.csv,online_data_edges online_matched_data/2020_12_08.csv,online_data_edges online_matched_data/2020_12_09.csv,online_data_edges online_matched_data/2020_12_10.csv,online_data_edges online_matched_data/2020_12_11.csv,online_data_edges online_matched_data/2020_12_13.csv,online_data_edges online_matched_data/2020_12_14.csv,online_data_edges online_matched_data/2020_12_16.csv,online_data_edges online_matched_data/2020_12_17.csv,online_data_edges online_matched_data/2020_12_18.csv,online_data_edges online_matched_data/2020_12_19.csv,online_data_edges)

myarg=${FILES[`expr $SLURM_ARRAY_TASK_ID % ${#FILES[@]}`]}

python3 transform_to_edges_wrapper.py $myarg