# idf
Rainfall intensity duration frequency (IDF) curve calculation and plotting

# Repository Details

* STATUS: Active
* LATEST RELEASE: v.0.4.2
* LAST UPDATED: 2019-11-27
* LICENSE: Public Domain (except where otherwise noted)
* URL: https://github.com/dt-woods/idf

# Summary

The intensity-duration-frequency (IDF) curve for a given region is often used as a design criteria for hydrologic structures: from rain barrels to dams.
Computing an IDF curve allows the designer to quickly calculate expected rainfall quantities at different return periods; answering questions such as "What storm characteristics should I expect in the next five or ten years and how much water will it bring?"
In order to more accurately predict future storm characteristics and their return periods, long-term rainfall observations are critical (>10 years).
Because different regions will likely have different rainfall characteristics that change over time, a method for quickly computing the IDF curve is advantageous.

This script reads rainfall data, identifies individual rainfall events, calculates each event's duration and intensity, computes the return period probabilities for all storm events, and plots the IDF curve.

Results will be highly dependent on the quality, resolution, and length of the rain data set.
Some assumptions have been made and can be edited within the code.
Notably is the minimum inter-event time (MIT), which is set to five (5) hours; this may not be suitable for all regions: consult the literature for advice.
This script also assumes that storm starting and ending times are immediately before and after they are recorded, which may not be accurate for data sets with long time intervals (e.g., hourly data).
The durations and the return periods have been hard-coded; if they are not what you need for your analysis, they are clearly identified in the code for IDF Analysis and Computing the IDF Curve; make adjustments as needed.

Please note that this code is not intended for use with designs that are life-saving or life-threatening.

Although all reasonable efforts have been taken to ensure the accuracy and reliability of this code, the author does not and cannot warrant the performance or results that may be obtained by its use.
The author disclaims all warranties, express or implied, including warranties of performance, merchantability or fitness for any particular purpose.

For comments or concerns, please use GitHub's Issues.

# Contents

idf.py

- Python script for reading precipitation data, identifying rainfall events, and computing/plotting the IDF curve

```
usage: idf.py [-h] [--usgs] [--make_regular] [--save_plot] [--verbose] file

IDF.py - Calculate IDF curves from rainfall data.

positional arguments:
  file            input rainfall file; format should be two-column (datetime
                  and rainfall amount) comma-separated plain text

optional arguments:
  -h, --help      show this help message and exit
  --usgs          input file format is based on USGS raingage station; the
                  script will format the file for you
  --make_regular  make regular irregular time stamped rainfall.
  --save_plot     save IDF curve to PNG file
  --verbose       print out all rainfall events
```

**EXAMPLE 1 - USGS RAINGAGE DATA**

Converts tab-separated file to csv and saves the IDF curve as a PNG image file.

```
python idf.py --usgs --save_plot nwis.waterdata.usgs.gov
```

**EXAMPLE 2 - TWO-COLUMN PLAIN TEXT FORMAT**

Plots the IDF curve.

```
python idf.py rainfall.txt
```

# Data
This script reads one of two types of rainfall data: USGS raingage tab-separated plain text file or a two-column comma-separated plain text file.

USGS Raingage Data
------------------
EXAMPLE DATA

* URL: https://waterdata.usgs.gov/nc/nwis/inventory/?site_no=354057080362545
* description: Contains 5-minute resolution rainfall data in CSV format for USGS rain gage at RO-149 PIEDMONT RS 1 NR BARBER, NC
* USGS site: 354057080362545
* Retrieved: 2019-04-10
* Parameter: Precipitation, total, inches
* Date range: 2009-10-01 01:00 EDT to 2019-04-10 09:55 EDT
* Rows of data: 960109

DATA ACCESS

* Browse to URL
* Click Current / Historical Observations
* Check 00045 Precipitation
* Output format: Tab-separated
* Begin date: 2009-10-01
* End date: 2019-04-10
* Click Go
* Right-click on page: Save page as "nwis.waterdata.usgs.gov"

DATA FORMAT

```
# ---------------------------------- WARNING ----------------------------------------
# Some of the data that you have obtained from this U.S. Geological Survey database
# may not have received Director's approval. Any such data values are qualified
# as provisional and are subject to revision. Provisional data are released on the
# condition that neither the USGS nor the United States Government may be held liable
# for any damages resulting from its use.
#
# Additional info: https://help.waterdata.usgs.gov/policies/provisional-data-statement
#
# File-format description:  https://help.waterdata.usgs.gov/faq/about-tab-delimited-output
# Automated-retrieval info: https://help.waterdata.usgs.gov/faq/automated-retrievals
#
# Contact:   gs-w_support_nwisweb@usgs.gov
# retrieved: 2019-11-24 12:55:21 EST       (nadww01)
#
# Data for the following 1 site(s) are contained in this file
#    USGS 354057080362545 RAINGAGE AT RO-149 (NC193) PIEDMONT RS 1 NR BARBER
# -----------------------------------------------------------------------------------
#
# Data provided for site 354057080362545
#            TS   parameter     Description
#         90643       00045     Precipitation, total, inches
#
# Data-value qualification codes included in this output:
#     A  Approved for publication -- Processing and review completed.
#
agency_cd	site_no	datetime	tz_cd	90643_00045	90643_00045_cd
5s	15s	20d	6s	14n	10s
USGS	354057080362545	2010-10-01 00:00	EDT	0.00	A
USGS	354057080362545	2010-10-01 00:05	EDT	0.00	A
USGS	354057080362545	2010-10-01 00:10	EDT	0.00	A
...
```

Use the `--usgs` flag to auto-format this file.

Two-Column Plain Text Format
----------------------------
You may create your own rainfall data file, so long as it meets the formatting guidelines of:

* single column header (e.g., "Datetime,Rainfall")
* ISO formatted timestamps (i.e., "YYYY-MM-DD HH:MM:SS")

EXAMPLE DATA

```
datetime,precip_inches
2019-02-06 13:00,0
2019-02-06 13:05,0
2019-02-06 13:10,0.1
...
```

If your rainfall data comes from a personal weather station or other source that has irregular time stamp intervals, you may use the flag `--make_regular` to calculate a regular time series (if needed).


# Changelog

* 2019-11-27: v0.4.2
    - fixed typo in usgs_to_csv
    - fixed potential problem in make_regular_ts with variable `my_data`
    - added command line arguments for easier workflows with other rainfall files
* 2019-11-25: v0.4.1
    - added check for formatted csv to avoid running conversion twice
    - changed usgs_to_csv to accept two string arguments (input/output file names) and return nothing
    - added boolean argument to make_plot for saving figure to PNG
* 2019-11-24: v.0.4
    - added three new functions: usgs_to_csv, writeout, writeline
    - removed file path variables (assumes rainfall file is in local dir)
    - new workflow: reads tab-separated usgs rain gage file, processes to csv, runs idf
* 2019-03-23: v.0.3.1
* 2019-03-22: v.0.3.0-dev

# Install

This script was tested using Python 3.6.7 and requires the installation of the following third-party packages (version numbers have been successfully tested).

* numpy (1.16.2; 1.17.4)
* scipy (1.2.1; 1.3.3)
* matplotlib (3.0.3)

## Windows

* Download the latest version of Python 3 for Windows (https://www.python.org/downloads/windows/).
* Install locally with pip and defaults (it should result in you having `py` command line tool).
* Test that the installation works.
    - Click the Windows start, search "cmd," and open the Command Prompt app
    - Type `py -V`
* Download necessary wheel files for the following three packages:
    - NumPy (https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy)
    - SciPy (https://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy)
    - Matplotlib (https://www.lfd.uci.edu/~gohlke/pythonlibs/#matplotlib)

    > Note that the wheel file (.whl) you want should match the Python version you downloaded (for example -cp27- for Python 2.7 or -cp37- for Python 3.7) and its bitness (for example win32 for 32-bit installations or amd64 for 64-bit installations).

* Install the wheel files using pip on the command line.
    - Open the Command Prompt
    - Type `cd %USERPROFILE%\Downloads` to move into your Downloads folder
    - Type `py -m pip install "numpy‑1.16.2+mkl‑cp37‑cp37m‑win32.whl"` replacing the file name with whichever version you downloaded
    - Type `py -m pip install scipy‑1.2.1‑cp37‑cp37m‑win32.whl`
    - Type `py -m pip install matplotlib‑3.0.3‑cp37‑cp37m‑win32.whl`

## macOS

* Download the latest version of Python 3 for Mac (https://www.python.org/downloads/mac-osx/)
* Open the Terminal app and test that the installation works by typing `python3 -V` and `pip3 -V`
* Use pip to install numpy, scipy and matplotlib
    - Open the Terminal
    - Type `pip3 install numpy`
    - Type `pip3 install scipy`
    - Type `pip3 install matplotlib`
