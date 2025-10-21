import pandas as pd
import numpy as np
import requests
import fastf1
import os

# STEP ONE: SET UP 
# Save Data to folder to prevent constant redownloading
cache_dir = "fastf1_cache"
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache('fastf1_cache')


# STEP TWO: DATA COLLECTION
# Download the data for Monza 2024 Race 
session = fastf1.get_session(2024, 'Monza', 'R')  
session.load()  # downloads the data

# Organize data by laps, pits, positions, and driver info 
laps_df = session.laps
laps_df.to_csv('lap_times.csv')

# Pit stops
pit_stops_df = laps_df[laps_df['PitOutTime'].notnull()]
pit_stops_df.to_csv('pit_stops.csv')

# Positions per lap
positions_df = laps_df[['Driver', 'LapNumber', 'Position']]
positions_df.to_csv('positions.csv')

# Driver info
drivers_df = session.results[['FullName', 'TeamName', 'DriverNumber', 'Abbreviation', 'Position']]
drivers_df.to_csv('drivers.csv')


# STEP THREE: DATA CLEANING AND MERGING
# Replace abbreviations with driver name 
laps_df = laps_df.merge(
    drivers_df[['Abbreviation', 'FullName', 'TeamName']],
    left_on="Driver",
    right_on="Abbreviation",
    how="left"
)
laps_df['Driver'] = laps_df['FullName']
laps_df = laps_df.drop(columns=['FullName'])

# Add pit stop flags
laps_df['PitStopFlag'] = laps_df['PitInTime'].notna() | laps_df['PitOutTime'].notna()

# Remove columns that aren't needed for our purposes and drop duplicates
f1_data = laps_df[['LapTime', 'Position', 'Driver', 'DriverNumber', 'TeamName', 'LapNumber', 'Compound', 'Stint', 'PitInTime', 'PitOutTime', 'PitStopFlag']]
f1_data.drop_duplicates()

# Check for missing values 
# print(f1_data.isnull().sum())

# STEP FOUR: EXPLORATORY ANALYSIS 
# Check Lap Progression and Stint (# of laps on one set of tires)
lap_diff = f1_data.groupby('Driver')['LapNumber'].diff()
issue = f1_data[(lap_diff.notna()) & (lap_diff != 1)]

stint_diff = f1_data.groupby('Driver')['Stint'].diff()
issue = f1_data[(stint_diff.notna()) & (stint_diff != 0) & (stint_diff != 1)]

# Fastest Lap 
fastest_lap = f1_data[f1_data['LapTime'] == f1_data['LapTime'].min()]

# Average Lap Time per Stint
average_lap_per_stint = f1_data.groupby(['Driver', 'Stint'])['LapTime'].mean()

# Driver Consistency
f1_data['LapSeconds'] = f1_data['LapTime'].dt.total_seconds()
driver_consistency = f1_data.groupby(['Driver', 'Stint'])['LapSeconds'].var()

# Export Data for Tableau Visualization
f1_data.to_csv("f1_clean.csv", index=False)
fastest_lap.to_csv("f1_fastest_lap.csv", index=False)
average_lap_per_stint.to_csv("f1_avg_stint.csv", index=False)
driver_consistency.to_csv("f1_consistency.csv", index=False)