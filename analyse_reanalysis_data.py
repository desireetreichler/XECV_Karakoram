# This file is an example how ERA5 data (downloaded in a separate script download_era5.py) 
# could be analysed to show trends/changes over the Karakoram area

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
plt.ion()  # Enable interactive mode

# Load the NetCDF file
data_file = 'era5_1990_2009_tp.nc'
ds = xr.open_dataset(data_file)

# Check the dataset contents
print(ds)

# Select total_precipitation variable
total_precipitation = ds['tp'] # this is total_precipitation

# Check the coordinates
print(total_precipitation.coords)

# Extract the month from the existing valid_time coordinate
total_precipitation = total_precipitation.assign_coords(month=total_precipitation['valid_time'].dt.month)
total_precipitation = total_precipitation.assign_coords(year=total_precipitation['valid_time'].dt.year)

# Extract values for May (5), June (6), and July (7)
summer_months = total_precipitation.where(total_precipitation['month'].isin([5, 6, 7, 8, 9]), drop=True)


# Aggregate May, June, and July for each year, calculating the mean
summer_sum = summer_months.groupby('year').sum(dim='valid_time')
summer_avg = summer_months.groupby('year').mean(dim='valid_time')

# Calculate decadal averages
decadal_avg_2000s = summer_sum.sel(year=slice(2000, 2009)).mean(dim='year')
decadal_avg_2010s = summer_sum.sel(year=slice(2010, 2019)).mean(dim='year')

# Calculate the difference between the two decades
difference = (decadal_avg_2010s - decadal_avg_2000s)*1000  # precipitation is in meters
print(difference)
fraction = (decadal_avg_2000s/decadal_avg_2010s)*100  # in percent

# Plotting the difference
plt.figure(figsize=(12, 6))
difference.plot(cmap='coolwarm_r', vmin=-15, vmax=15, 
                cbar_kwargs={'label': 'Difference in Total Precipitation (mm)'})
plt.title('Difference in Total Precipitation (2010-2019) - (2000-2009)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid()
plt.savefig('decadal_difference_summer_tp_ERA5Land_15.jpg')
plt.show()


# Plotting the difference
plt.figure(figsize=(12, 6))
fraction.plot(cmap='coolwarm_r', cbar_kwargs={'label': 'Change in Total Precipitation (%)'})
plt.title('Change in Total Precipitation  - (2000-2009) / (2010-2019)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid()
plt.savefig('decadal_changefraction_summer_tp_ERA5Land.jpg')
plt.show()