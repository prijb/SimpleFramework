# SimpleFramework
Simple framework for processing files throuhg htcondor.

</br>
Setup in `CMSSW_14_0_6_patch1` (requires a valid voms account)
```
cmsrel CMSSW_14_0_6_patch1
cd CMSSW_14_0_6_patch1/src
git clone git@github.com:prijb/SimpleFramework.git <project_name>
source setup.sh
```

Preprocessing code should be placed in the `Preprocess` directory. The script should be mentioned in `Preprocess/preprocess_dataset.py` as the `script` variable.

To run a preprocessing job
```
python3 Preprocess/preprocess_dataset.py -i <input_directory> -o <output_directory> --prefix <input_prefix> <additional flags>
```
