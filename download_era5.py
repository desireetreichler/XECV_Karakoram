# Example script to download ERA5 (atmospheric reanalysis) data
#---------------------------------------------------------
# Prerequisites: CDS api access https://cds.climate.copernicus.eu/how-to-api
# Dataset, variables, extent, time etc. can easily be adjusted.
# Example scripts for changed parameters are provided on the fly online,
# when changing parameters - e.g., https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-monthly-means?tab=download
# Local environment used: reanalysis (updated feb 2026)
    

import cdsapi
import os

# Create output directory if it doesn't exist
os.makedirs('data/ERA5', exist_ok=True)
os.makedirs('data/ERA5L', exist_ok=True)


# Note: ERA5 variable names differ slightly from ERA5-Land
# Some variables (like snowmelt, snow_evaporation) are not available in ERA5 single levels
for datasetname, dataset in zip(['ERA5','ERA5L'], ["reanalysis-era5-single-levels-monthly-means", "reanalysis-era5-land-monthly-means"]):
    for variable in [
            "2m_temperature",
            "snow_depth",
            "snow_depth_water_equivalent", # error
            "snowfall", # error
            "snowmelt",  # Not available in ERA5 single levels
            "snow_evaporation",  # Not available in ERA5 single levels
            "total_evaporation", # error
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "total_precipitation"
        ]:
        if datasetname == "ERA5" and variable in ["snowmelt", "snow_evaporation"]:
            print(f'Skipping {variable} for {dataset} (not available)')
            continue

        print(f'\n{"="*60}')
        print(f'Downloading: {variable}')
        print(f'{"="*60}')

        #dataset = "reanalysis-era5-single-levels-monthly-means" made into looping variable above
        request = {
            "product_type": ["monthly_averaged_reanalysis"],
            "variable": [variable],
            "year": [
                "1981", "1982", "1983", "1984", "1985",
                "1986", "1987", "1988", "1989", "1990", "1991",
                "1992", "1993", "1994", "1995", "1996", "1997",
                "1998", "1999", "2000", "2001", "2002", "2003",
                "2004", "2005", "2006", "2007", "2008", "2009",
                "2010", "2011", "2012", "2013", "2014", "2015",
                "2016", "2017", "2018", "2019", "2020", "2021",
                "2022", "2023", "2024", "2025"
            ],
            "month": [
                "01", "02", "03",
                "04", "05", "06",
                "07", "08", "09",
                "10", "11", "12"
            ],
            "time": ["00:00"],
            "data_format": "netcdf",
            "download_format": "unarchived",
            "area": [45, 65, 20, 105]  # [North, West, South, East]
        }
        target = f"data/{datasetname}/{datasetname}_{variable}_monthly_1981_2025.nc"
        
        try:
            client = cdsapi.Client()
            client.retrieve(dataset, request, target)
            print(f'Successfully downloaded: {variable}')
        except Exception as e:
            print(f'Error downloading {variable}: {e}')
            continue

    print('\n' + '='*60)
    print(f'All {datasetname} downloads complete!') 
    print(f'Files saved in: data/{datasetname}')
    print('='*60)



# download the DEM surface (from static fields):

def download_static_field(dataset, datasetname, variable, target_suffix):
    print(f'\n{"="*60}')
    print(f'Downloading static field: {variable} ({datasetname})')
    print(f'{"="*60}')

    request = {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": [variable],
        "year": ["2025"],
        "month": ["01"],
        "time": ["00:00"],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": [45, 65, 20, 105]  # [North, West, South, East]
    }
    target = f"data/{datasetname}/{datasetname}_{target_suffix}.nc"

    try:
        client = cdsapi.Client()
        client.retrieve(dataset, request, target)
        print(f'Successfully downloaded static field: {variable} ({datasetname})')
    except Exception as e:
        print(f'Error downloading static field {variable} for {datasetname}: {e}')



# Download for ERA5 and ERA5L (same variable, different datasets)
download_static_field(
    "reanalysis-era5-single-levels-monthly-means",
    "ERA5",
    "geopotential",
    "gridcell_surface_elevation_geopotential_monthly_2025_01"
)

download_static_field(
    "reanalysis-era5-land-monthly-means",
    "ERA5L",
    "geopotential",
    "gridcell_surface_elevation_geopotential_monthly_2025_01"
)


# Convert downloaded static geopotential fields to GeoTIFF with GDAL: run these commands in a (bash) terminal with gdal installed
# Geopotential can optionally be converted to elevation in meters with gdal_calc.py

# 'ERA5 to GeoTIFF:'
print(
    'gdal_translate -of GTiff '
    'NETCDF:"data/ERA5/ERA5_gridcell_surface_elevation_geopotential_monthly_2025_01.nc":z '
    'data/ERA5/ERA5_gridcell_surface_elevation_geopotential_monthly_2025_01.tif'
)
#'ERA5-Land to GeoTIFF:'
print(
    'gdal_translate -of GTiff '
    'NETCDF:"data/ERA5L/ERA5L_gridcell_surface_elevation_geopotential_monthly_2025_01.nc":z '
    'data/ERA5L/ERA5L_gridcell_surface_elevation_geopotential_monthly_2025_01.tif'
)

# Note: the data are in geopotential units and need to be converted to elevation in meters by dividing by
# the gravitational acceleration (9.80665 m/s^2) 
# -> I did this manually in qgis, where I also assigned the WGS84 coordinate reference system (EPSG:4326) to the output GeoTIFFs, but it can also be done with gdal_calc.py in a terminal:

# output files: data/ERA5/ERA5_gridcell_surface_elevation_geopotential_m.tif and data/ERA5L/ERA5L_gridcell_surface_elevation_geopotential_m.tif
