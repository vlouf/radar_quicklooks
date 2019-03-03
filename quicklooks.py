"""
Radar quicklooks.
Create quicklooks for radar data.

@title: quicklooks.py
@author: Valentin Louf <valentin.louf@monash.edu>
@date: 2019
@copyright: Valentin Louf 
@institution: Monash University

.. autosummary::
    :toctree: generated/

    plot_quicklook
"""
import os
import glob
import matplotlib
matplotlib.use('Agg')

import pyart
import matplotlib.pyplot as pl
import dask.bag as db


def plot_quicklook(radar, gatefilter, radar_date, figure_path):
    """
    Plot figure of old/new radar parameters for checking purpose.

    Parameters:
    ===========
        radar:
            Py-ART radar structure.
        gatefilter:
            The Gate filter.
        radar_date: datetime
            Datetime stucture of the radar data.
    """
    if figure_path is None:
        return None
    # Extracting year and date.
    year = str(radar_date.year)
    datestr = radar_date.strftime("%Y%m%d")
    # Path for saving Figures.
    outfile_path = os.path.join(figure_path, year, datestr)

    # Checking if output directory exists. Creating them otherwise.
    if not os.path.isdir(os.path.join(figure_path, year)):
        try:
            os.mkdir(os.path.join(figure_path, year))
        except FileExistsError:
            pass
    if not os.path.isdir(outfile_path):
        try:
            os.mkdir(outfile_path)
        except FileExistsError:
            pass

    # Checking if figure already exists.
    outfile = radar_date.strftime("%Y%m%d_%H%M") + ".png"
    outfile = os.path.join(outfile_path, outfile)

    # Initializing figure.
    with pl.style.context('seaborn-paper'):
        gr = pyart.graph.RadarDisplay(radar)
        fig, the_ax = pl.subplots(4, 3, figsize=(14, 15), sharex=True, sharey=True)
        the_ax = the_ax.flatten()
        # Plotting reflectivity
        gr.plot_ppi('total_power', ax=the_ax[0], cmap='pyart_NWSRef')
        the_ax[0].set_title(gr.generate_title('total_power', sweep=0, datetime_format='%Y-%m-%dT%H:%M'))

        gr.plot_ppi('reflectivity', ax=the_ax[1], gatefilter=gatefilter, cmap='pyart_NWSRef')
        the_ax[1].set_title(gr.generate_title('reflectivity', sweep=0, datetime_format='%Y-%m-%dT%H:%M'))

        gr.plot_ppi('radar_estimated_rain_rate', ax=the_ax[2])
        the_ax[2].set_title(gr.generate_title('radar_estimated_rain_rate', sweep=0, datetime_format='%Y-%m-%dT%H:%M'))

        gr.plot_ppi('differential_phase', ax=the_ax[3], vmin=-180, vmax=180, cmap='pyart_Wild25')
        the_ax[3].set_title(gr.generate_title('differential_phase', sweep=0, datetime_format='%Y-%m-%dT%H:%M'))

        try:
            gr.plot_ppi('corrected_differential_phase', ax=the_ax[4], vmin=-180, vmax=180, cmap='pyart_Wild25', gatefilter=gatefilter)
            the_ax[4].set_title(gr.generate_title('corrected_differential_phase', sweep=0,
                                                  datetime_format='%Y-%m-%dT%H:%M'))
        except KeyError:
            pass

        try:
            gr.plot_ppi('corrected_specific_differential_phase', ax=the_ax[5], vmin=-2, vmax=5, cmap='pyart_Theodore16', gatefilter=gatefilter)
            the_ax[5].set_title(gr.generate_title('corrected_specific_differential_phase', sweep=0,
                                                  datetime_format='%Y-%m-%dT%H:%M'))
        except KeyError:
            pass

        try:
            gr.plot_ppi('raw_velocity', ax=the_ax[6], cmap='pyart_NWSVel', vmin=-30, vmax=30)
            the_ax[6].set_title(gr.generate_title('velocity', sweep=0, datetime_format='%Y-%m-%dT%H:%M'))
        except KeyError:
            pass

        try:
            gr.plot_ppi('velocity', ax=the_ax[7], gatefilter=gatefilter,
                        cmap='pyart_NWSVel', vmin=-30, vmax=30)
            the_ax[7].set_title(gr.generate_title('region_dealias_velocity', sweep=0,
                                                  datetime_format='%Y-%m-%dT%H:%M'))
        except KeyError:
            pass

        try:
            gr.plot_ppi('cross_correlation_ratio', ax=the_ax[8], vmin=0.5, vmax=1.05)
            the_ax[8].set_title(gr.generate_title('cross_correlation_ratio',
                                                  sweep=0, datetime_format='%Y-%m-%dT%H:%M'))
        except KeyError:
            pass

        gr.plot_ppi('differential_reflectivity', ax=the_ax[9])
        the_ax[9].set_title(gr.generate_title('differential_reflectivity', sweep=0, datetime_format='%Y-%m-%dT%H:%M'))

        gr.plot_ppi('corrected_differential_reflectivity', ax=the_ax[10], gatefilter=gatefilter)
        the_ax[10].set_title(gr.generate_title('corrected_differential_reflectivity',
                                              sweep=0, datetime_format='%Y-%m-%dT%H:%M'))

        gr.plot_ppi('radar_echo_classification', ax=the_ax[11])
        the_ax[11].set_title(gr.generate_title('radar_echo_classification', sweep=0, datetime_format='%Y-%m-%dT%H:%M'))

        for ax_sl in the_ax:
            gr.plot_range_rings([50, 100, 150], ax=ax_sl)
            ax_sl.set_aspect(1)
            ax_sl.set_xlim(-150, 150)
            ax_sl.set_ylim(-150, 150)

        pl.tight_layout()
        pl.savefig(outfile)  # Saving figure.
        fig.clf()  # Clear figure
        pl.close()  # Release memory
    del gr  # Releasing memory

    return None


def main():
    # TODO:
    # - List files (argparse input directory?).
    # - Generate output directory (argparse output root directory?).
    # - Use dask to multiproc figure creation.

    return None


if __name__ == '__main__':
    main()