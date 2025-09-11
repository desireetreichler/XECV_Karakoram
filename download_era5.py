# import cdsapi

# def download_era5_land_data(output_file, lat_range, lon_range, variables, years):
#     # Initialize the CDS API client
#     c = cdsapi.Client()

#     # Create the request
#     request = {
#         'product_type': 'reanalysis',
#         'format': 'netcdf',
#         'variables': variables,
#         'area': [lat_range[1], lon_range[0], lat_range[0], lon_range[1]],  # [N, W, S, E]
#         'date': years,
#         'grid': [0.1, 0.1],  # specify grid resolution if needed
#     }

#     # Output the data to a file
#     c.retrieve('reanalysis-era5-land', request, output_file)
#     print(f'Data downloaded to {output_file}')


# if __name__ == "__main__":
#     # Define your parameters
#     output_file = 'era5_land_data.nc'  # Output file name
#     lat_range = [35.0, 37.0]  # [south, north]
#     lon_range = [85.0, 87.0]  # [west, east]
#     variables = [
#         "snow_depth_water_equivalent",
#         "snowfall",
#         "total_precipitation"]  # Example variables
#     date_range = '2020-01-01/to/2020-01-31'  # Date range in YYYY-MM-DD format

#     # Call the download function
#     download_era5_land_data(output_file, lat_range, lon_range, variables, date_range)



    

import cdsapi

dataset = "reanalysis-era5-land-monthly-means"
request = {
    "product_type": ["monthly_averaged_reanalysis"],
    "variable": [
        "snow_depth_water_equivalent",
        "snowfall",
        "total_precipitation"
    ],
    "year": [
        "1950", "1951", "1952", "1953", "1954", "1955",
        "1956", "1957", "1958", "1959", "1960", "1961",
        "1962", "1963", "1964", "1965", "1966", "1967",
        "1968", "1969", "1970", "1971", "1972", "1973",
        "1974", "1975", "1976", "1977", "1978", "1979",
        "1980", "1981", "1982", "1983", "1984", "1985",
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
    "area": [39, 70, 24, 90]
}
target = "era5test.nc"
client = cdsapi.Client()
client.retrieve(dataset, request, target)
#client.retrieve(dataset, request).download()


"""


        """

# client = cdsapi.Client()

# dataset = 'reanalysis-era5-pressure-levels'
# request = {
#   'product_type': ['reanalysis'],
#   'variable': ['geopotential'],
#   'year': ['2024'],
#   'month': ['03'],
#   'day': ['01'],
#   'time': ['13:00'],
#   'pressure_level': ['1000'],
#   'data_format': 'grib',
# }
# target = 'download.grib'

# client.retrieve(dataset, request, target)
