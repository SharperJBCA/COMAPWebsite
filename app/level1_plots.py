import matplotlib.pyplot as plt
from astropy.time import Time
from datetime import datetime
import numpy as np 
import os
from .create_all import Level1File
import matplotlib.dates as mdates
from datetime import timedelta
import pandas as pd


def generate_plots(plot_type='mean_Tvane',start_mjd=None, end_mjd=None):
    # Example data retrieval (replace with actual data retrieval logic)
    # e.g., data = Level1File.query.filter(Level1File.date.between(start_date, end_date)).all()

    records = Level1File.query.filter(Level1File.mjd >= start_mjd, Level1File.mjd <= end_mjd).all()
    mjds = [record.mjd for record in records]
    # Convert MJD to YYYY-MM-DD
    dates = [Time(m, format='mjd').datetime for m in mjds]
    delta_days = np.max(mjds) - np.min(mjds)
    # Calculate the difference in days
    data_dict = {'mjd': mjds,'dates':dates, 'source_name': [record.source_name for record in records]}

    for column in Level1File.__table__.columns:
        if not any([column.name == 'mjd', column.name == 'obs_id', column.name == 'file_path', column.name == 'year', column.name == 'month', column.name == 'source_name']):
            data_dict[column.name] = [getattr(record, column.name) for record in records]

    # Converting dictionary to pandas DataFrame
    df = pd.DataFrame(data_dict)
    df['source_name'] = df['source_name'].str.replace(r'^(GField\d+[a-z]?|Field\d+[a-z]?)$', 'Field')
    df = df.replace([np.inf, -np.inf], np.nan)

    for column in [c for c in Level1File.__table__.columns if c.name == plot_type]:
        # We don't want to plot mjd vs mjd
        if not any([column.name == 'mjd', column.name == 'obs_id', column.name == 'file_path', column.name == 'year', column.name == 'month', column.name == 'source_name']):
            values = [getattr(record, column.name) for record in records]

            # Create first plot
            fig, ax = plt.subplots()
            if delta_days <= 30:  # A month of data
                ax.xaxis.set_major_locator(mdates.DayLocator())  # Tick for every day
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            elif delta_days <= 90:  # Up to 3 months
                ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[1, 15]))  # Tick on 1st and 15th of each month
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            else:  # A year or more
                ax.xaxis.set_major_locator(mdates.MonthLocator())  # Tick for every month
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

            # Grouping by 'source_name' and plotting each group
            for name, group in df.groupby('source_name'):
                ax.plot(group['dates'], group[column.name], '.', label=name)

            #ax.plot(dates, values,'.')
            plt.xlabel('Date')
            plt.ylabel(column.name)
            plt.xticks(rotation=30)
            plt.grid()
            plt.legend(loc='best')  # Adding a legend
            plt.savefig(f'app/static/figures/level1_plots/timeseries_{column.name}.png')
            plt.close()

            # Create second plot
            plt.figure()
            try:
                data = df[column.name].dropna()
                plt.hist(data)
            except (TypeError, ValueError) as e:
                print(f'Unable to plot histogram for {column.name} with error {e}')
            plt.xlabel(column.name)
            plt.grid()
            plt.savefig(f'app/static/figures/level1_plots/hist_{column.name}.png')
            plt.close()




def run(start_mjd=None, end_mjd=None):
    generate_plots(start_mjd=start_mjd, end_mjd=end_mjd)
