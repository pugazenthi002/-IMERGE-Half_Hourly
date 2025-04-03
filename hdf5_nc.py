import h5py
import numpy as np
from netCDF4 import Dataset, date2num
from datetime import datetime, timedelta
import glob
import os
'''
result of #h5dump -d filename# 
FILE_CONTENTS {
 group      /
 group      /Grid
 group      /Grid/Intermediate
 dataset    /Grid/Intermediate/IRinfluence
 dataset    /Grid/Intermediate/IRprecipitation
 dataset    /Grid/Intermediate/MWobservationTime
 dataset    /Grid/Intermediate/MWprecipSource
 dataset    /Grid/Intermediate/MWprecipitation
 dataset    /Grid/Intermediate/precipitationUncal
 dataset    /Grid/lat
 dataset    /Grid/lat_bnds
 dataset    /Grid/latv
 dataset    /Grid/lon
 dataset    /Grid/lon_bnds
 dataset    /Grid/lonv
 dataset    /Grid/nv
 dataset    /Grid/precipitation
 dataset    /Grid/precipitationQualityIndex
 dataset    /Grid/probabilityLiquidPrecipitation
 dataset    /Grid/randomError
 dataset    /Grid/time
 dataset    /Grid/time_bnds
 }
}
'''
input_folder = "../IMERGE/2001/01/01"
output_folder = "."
   
current_datetime = datetime.now().strftime("%Y-%m-%d")

def covert_hdf52nc(hdf5_file,netcdf_file_path):
    
    with h5py.File(hdf5_file, 'r') as h5f:
        precip_data = h5f['/Grid/precipitation'][:]
        precip_attrs = h5f['/Grid/precipitation'].attrs
        lat_data = h5f['/Grid/lat'][:]
        lon_data = h5f['/Grid/lon'][:]
        time_data = h5f['/Grid/time'][:]
        #print(time_data)
        base_time = datetime(1980, 1, 6)  # IMERG epoch
        time_dates = (base_time + timedelta(seconds=int(time_data)))
        time_numeric = date2num(time_dates, units="seconds since 1980-01-06 00:00:00 UTC", calendar="standard")
    
    #netcdf_file_path = 'precipitation_data.nc'
    with Dataset(netcdf_file_path, 'w', format='NETCDF4') as ncfile:
        # Create dimensions for lat, lon, and time if applicable
        lat_dim = ncfile.createDimension('lat', len(lat_data))
        lon_dim = ncfile.createDimension('lon', len(lon_data))
        time_dim = ncfile.createDimension('time', None)  # Unlimited dimension
    
        # Create variables for lat, lon, and precipitation
        lat_var = ncfile.createVariable('lat', np.float32, ('lat',))
        lon_var = ncfile.createVariable('lon', np.float32, ('lon',))
        time_var = ncfile.createVariable('time', np.int32, ('time',))
        precip_var = ncfile.createVariable('precipitation', np.float32, ('time', 'lat', 'lon'), zlib=True, complevel=4)
        time_var.calendar = "standard"
        
        time_var[:] = time_numeric
        lat_var[:] = lat_data
        lon_var[:] = lon_data
        precip_var[:] = precip_data
    
        # Set attributes for each variable (if needed)
        lat_var.units = 'degrees_north'
        lon_var.units = 'degrees_east'
        time_var.units = "seconds since 1980-01-06 00:00:00 UTC"
        precip_var.units = 'mm/half_hour' 
    
        # Add global attributes if necessary
        ncfile.title = "Precipitation Data only from IMERGE half hourly Dataset"
        ncfile.source = "Generated from HDF5 file"
        ncfile.history = f"Created on {current_datetime} by pugazh"

for hdf5_file_path in glob.glob(os.path.join(input_folder, "*.HDF5")):
    ss=(os.path.basename(hdf5_file_path)).split(".")
    #print(ss)
    netcdf_file_path=ss[5]+".nc"
    covert_hdf52nc(hdf5_file_path,netcdf_file_path)

    