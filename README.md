
# Radiation Load and Yield

## Description
This project is focused on calculating radiation load and yield. It includes various tools and scripts to perform these calculations.

## Usage
To use the tools and scripts provided in this project, follow the instructions in the respective files. Typically, you would run:
```bash
bash run_me.sh
```

The python scripts are to be considered tools subject to change. The *f files are FLUKA user routines for the FLUKA simulations.

## Repository Structure
The main repository structure is the following
```
├── tapering_coils_configurations     # Magnetic field maps
│   └─── HTS_v3_23_coils
│       ├── tapering
│       └── chicane
│   
│   
│   
├── src
│   ├── exe_mgdraw
│   └── emittance_calculator          # Postprocessing tools for calculating yiels
│       ├── testing
│       ├── fill_json.py
│       └── emittance_calculator.py
├── README.md
└── fluka_geometries                  # Contains only FLUKA inputfiles
   ├── target_taper
   ├── only_target
```
