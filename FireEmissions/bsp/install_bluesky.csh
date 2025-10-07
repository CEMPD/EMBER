#!/bin/tcsh

## NOTE: source this script in stead of excuting it: source BLUESKY.configure.csh 
#source "/nas/longleaf/home/tranhuy/software/pkg/miniconda3/etc/profile.d/conda.csh"
module load anaconda

# After testing many, this is the only configure file that work, do not change anything in this except value after "name: "
setenv BSPCONFIG "/proj/ie/proj/GSA-EMBER/BlueSky/configue_bluesky.yml"
set env_name = `awk '/^name:/ {print $2; exit}' $BSPCONFIG`
set env_path = "/proj/ie/proj/GSA-EMBER/BlueSky/$env_name"

# Get the list of conda environments
set env_list = (`conda env list | awk '{print $1}'`)

# Check if the environment name exists in the list
if (`echo $env_list | grep -w $env_path` != "") then
  conda deactivate
  conda activate $env_path
# setenv BINDIR  `which pip | xargs dirname`
# alias bps `${BINDIR}/bsp`
# setenv PATH "/nas/longleaf/home/tranhuy/software/pkg/miniconda3/envs/$env_name/bin:$PATH"
else
  echo "conda env $env_path is not found. Set it up first (could take some time) ... "
  conda env create --prefix=$env_path -f $BSPCONFIG
  conda activate $env_path
  pip install --timeout 60 --no-binary gdal --extra-index https://pypi.airfire.org/simple bluesky==4.4.1 # large enough --timeout to let pip regcognize bluesky tarball
  ## Reactivate env to add BSP binaries to $PATH
  conda deactivate
  conda activate $env_path
endif

## NOTE: To update a BSP package post-installation, e.g., eflookup, activate BSP env first, then
# pip install --extra-index https://pypi.airfire.org/simple eflookup==5.0.1  
