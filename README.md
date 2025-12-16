# GSA O3MAT EMBER Study Scripts

This repository contains documentation and scripts used for the GSA O3MAT EMBER study. The codebase is organized into two main components: Fire Emissions processing and NACC model workflows.

## Directory Structure

### 1. FireEmissions
Contains tools, scripts, and documentation for processing fire emissions data, including BlueSky Pipeline (BSP) configurations, HMS data processing, and SMOKE model run scripts.

*   **`bsp/`**: BlueSky Pipeline scripts and configurations.
    *   Contains JSON/YAML config files (`bsp_config_*.json`, `configue_bluesky.yml`).
    *   Scripts for running BSP (`run_bsp.csh`) and post-processing.
    *   Utilities for adding HAPs and generating FF10 files.
*   **`finn/`**: Scripts for processing Fire INventory from NCAR (FINN) data (`combine_finn.py`).
*   **`fire_activities/`**: Tools for handling fire activity data.
    *   HMS (Hazard Mapping System) processing scripts (`get_HMS.py`, `HMS_Processing.ipynb`).
    *   Perimeter handling (`get_nbac_perimeters.csh`, `setup_perimeters.v2.csh`).
*   **`sf2py/`**: Source code and data sources for preparing inputs, likely bridging SmartFire or similar tools to Python workflows.
*   **`smoke/`**: SMOKE model run scripts for various fire sectors.
    *   Scripts for Wildfires (`ptfire-wild`) and Prescribed burns (`ptfire-rx`).
    *   Regional scripts for Canada and Mexico.
    *   Configuration files for exclusions and directory definitions.
*   **Documentation**: `EMBER Fire Technical Documentation.docx` provides detailed technical information.

### 2. NACC
Contains scripts and instructions for running the NACC (NOAA's Assimilation and Climate Change) model components, specifically related to FV3 and cloud workflows.

*   **Documentation**: `HOW_TO_run_NACC_cloud.README` provides instructions for running NACC in the cloud.
*   **Data Management**:
    *   `aws_pull_data.csh`: Script to retrieve data from AWS.
    *   `batch_merge_nacc.csh` & `merge.sh`: Scripts for merging model outputs.
*   **Execution**:
    *   `compile.NACC.csh`: Script to compile the NACC model.
    *   `parallel.EMBER-run-nacc-fv3.csh`: Script for parallel execution of NACC-FV3.
*   **Quality Assurance**: `QA_Check.ipynb` for validating outputs.

## Usage

Please refer to the specific README files or documentation within each subdirectory for detailed usage instructions.
