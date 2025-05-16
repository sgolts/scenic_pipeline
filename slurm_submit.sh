#!/bin/bash

#SBATCH --job-name=scenic_run
#SBATCH --account=indikar1
#SBATCH --partition=standard
#SBATCH --mail-user=sgolts@umich.edu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mem=100G
#SBATCH --time=24:00:00
#SBATCH --nodes=1                     
#SBATCH --ntasks=1                    
#SBATCH --cpus-per-task=32

module load openjdk
module load singularity
export PATH="/nfs/turbo/umms-indikar/Sarah/tools/nextflow_1:$PATH"

python pipeline_runner.py --overwrite 
