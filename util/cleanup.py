import os
import shutil

# First, cleanup traindata

train_data_dir = "../RL/traindata"
archive_data_dir = "../RL/archivedata"
filenames = os.listdir(train_data_dir)
for filename in filenames:
    if filename.split(".")[-1] != 'pkl':
        continue
    old_filepath = os.path.join(train_data_dir, filename)
    new_filepath = os.path.join(archive_data_dir, filename)
    os.replace(old_filepath, new_filepath)

# Next, archive the sim data
sim_data_dir = "../data"
sim_archive_data_dir = "../sim/archivedata"
dirnames = os.listdir(sim_data_dir)
for dirname in dirnames:
    if "." in dirname:
        continue
    old_filepath = os.path.join(sim_data_dir, dirname)
    new_filepath = os.path.join(sim_archive_data_dir, dirname)
    shutil.move(old_filepath, new_filepath)
    