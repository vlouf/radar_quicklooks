"""
Turning radar PPIs into Cartesian grids.

@title: radar_grids
@author: Valentin Louf <valentin.louf@bom.gov.au>
@institution: Monash University and Bureau of Meteorology
@date: 05/08/2020
@version: 1

.. autosummary::
    :toctree: generated/

    chunks
    main
"""
import gc
import os
import sys
import glob
import time
import argparse
import datetime
import warnings
import traceback

import crayons
import dask
import dask.bag as db
import matplotlib


def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    From http://stackoverflow.com/a/312464
    """
    for i in range(0, len(l), n):
        yield l[i : i + n]


def main(infile, outpath):
    """
    It calls the production line and manages it. Buffer function that is used
    to catch any problem with the processing line without screwing the whole
    multiprocessing stuff.

    Parameters:
    ===========
    infile: str
        Name of the input radar file.
    outpath: str
        Path for saving output data.
    """
    import quicklooks
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            quicklooks.plot_quicklook(infile, outpath)
        except Exception:
            traceback.print_exc()
            return None

    gc.collect()
    return None


if __name__ == "__main__":
    """
    Global variables definition.
    """
    matplotlib.use("Agg")
    # Parse arguments
    parser_description = "Processing of radar data from level 1a to level 1b."
    parser = argparse.ArgumentParser(description=parser_description)
    parser.add_argument(
        "-s", "--start-date", dest="start_date", default=None, type=str, help="Starting date.", required=True,
    )
    parser.add_argument(
        "-e", "--end-date", dest="end_date", default=None, type=str, help="Ending date.", required=True,
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        dest="indir",
        default="/g/data/hj10/cpol_level_1b/v2020/ppi",
        type=str,
        help="Input directory.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="outdir",
        default="/g/data/hj10/cpol_level_1b/v2020/quicklooks",
        type=str,
        help="Output directory.",
    )

    args = parser.parse_args()
    START_DATE = args.start_date
    END_DATE = args.end_date
    INPATH = args.indir
    OUTPATH = args.outdir
    try:
        start = datetime.datetime.strptime(START_DATE, "%Y%m%d")
        end = datetime.datetime.strptime(END_DATE, "%Y%m%d")
        if start > end:
            raise ValueError("End date older than start date.")
        date_range = [start + datetime.timedelta(days=x) for x in range(0, (end - start).days + 1,)]
    except ValueError:
        print("Invalid dates.")
        sys.exit()

    print("The start date is: " + start.strftime("%Y-%m-%d"))
    print("The end date is: " + end.strftime("%Y-%m-%d"))
    print(f"The input directory is {INPATH}\nThe output directory is {OUTPATH}.")

    sttime = time.time()
    for day in date_range:
        input_dir = os.path.join(INPATH, str(day.year), day.strftime("%Y%m%d"), "*.*")
        flist = sorted(glob.glob(input_dir))
        if len(flist) == 0:
            print("No file found for {}.".format(day.strftime("%Y-%b-%d")))
            continue
        print(f"{len(flist)} files found for " + day.strftime("%Y-%b-%d"))
        arglist = [(f, OUTPATH) for f in flist]
        bag = db.from_sequence(arglist).starmap(main)
        bag.compute()

    print(crayons.green(f"Process completed in {time.time() - sttime:0.2f}."))
