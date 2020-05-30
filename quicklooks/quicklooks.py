"""
Radar quicklooks.
Create quicklooks for radar data.

@title: quicklooks.py
@author: Valentin Louf <valentin.louf@monash.edu>
@date: 2020
@copyright: Valentin Louf
@institution: Monash University

.. autosummary::
    :toctree: generated/

    plot_quicklook
"""
import os
import crayons

import pyart
import cftime
import matplotlib.pyplot as pl
import matplotlib.colors as colors


def _adjust_csu_scheme_colorbar_for_pyart(cb):
    cb.set_ticks(np.arange(.55, 11, .9))
    cb.ax.set_yticklabels(['None','Drizzle','Rain',
                           'Ice Crystals','Aggregates','Wet/Melting Snow','Vertically Aligned Ice',
                           'Low-Density Graupel','High-Density Graupel',
                           'Hail',
                           'Big Drops'])
    cb.ax.set_ylabel('')
    cb.ax.tick_params(length=0)
    return cb


def plot_quicklook(input_file, figure_path):
    """
    Plot radar PPIs quicklooks.

    Parameters:
    ===========
    radar:
        Py-ART radar structure.
    gatefilter:
        The Gate filter.
    """
    try:
        radar = pyart.io.read(input_file)
    except Exception:
        raise

    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_invalid('corrected_reflectivity')
    radar_date = cftime.num2pydate(radar.time['data'][0], radar.time['units'])

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
    gr = pyart.graph.RadarDisplay(radar)
    fig, the_ax = pl.subplots(3, 3, figsize=(15, 12), sharex=True, sharey=True)
    the_ax = the_ax.flatten()
    # Plotting reflectivity

    gr.plot_ppi('corrected_reflectivity', ax=the_ax[0], gatefilter=gatefilter, cmap='pyart_NWSRef')
    the_ax[0].set_title(gr.generate_title('corrected_reflectivity', sweep=0, datetime_format='%Y-%m-%dT%H:%M'))

    #echo classification
    #create colormap
    hca_colors = ['White',
                  'LightBlue',
                  'SteelBlue',
                  'MediumBlue',
                  'Plum',
                  'MediumPurple',
                  'm',
                  'Green',
                  'YellowGreen',
                  'Gold',
                  'Red']
    hca_cmap = colors.ListedColormap(hca_colors)
    gr.plot_ppi('radar_echo_classification', ax=the_ax[1], cmap=hca_cmap, vmin=0, vmax=10)
    the_ax[1].set_title(gr.generate_title('radar_echo_classification', sweep=0, datetime_format='%Y-%m-%dT%H:%M'))
    #adjust colorbar for classification
    gr.cbs[1] = _adjust_csu_scheme_colorbar_for_pyart(gr.cbs[1])

    gr.plot_ppi('radar_estimated_rain_rate', ax=the_ax[2])
    the_ax[2].set_title(gr.generate_title('radar_estimated_rain_rate', sweep=0, datetime_format='%Y-%m-%dT%H:%M'))

    gr.plot_ppi('corrected_differential_reflectivity', ax=the_ax[3], gatefilter=gatefilter)
    the_ax[3].set_title(gr.generate_title('corrected_differential_reflectivity',
                                          sweep=0, datetime_format='%Y-%m-%dT%H:%M'))

    try:
        gr.plot_ppi('corrected_differential_phase', ax=the_ax[4], vmin=-180, vmax=180, cmap='pyart_Wild25', gatefilter=gatefilter)
        the_ax[4].set_title(gr.generate_title('corrected_differential_phase', sweep=0,
                                              datetime_format='%Y-%m-%dT%H:%M'))
    except KeyError:
        print(crayons.red("Problem with 'corrected_differential_phase' field."))
        pass

    try:
        gr.plot_ppi('corrected_specific_differential_phase', ax=the_ax[5], vmin=-2, vmax=5,
                    cmap='pyart_Theodore16', gatefilter=gatefilter)
        the_ax[5].set_title(gr.generate_title('corrected_specific_differential_phase', sweep=0,
                                              datetime_format='%Y-%m-%dT%H:%M'))
    except KeyError:
        print(crayons.red("Problem with 'corrected_specific_differential_phase' field."))
        pass

    try:
        gr.plot_ppi('raw_velocity', ax=the_ax[6], cmap='pyart_NWSVel', vmin=-30, vmax=30)
        the_ax[6].set_title(gr.generate_title('velocity', sweep=0, datetime_format='%Y-%m-%dT%H:%M'))
    except KeyError:
        print(crayons.red("Problem with 'raw_velocity' field."))
        pass

    try:
        gr.plot_ppi('velocity', ax=the_ax[7], gatefilter=gatefilter,
                    cmap='pyart_NWSVel', vmin=-30, vmax=30)
        the_ax[7].set_title(gr.generate_title('velocity', sweep=0,
                                              datetime_format='%Y-%m-%dT%H:%M'))
    except KeyError as error:
        print(error)
        print(crayons.red("Problem with 'velocity' field."))
        pass

    try:
        gr.plot_ppi('cross_correlation_ratio', ax=the_ax[8], vmin=0.5, vmax=1.05)
        the_ax[8].set_title(gr.generate_title('cross_correlation_ratio',
                                              sweep=0, datetime_format='%Y-%m-%dT%H:%M'))
    except KeyError:
        print(crayons.red("Problem with 'cross_correlation_ratio' field."))
        pass

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

    print(crayons.green(f"{os.path.basename(outfile)} plotted."))

    return None
