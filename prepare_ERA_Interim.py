# Data wrangling libs
import xarray as xr


interim_dir = 'data/ERAInterim/'  # for consistency with other datasets, we will copy the files here
# File naming conventions
interim_prefix = 'ERAInterim_'

file_suffix_eraI = "_monthly_1979_2015.nc"  # ERA Interim has a different time range

# Split old ERA Interim data into variables so that the data matches the new ERA5/ERA5L/MERRA-2 structure
# DONE- no need to redo, move to data preparation step.  
interim_dir_orig = '../../SCIENCE/HMA/data/ERAInterim/'

# load the data to see what we have
ds = xr.open_dataset(interim_dir_orig + 'output.nc')
#print(ds)
ds2 = xr.open_dataset(interim_dir_orig + 'output_P_snow_E.nc')
#print(ds)
ds3 = xr.open_dataset(interim_dir_orig + 'output_pt_e_sf.nc')
#print(ds)
# all contain the attributes sf (snow), e, and tp, with various time stamps (800something, 423, 444), and output is global whereas the other are clipped to 15-55 /60-130 degrees
# We try to recreate the clipped datasets from output.nc. It seems that output.nc contains double timestamps. Clean it up. 
#print(ds.time.values) 
# the time values are at T00 and T12 for each first day in the month, which is likely the source of the duplication. We can just take the first timestamp for each month to get a clean monthly dataset.
ds_clean = ds.isel(time=slice(0, None, 2)) # take every second timestamp starting from the first one
#print(ds_clean.time.values) # now we should have only one timestamp per month, at T00.
#print(ds_clean)
# now make a spatial subset for the data to match the region of interes (+5 deg in all directions), and split into the three variables of interest (sf, e, tp)
# the lat/lon dimensions are called latitude/longitude in the dataset, so we need to use those names for slicing
ds_subset = ds_clean.sel(longitude=slice(lon_min-5, lon_max+5), latitude=slice(lat_max+5, lat_min-5)) # note that latitude is in reverse order, so we need to slice from max to min
print(ds_subset)
ds_sf = ds_subset['sf']
ds_e = ds_subset['e']
ds_tp = ds_subset['tp']
print(ds_sf)
print(ds_e)
print(ds_tp)
# Now we can save these as separate netCDF files with the same naming convention as the other reanalysis products, so that they can be easily loaded and compared in the later analysis steps.
ei_suffix = '_monthly_1979_2015.nc' # same suffix as the other datasets
ds_sf.to_netcdf(interim_dir + interim_prefix + 'sf' + ei_suffix)
ds_e.to_netcdf(interim_dir + interim_prefix + 'e' + ei_suffix)
ds_tp.to_netcdf(interim_dir + interim_prefix + 'tp' + ei_suffix)