#!/bin/bash

# copying sim files to be be downloaded into Hamilton
# making  a list of sim files in the current dir and saves the source path
get_sim_files() {
  local remote_dir=${1:-$PWD}
  local dirname=$(basename $remote_dir)  # ex:  JM_recoil0

  # find all  sim files
  find $remote_dir -type f \( \
    -name "*.BHMergers" -o \
    -name "*.BlackHoles" -o \
    -name "*.iord" -o \
    -name "*.log" -o \
    -name "*.param" -o \
    -name "*.sinklog" -o \
    -name "*.starlog" -o \
    -name "*.[0-9][0-9][0-9][0-9][0-9][0-9]" \
  \) | sed "s|^$remote_dir/||" > ~/sim_files_${dirname}.txt

  # save the src path so sync_from_mendel knows where to pull from
  echo "$remote_dir" > ~/sim_source_${dirname}.txt
  echo "Done! sim_files_${dirname}.txt and sim_source_${dirname}.txt are ready."
}

##################################################################################

# pulls sim files from Mendel into the current dir
# usage: sync_from_mendel JM_recoil0 or whatever name was printed in the function above 
# pulls sim files from Mendel into the current directory
# usage: sync_from_mendel JM_recoil0
sync_from_mendel() {
  local dirname=$1

  # read the source path saved by get_sim_files on Mendel
  local source_dir=$(ssh jmeftah@mendel.sdmz.amnh.org cat ~/sim_source_${dirname}.txt)

  # count files on Mendel (not locally)
  local total=$(ssh jmeftah@mendel.sdmz.amnh.org "wc -l < ~/sim_files_${dirname}.txt")
  echo "Syncing $total files from $source_dir ..."

  # rsync using the file list from Mendel
  rsync -rlgtvz -P --info=progress2 \
    --files-from=<(ssh jmeftah@mendel.sdmz.amnh.org cat ~/sim_files_${dirname}.txt) \
    jmeftah@mendel.sdmz.amnh.org:$source_dir .

  echo "Done! $total files synced from $source_dir"
}
