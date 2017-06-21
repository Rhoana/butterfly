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
#SBATCH -o /n/coxfs01/thejohnhoffer/2017/butterfly/scripts/h5_tile_test/results/64K_h5_%a.out
#SBATCH -e /n/coxfs01/thejohnhoffer/2017/butterfly/scripts/h5_tile_test/results/64K_h5_%a.err

source new-modules.sh
module load python/2.7.11-fasrc01
conda create -n h5_tile --clone="$PYTHON_HOME"
source activate h5_tile
pip install --upgrade numpy
pip install --upgrade h5py

# Export name
export H5_EXPERIMENT=2017_06_21_64K_10trial

# we are working
cd /n/coxfs01/thejohnhoffer/2017/butterfly/scripts/h5_tile_test
python -u record_data.py ${SLURM_ARRAY_TASK_ID} 16

# end of program
exit 0;
