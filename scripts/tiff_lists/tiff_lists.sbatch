#!/bin/bash
#
# add all other SBATCH directives here...
#
#SBATCH -p holyseasgpu
#SBATCH -n 1 # Number of cores
#SBATCH -N 1 # Ensure that all cores are on one machine
#SBATCH --mem=16000
#SBATCH -t 10-12:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=john@hoff.in
#SBATCH -o /n/coxfs01/thejohnhoffer/tiff_lists/tiff_%a.out
#SBATCH -e /n/coxfs01/thejohnhoffer/tiff_lists/tiff_%a.err

source new-modules.sh
module load python/2.7.11-fasrc01
conda create -n h5_tile --clone="$PYTHON_HOME"
source activate h5_tile
pip install --upgrade numpy
pip install --upgrade h5py
pip install --upgrade tifffile

TOTAL_RUNS=4
TIFF_JSON="/n/coxfs01/leek/results/2017-04-19_R2B1V3/boss/boss.json"

# we are working
cd /n/coxfs01/thejohnhoffer/2017/butterfly/scripts/tiff_lists
python tiff2h5.py ${TIFF_JSON} ${SLURM_ARRAY_TASK_ID} -r ${TOTAL_RUNS}

# end of program
exit 0;
