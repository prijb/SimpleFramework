#This code runs a script over a whole dataset using HTCondor
import os
import argparse

#Get current directory
current_dir = os.getcwd()

#Argument parser
#Example submission command:
#python3 Preprocess/preprocess_dataset.py --input store/user/ppradeep/L1Scouting/L1ScoutingSelection/run383996_dijet/240903_120147/0000/ --output /vols/cms/pb4918/L1Scouting/Sep24/Analysis/CMSSW_14_1_0_pre4/src/Preprocess/output/Data --nfiles -1 --grid --prefix davs://gfe02.grid.hep.ph.ic.ac.uk:2880/pnfs/hep.ph.ic.ac.uk/data/cms/
parser = argparse.ArgumentParser(description='Preprocess Dataset')
parser.add_argument('--input', '-i', type=str, help='Input dataset path')
parser.add_argument('--output', '-o', type=str, help='Output dataset path')
parser.add_argument('--nfiles', '-n', default=-1, type=int, help='Number of files to process')
parser.add_argument('--start', '-s', default=0, type=int, help='Start file index')
parser.add_argument('--grid', '-g', action="store_true", help='Dataset is on the grid')
parser.add_argument('--prefix', '-p', default="davs://gfe02.grid.hep.ph.ic.ac.uk:2880/pnfs/hep.ph.ic.ac.uk/data/cms/", type=str, help='Grid prefix')

args = parser.parse_args()

# Script that's preprocessed
script = "Preprocess/preprocess_file.py"
dataset_input = args.input
# If grid, add prefix
if args.grid:
    #prefix = "davs://gfe02.grid.hep.ph.ic.ac.uk:2880/pnfs/hep.ph.ic.ac.uk/data/cms/"
    #prefix = "root://gfe02.grid.hep.ph.ic.ac.uk/pnfs/hep.ph.ic.ac.uk/data/cms/"
    #prefix = root://eosuser.cern.ch/
    prefix = args.prefix
    dataset_input = prefix + dataset_input   

#Make a directory for the output path
os.makedirs(args.output, exist_ok=True)

#Make a directory for condor submission 
os.makedirs("condor_submission", exist_ok=True)

#Make a directory for condor logs
os.makedirs("condor_submission/logs", exist_ok=True)


#Make the input arguments file for the condor job
with open("condor_submission/preprocess_args.txt", "w") as f:
    #Count the number of files in the dataset
    files = None
    if args.grid == True:
        #Subdirectory structure
        #subdirs = os.popen(f"gfal-ls {dataset_input}").read().strip().split("\n")
        #print("Number of subdirectories: {}".format(len(subdirs)))
        #files = []
        #for subdir in subdirs:
        #    files += os.popen(f"gfal-ls {dataset_input}/{subdir}").read().strip().split("\n")
        
        files = os.popen(f"gfal-ls {dataset_input}").read().strip().split("\n")
    else:
        files = os.popen(f"ls {dataset_input}").read().strip().split("\n")
    #Only retain .root files
    files_filtered = [file for file in files if "root" in file]
    n_files_dataset = len(files_filtered)

    #Number of files to process
    n_files_to_process = args.nfiles
    if(args.nfiles > n_files_dataset):
        n_files_to_process = n_files_dataset
    elif(args.nfiles < 0):
        n_files_to_process = n_files_dataset
    else:
        n_files_to_process = args.nfiles

    #Set number of files to process to be half of the total number of files if the arg is -2
    if args.nfiles == -2:
        n_files_to_process = n_files_dataset//2
    
    #Now write the input arguments for the job submission
    start = args.start
    for i in range(n_files_to_process):
        file_index = start + i
        f.write(f"{dataset_input}/{files_filtered[file_index]} {args.output}/processed_{files_filtered[file_index]}\n")


#Create the wrapper file for the condor job
wrapper_file_content = f"""#!/bin/bash
#This wrapper runs the python script for running on a file
#Go to the CMSSW directory and set up the environment
cd $1
source /cvmfs/cms.cern.ch/cmsset_default.sh
source /vols/grid/cms/setup.sh
export X509_USER_PROXY=$1/condor_submission/cms.proxy
cmsenv
#Run the python script
python3 {script} -i $2 -o $3
"""

#Write and give execute permission to the wrapper file
with open(f"{current_dir}/Preprocess/preprocess_file_wrapper.sh", "w") as f:
    f.write(wrapper_file_content)
os.system("chmod +x Preprocess/preprocess_file_wrapper.sh")


#Create the HTCondor submit file
submit_file_content = f"""
universe = vanilla
executable = {current_dir}/Preprocess/preprocess_file_wrapper.sh
executable = {current_dir}/Preprocess/preprocess_file_wrapper.sh
arguments = {current_dir} $(infile) $(outfile)
output = condor_submission/logs/preprocess_$(Cluster)_$(Process).out
error = condor_submission/logs/preprocess_$(Cluster)_$(Process).err
log = condor_submission/logs/preprocess_$(Cluster)_$(Process).log
request_cpus = 1
request_memory = 1GB
use_x509userproxy = true
+MaxRuntime = 3600
queue infile, outfile from condor_submission/preprocess_args.txt
"""

with open("condor_submission/preprocess.submit", "w") as f:
    f.write(submit_file_content)


#Delete exist log files
os.system("rm condor_submission/logs/*")

# Run the condor job
os.system("condor_submit condor_submission/preprocess.submit")

# Remove the condor submission file
os.system("rm condor_submission/preprocess.submit")
        