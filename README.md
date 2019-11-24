# idf
Rainfall intensity duration frequency (IDF) curve calculation and plotting

# Repository Details

* STATUS: Active
* LATEST RELEASE: v.0.4
* LAST UPDATED: 2019-11-24
* LICENSE: Public Domain (except where otherwise noted)
* URL: https://github.com/dt-woods/idf

# Contents

idf.py

- Python script for reading precipitation data, identifying rainfall events, and computing/plotting the IDF curve

# Changelog

* 2019-11-24: v.0.4
    - added three new functions: usgs_to_csv, writeout, writeline
    - removed file path variables (assumes rainfall file is in local dir)
    - new workflow: reads tab-separated usgs rain gage file, processes to csv, runs idf
* 2019-03-23: v.0.3.1
* 2019-03-22: v.0.3.0-dev

# Install

This script was tested using Python 3.6.7 and requires the installation of the following third-party packages (version numbers have been successfully tested).

* numpy (1.16.2)
* scipy (1.2.1)
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
