# Natively downloaded MERRA-2 data (in the folder data/MERRA2) is organised in single files per month
# and stems from three collections
# we want to merge these into one file per variable (and save in a new folder data/MERRA2_merged)
import xarray as xr
import os
import re

os.makedirs('data/MERRA2_merged', exist_ok=True)


# there are three name patterns, corresponding to the three collections
# patterns: 
pattern1 = "M*slv*.nc4" # ? is a wildcard for one letter
pattern2= "MERRA2_*lnd*nc4.nc4"
pattern3 = "MERRA2_*flx*nc4.nc4"

# read the list of files in the MERRA2 folder matching pattern 1, pattern 2, and pattern 3
files = os.listdir('data/MERRA2/')
files_pattern1 = [f for f in files if f.startswith("M") and "slv" in f and f.endswith(".nc4")]
files_pattern2 = [f for f in files if f.startswith("MERRA2_") and "lnd" in f and f.endswith("nc4.nc4")]
files_pattern3 = [f for f in files if f.startswith("MERRA2_") and "flx" in f and f.endswith("nc4.nc4")]
for pattern in [files_pattern1, files_pattern2, files_pattern3]:
    # load a random file matching the first pattern to get the variable names and dimensions
    sample_file = pattern[0]
    ds_sample = xr.open_dataset(os.path.join('data/MERRA2', sample_file))
    variables_pattern = list(ds_sample.data_vars.keys())
    dimensions_pattern  = list(ds_sample.dims.keys())
    print(variables_pattern)
    print(dimensions_pattern)
    # 
    # for all variables in the first pattern, load all files matching the first pattern, extract the variable, and merge into one dataset
    # using the file name pattern MERRA2_{variable}_monthly_1981_2025.nc
    for variable in variables_pattern:
        print(f'Processing variable: {variable}')
        datasets = []
        for f in pattern:
            ds = xr.open_dataset(os.path.join('data/MERRA2', f))
            ds_variable = ds[variable]
            datasets.append(ds_variable)
        ds_merged = xr.concat(datasets, dim='time')
        # save the merged dataset to a new file
        output_file = os.path.join('data/MERRA2_merged', f'MERRA2_{variable}_monthly_1981_2025.nc')
        ds_merged.to_netcdf(output_file)