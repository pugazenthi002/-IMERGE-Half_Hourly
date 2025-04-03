import os
import h5py
import numpy as np
from netCDF4 import Dataset, date2num
from datetime import datetime, timedelta
current_datetime = datetime.now().strftime("%Y-%m-%d")
data_root = "../IMERGE/"

# Function to process a single month
def process_month(year, month):
    monthly_files = []  # Store all HDF5 file paths for the month
    lat_data, lon_data = None, None  # Latitude and Longitude
    
    # Scan daily subfolders under the year/month
    month_path = os.path.join(data_root, str(year), str(month).zfill(2))
    print(month_path)
    if not os.path.exists(month_path):
        print(f"Skipping missing folder: {month_path}")
        return

    for day in sorted(os.listdir(month_path)):  # Sort days numerically
        day_path = os.path.join(month_path, day)
        if os.path.isdir(day_path):
            for file in sorted(os.listdir(day_path)):  # Sort files within a day
                if file.endswith(".HDF5"):
                    monthly_files.append(os.path.join(day_path, file))

    if not monthly_files:
        print(f"No files found for {year}-{month:02d}")
        return

    time_data_list, precip_data_list = [], []

    # Process each file
    for h5_file in monthly_files:
        with h5py.File(h5_file, "r") as f:
            # Read Latitude and Longitude once (assume it's the same for all files)
            if lat_data is None or lon_data is None:
                lat_data = f['/Grid/lat'][:]
                lon_data = f['/Grid/lon'][:]
            
            # Read time data
            time_values = f['/Grid/time'][:]  # Assuming 'time' dataset exists    
            time_data_list.extend(time_values)
            precip_data_list.append(f['/Grid/precipitation'][:])  # Assuming 'precipitation' dataset

    # Stack precipitation data along the time dimension
    time_data = time_data_list
    precip_data = np.concatenate(precip_data_list, axis=0)  # (time, lat, lon)

    # Create NetCDF file
    output_nc = f"{year}_{month:02d}.nc"
    ncfile = Dataset(output_nc, "w", format="NETCDF4")

    # Create dimensions
    ncfile.createDimension('time', None)  # Unlimited
    ncfile.createDimension('lat', len(lat_data))
    ncfile.createDimension('lon', len(lon_data))

    # Create variables
    time_var = ncfile.createVariable('time', np.int32, ('time',))
    lat_var = ncfile.createVariable('lat', np.float32, ('lat',))
    lon_var = ncfile.createVariable('lon', np.float32, ('lon',))
    precip_var = ncfile.createVariable('precipitation', np.float32, ('time', 'lat', 'lon'), zlib=True, complevel=4)

    # Assign data
    lat_var[:] = lat_data
    lon_var[:] = lon_data
    time_var[:] = time_data  # Convert time to integers
    precip_var[:] = precip_data

    # Set attributes
    lat_var.units = 'degrees_north'
    lon_var.units = 'degrees_east'
    time_var.units = "seconds since 1980-01-06 00:00:00 UTC"
    time_var.standard_name = "time"
    time_var.calendar = "standard"
    time_var.axis = "T"

    precip_var.units = 'mm/half_hour'
    ncfile.title = f"IMERG half hourly Precipitation for {year}-{month:02d} as monthly single file"
    ncfile.source = "Merged from HDF5 files"
    ncfile.history = f"Created on {current_datetime} by pugazzh"

    # Close file
    ncfile.close()
    print(f"Created NetCDF: {output_nc}")

# **Run the script for all years and months**
for year in range(2001, 2010):  # Modify based on your dataset range
    for month in range(1, 13):
        process_month(year, month)


