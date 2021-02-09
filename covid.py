import numpy as np
import matplotlib.pyplot as plt
import urllib.request
import pandas as pd

# get the data from the Hopkins GitHub
url = r'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv'
# url = r'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'

def backward_moving_average(x, y, lag=7):
    cum_sum = y.cumsum()
    y_smooth = (cum_sum[lag:] - cum_sum[:-lag])/lag
    return (x[lag-1:], np.r_[cum_sum[lag-1]/lag, y_smooth])


print('Downloading data...')
fname = './covid_data.csv'
urllib.request.urlretrieve(url, fname)
df = pd.read_csv(fname)

fig, axs = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(8, 8), tight_layout=True)


def plot_data(ax, location='Colorado', start_col_idx=11, smoothings=[3, 7]):
    print('Plotting %s...'%location)
    if location == 'Boulder County':
        idx = np.where(df['Admin2']=='Boulder')[0][0]
        y = df.iloc[idx].values[start_col_idx:]
    elif location == 'Colorado':
        idx = np.where(df['Province_State']=='Colorado')[0]
        y = np.zeros_like(df.iloc[idx[0]].values[start_col_idx:])
        for county_idx in idx:
            y = y + df.iloc[county_idx].values[start_col_idx:]
    elif location == 'USA':
        idx = np.where(df['Country_Region']=='US')[0]
        y = np.zeros_like(df.iloc[idx[0]].values[start_col_idx:])
        for county_idx in idx:
            y = y + df.iloc[county_idx].values[start_col_idx:]
    else:
        raise ValueError('Location name not recognized.')

    x = np.arange(y.size-1)

    y = y.astype(np.float)
    ax.fill_between(x-x[-1],np.diff(y), y2=0, step="pre", alpha=0.4, color='C0', label='Cases per day', linewidth=0)

    for n, smoothing in enumerate(smoothings):
        x_sm, y_sm = backward_moving_average(np.arange(y.size-1), np.diff(y), lag=smoothing)
        ax.plot(x_sm - x_sm[-1], y_sm, color='C%i'%(n+1), label='Smoothed (%i day)'%smoothing)

    ax.set_title(location + ' cases')


plot_data(axs[0], 'USA')
plot_data(axs[1], 'Colorado')
plot_data(axs[2], 'Boulder County')

axs[-1].set_xlabel('days relative to '+df.columns[-1])

for ax in axs:
    ax.set_xlim(-300, 1)
    ax.set_ylabel('Cases')
    ax.legend(loc='upper left')
    ax.grid(alpha=0.15)

fig.savefig('Covid cases.png', dpi=250)
plt.show()
