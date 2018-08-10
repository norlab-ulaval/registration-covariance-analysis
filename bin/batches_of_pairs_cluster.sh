#!/usr/bin/env bash

#SBATCH --account=rpp-corbeilj
#SBATCH --time=03:00:00
#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=256M
#SBATCH --ntasks-per-node 1

source activate torch
compute_batches_of_pairs --begin 0 --end 10 --location 00 -n 100 $HOME/project/dlandry/dbs/db_kitti $HOME/project/dataset/sequences/00/

