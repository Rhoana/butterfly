#!/bin/bash
#
# add all other SBATCH directives here...
#
#SBATCH -p cox
#SBATCH -n 1 # Number of cores
#SBATCH -N 1 # Ensure that all cores are on one machine
#SBATCH --gres=gpu
#SBATCH --mem=8000
#SBATCH -t 10-12:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=john@hoff.in
#SBATCH -o /n/coxfs01/thejohnhoffer/h5_tiles/2017_04_25/h5_%a.out
#SBATCH -e /n/coxfs01/thejohnhoffer/h5_tiles/2017_04_25/h5_%a.err

source new-modules.sh
module load Anaconda/2.5.0-fasrc01
module load gcc/4.9.0-fasrc01

module load cuda/7.5-fasrc01
module load cudnn/7.0-fasrc01

module load opencv/3.0.0-fasrc04

# custom HDF5 lib
export LIBRARY_PATH=/n/home05/haehn/nolearncox/src/hdf5-1.8.17/hdf5/lib:$LIBRARY_PATH
export LD_LIBRARY_PATH=/n/home05/haehn/nolearncox/src/hdf5-1.8.17/hdf5/lib:$LD_LIBRARY_PATH
export CPATH=/n/home05/haehn/nolearncox/src/hdf5-1.8.17/hdf5/include:$CPATH
export FPATH=/n/home05/haehn/nolearncox/src/hdf5-1.8.17/hdf5/include:$FPATH

source /n/home05/haehn/nolearncox/bin/activate

# Make graph directory
mkdir -p /n/coxfs01/thejohnhoffer/h5_tiles/2017_04_25
# we are working
cd /n/coxfs01/thejohnhoffer/2017/butterfly/scripts/h5_tile_test
python record_data.py ${SLURM_ARRAY_TASK_ID}

# end of program
exit 0;
