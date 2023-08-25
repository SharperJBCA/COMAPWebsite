import h5py
import os 
import numpy as np
import argparse
from tqdm import tqdm
from .create_all import Level1File
from . import app, db

import sqlite3

def add_column_if_not_exists(db_path, table_name, column_name, column_type):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Fetch the info for the table
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [info[1] for info in cursor.fetchall()]

        # Check if the column exists
        if column_name not in columns:
            # Add the column
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
            print(f"Column {column_name} added to {table_name}.")
        else:
            print(f"Column {column_name} already exists in {table_name}.")

def populate_level1_database(directory_path):
    VANE_HOT_TEMP_OFFSET = 273.15 # K

    # Get a list of all HDF5 files in the directory
    hdf5_files = [f for f in os.listdir(directory_path) if f.endswith('.hd5')]
    hdf5_obsids = [int(os.path.basename(f).split('-')[1]) for f in hdf5_files]

    # filter the files:
    hdf5_files = [f for f,obs_id in zip(hdf5_files,hdf5_obsids) if not Level1File.query.filter_by(obs_id=obs_id).first()]
    hdf5_obsids = [obs_id for obs_id in hdf5_obsids if not Level1File.query.filter_by(obs_id=obs_id).first()]

    for hdf5_file,obs_id in zip(tqdm(hdf5_files,desc='Populating SQL table'),hdf5_obsids):
        file_path = os.path.join(directory_path, hdf5_file)

        # Read the HDF5 file
        with h5py.File(file_path, 'r') as h:
            source_name = h['comap'].attrs['source'].split(',')[0]  # Adjust accordingly
            year = hdf5_file.split('-')[2]
            month = hdf5_file.split('-')[3]
            mean_Tvane = float(h['hk/antenna0/vane/Tvane'][:].mean())/100. + VANE_HOT_TEMP_OFFSET 
            mean_Tshroud = float(h['hk/antenna0/vane/Tshroud'][:].mean())/100.  + VANE_HOT_TEMP_OFFSET
            mean_wind_speed = float(h['hk/array/weather/windSpeed'][:].mean()) # m/s
            mean_air_temp = float(h['hk/array/weather/airTemperature'][:].mean()) # degC 
            mean_air_pressure = float(h['hk/array/weather/pressure'][:].mean()) # mbar
            mean_relative_humidity = float(h['hk/array/weather/relativeHumidity'][:].mean()) # %
            mean_wind_direction = float(h['hk/array/weather/windDirection'][:].mean()) # deg azimuth
            mean_az = float(h['spectrometer/pixel_pointing/pixel_az'][0,:].mean()) # deg
            mean_el = float(h['spectrometer/pixel_pointing/pixel_el'][0,:].mean()) # deg
            mjd = float(h['spectrometer/MJD'][0]) # MJD

        # Check if this obs_id is already in the database
        existing_entry = Level1File.query.filter_by(obs_id=obs_id).first()
        if not existing_entry:
            # Create a new entry and add it to the database
            new_entry = Level1File(
                obs_id=obs_id,
                source_name=source_name,
                year=year,
                month=month,
                file_path=file_path,
                mean_Tvane=mean_Tvane,
                mean_Tshroud=mean_Tshroud,
                mean_wind_speed=mean_wind_speed,
                mean_air_temp=mean_air_temp,
                mean_air_pressure=mean_air_pressure,
                mean_relative_humidity=mean_relative_humidity,
                mean_wind_direction=mean_wind_direction,
                mean_az=mean_az,
                mean_el=mean_el,
                mjd=mjd
            )
            db.session.add(new_entry)
            db.session.commit()

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory_path',type=str, help='Path to directory containing HDF5 files', default='./data')
    parser.add_argument('--database_name',type=str, help='Name of the database to create', default='comap_manchester_database.db')
    return parser.parse_args()

def run():

    args = options()

    with app.app_context():
        populate_level1_database(args.directory_path)
    

if __name__ == "__main__":
    run()