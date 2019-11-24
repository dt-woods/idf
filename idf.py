#!/usr/bin/python
#
# idf.py
#
# VERSION: 0.4
#
# LAST EDIT: 2019-11-24
#
###############################################################################
# PUBLIC DOMAIN NOTICE                                                        #
###############################################################################
# This software is freely available to the public for use.                    #
#                                                                             #
# Although all reasonable efforts have been taken to ensure the accuracy and  #
# reliability of the software, the author does not and cannot warrant the     #
# performance or results that may be obtained by using this software.         #
# The author disclaims all warranties, express or implied, including          #
# warranties of performance, merchantability or fitness for any particular    #
# purpose.                                                                    #
#                                                                             #
# Please cite the author in any work or product based on this material.       #
#    Tyler W. Davis                                                           #
#    * based on Precip.py (2015) by Tyler Davis, USDA- Agricultural Research  #
#      Service, 538 Tower Road, Ithaca NY, 14853                              #
#    * based on Precip.m (2011--2012) by Tyler Davis, University of           #
#      Pittsburgh, Department of Civil & Environmental Engineering,           #
#      3700 O'Hara Street, Pittsburgh, PA 15261                               #
###############################################################################
#
###############################################################################
# REQUIRED MODULES:
###############################################################################
from copy import copy  # used in exec functions
import datetime
import os.path

import numpy
import scipy.stats
import matplotlib

# Address issues with backend: (source: Rolf of Saxony on stackoverflow)
for gui in matplotlib.rcsetup.interactive_bk:
    try:
        matplotlib.use(gui,warn=False, force=True)
        from matplotlib import pyplot as plt
        break
    except:
        continue
print("Using:",matplotlib.get_backend())


###############################################################################
# FUNCTIONS:
###############################################################################
def make_plot(mat, dur, lab):
    """
    Name:     make_plot
    Input:    - numpy.ndarray, IDF matrix (mat)
              - numpy.ndarray, durations (dur)
              - list, labels (lab)
    Output:   None
    Features: Creates a plot of IDF
    """
    fig = plt.figure(figsize=(8, 8), dpi=180)

    ax1 = fig.add_subplot(111)
    plt.setp(ax1.get_xticklabels(), rotation=0, fontsize=12)
    plt.setp(ax1.get_yticklabels(), rotation=0, fontsize=12)
    m, n = mat.shape
    for i in range(n):
        ax1.loglog(dur, mat[:, i], label=lab[i])
    ax1.set_ylabel('Rainfall (in/hr)', fontsize=12)
    ax1.set_xlabel('Duration (min)', fontsize=12)
    ax1.grid(True, which='both')

    ax1.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
               ncol=6, mode="expand", borderaxespad=0., fontsize=12)
    plt.xlim([5e0, 1.5e3])
    plt.show()


def make_regular_ts(x):
    """
    Name:     make_regular_ts
    Input:    numpy.ndarray, original data (x)
    Output:   numpy.ndarray, processed data
    Features: Creates a regular time series based on the mode of the timedeltas
    """
    ts_orig = x['timestamps']
    data_orig = x['rain']
    ts_deltas = []
    for i in range(1, len(ts_orig)):
        deltat = (ts_orig[i] - ts_orig[i-1]).total_seconds()/3600.0
        ts_deltas.append(deltat)

    ts_deltas = numpy.array(ts_deltas)

    # Use mode as the regular interval
    ts_mode = scipy.stats.mode(ts_deltas, axis=None)[0][0]

    # Iterate through time, gap fill with zeros, average over smaller intervals
    ts_start = ts_orig[0]
    ts_end = ts_orig[-1]
    ts_curr = ts_start
    ts_time = [ts_start, ]
    ts_data = [data_orig[0], ]
    while ts_curr < ts_end:
        ts_temp = ts_curr + datetime.timedelta(hours=ts_mode)
        ts_time.append(ts_temp)
        if ts_temp in ts_orig:
            # The next timestamp already exists, set it as current!
            ts_index = numpy.where(ts_orig == ts_temp)[0][0]
            ts_data.append(data_orig[ts_index])
            ts_curr = ts_temp
        else:
            # Did we over or undershoot?
            ts_look = numpy.where((ts_orig > ts_curr) & (ts_orig <= ts_temp))
            if len(ts_look[0]) > 0:
                # We overshot, time to average!
                ts_ave = data_orig[ts_look].mean()
                ts_data.append(ts_ave)
                ts_curr = ts_temp
            else:
                # We undershot, time to gapfill!
                ts_data.append(0.0)
                ts_curr = ts_temp

    # Regroup data into numpy array:
    for i in range(len(ts_data)):
        var_params = (ts_time[i], ts_data[i])
        if i == 0:
            my_data = numpy.array(
                var_params,
                dtype={'names': ('timestamps', 'rain'),
                       'formats': ('O', 'f4')},
                ndmin=1
            )
        else:
            my_temp = numpy.array(
                var_params,
                dtype={'names': ('timestamps', 'rain'),
                       'formats': ('O', 'f4')},
                ndmin=1
            )
            my_data = numpy.append(my_data, my_temp, axis=0)

    return my_data


def string_to_date(x):
    """
    Name:     string_to_date
    Input:    string (x)
    Output:   datetime.datetime (d)
    Features: Returns datetime object for a timestamp string
              Updated with UTF-8 decoding for Python 3
    """
    try:
        d = datetime.datetime.strptime(x.decode('utf-8'), '%Y-%m-%d %H:%M')
    except ValueError:
        # Take another crack at it:
        try:
            d = datetime.datetime.strptime(x, '%m/%d/%Y %H:%M')
        except:
            raise ValueError("Error! Could not process time stamp!")
    except:
        raise ValueError("Error! Could not process time stamp!")
    else:
        return d


def usgs_to_csv(filepath):
    """
    Name:     usgs_to_csv
    Inputs:   str, filepath to USGS rainfall data file
    Outputs:  str, formatted output file path
    Features: Processes a tab-separated USGS rainfall data file to CSV format
    Depends:  - writeline
              - writeout
    """
    outfile = None
    if os.path.isfile(filepath):
        # Prepare the output file (preserve original)
        headerline="datetime,rainfall\n"
        outfile = ''.join([filepath, ".csv"])
        writeout(outfile, headerline)

        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith("U"):
                    my_items = line.split("\t")
                    # usgs file should have six columns beginning with 'USGS'
                    # save only the datetime and rainfall amounts (cols 2&4)
                    my_data = ','.join((my_items[2], my_items[4])) + '\n'
                    writeline(outfile, my_data)
    return outfile


def writeline(f, d):
    """
    Name:     writeline
    Input:    - str, file name with path (f)
              - str, data to be written to file (d)
    Output:   None
    Features: Appends an existing file with data string
    """
    try:
        with open(f, 'a') as my_file:
            my_file.write(d)
    except:
        raise IOError("Can not write to output file.")


def writeout(f, d):
    """
    Name:     writeout
    Input:    - str, file name with path (f)
              - str, data to be written to file (d)
    Output:   None
    Features: Writes new/overwrites existing file with data string
    """
    try:
        with open(f, 'w') as my_file:
            my_file.write(d)
    except:
        raise IOError("Can not write to output file.")


###############################################################################
# CLASSES:
###############################################################################
class PrecipEvent:
    """
    Name:     PrecipEvent
    Features: This class handles rain events
    History:  Version 0.3.1
              - updated minimum storm duration to five minutes [19.03.13]
    """
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Variable Initialization
    # ////////////////////////////////////////////////////////////////////////
    MINIMUM_DURATION = 5.0/60.0  # hours

    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Class Initialization
    # ////////////////////////////////////////////////////////////////////////
    def __init__(self, is_rate):
        """
        Name:     PrecipEvent.__init__
        Input:    is_rate, bool:
                    True - data is a rate (i.e., in/hr)
                    False - data is amount (i.e., in)
        Output:   None
        Features: Initializes a PrecipEvent class object
        """
        # Initialization:
        self.time = []       # list of timestamps for rain event
        self.rain = []       # list of rainfall quantities for rain event
        self.duration = 0    # duration of rain event (hrs)
        self.points = 0      # number of data points found for rain event
        self.total_rain = 0  # total rainfall amount (inches)
        self.IDFdurations = []  # list of durations for IDF analysis
        self.IDFrainfalls = []  # list of max rainfalls for each IDF duration

        # Set integration method based on source:
        self.is_rate = is_rate

    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # Class Function Definitions
    # ////////////////////////////////////////////////////////////////////////
    def calc_duration(self):
        """
        Name:     PrecipEvent.calc_duration
        Features: Calculates the storm duration in hours
        """
        if len(self.time) > 1:
            # Due to the ambiguity of when rainfall actually starts (i.e.,
            # sometime between self.time[0] and self.time[1]) and when it
            # ends (i.e., sometime between self.time[-2] and self.time[-1]),
            # this method makes the following assumption:
            #   1. rainfall begins immediately before the first indication
            #   2. rainfall ends immediately after the last indication
            #   3. the minumum duration for an event is defined above
            rain_array = numpy.array(self.rain)
            rain_events = numpy.where(rain_array > 0)[0]
            start_index = rain_events[0]
            end_index = rain_events[-1]
            if start_index != end_index:
                start_time = self.time[start_index]
                end_time = self.time[end_index]
                self.duration = (end_time - start_time).total_seconds()/3600.0
            else:
                # Found single positive rain event:
                self.duration = self.MINIMUM_DURATION
        else:
            self.duration = 0.0

    def calc_points(self):
        """
        Name:     PrecipEvent.calc_points
        Input:    None.
        Output:   int, number of points
        Features: Calculates the total number of points found for rain event
        """
        if len(self.time) == len(self.rain):
            self.points = len(self.time)
            return len(self.time)
        else:
            print("Warning! Timestamps and rainfall amounts are unmatched!")

    def calc_total_rain(self, start=None, end=None):
        """
        Name:     PrecipEvent.calc_total_rain
        Input:    - m, starting index
                  - n, ending index
        Features: Calculates the total rainfall amount based on the units of
                  data
        """
        # set starting index
        if start is None:
            m = 0
        else:
            m = int(start)

        # set ending index
        if end is None:
            n = self.calc_points()
            n -= 1
        else:
            n = int(end)

        if m > n:
            raise ValueError("Ending index must be after starting index!")
        if n > self.points-1:
            raise ValueError("Out of index error")

        if m == n:
            self.total_rain = 0.0
        elif self.is_rate:
            self.total_rain = 0.0
            for i in range(m, n):
                # Rainfall data is given in units of in/hr, use the trapezoidal
                # rule for non-uniform grids:
                delta_t = (
                    self.time[i+1] - self.time[i]).total_seconds()/3600.0
                self.total_rain += 0.5*(self.rain[i] + self.rain[i+1])*delta_t
        else:
            # Rainfall data is given as total rainfall per unit time (in)
            rain_amounts = numpy.array(self.rain[m:n])
            self.total_rain = rain_amounts.sum()


###############################################################################
# MAIN:
###############################################################################
if __name__ == '__main__':
    # Assume text file is in local directory (same as script)
    usgs_file = "nwis.waterdata.usgs.gov"
    fname = usgs_to_csv(usgs_file)

    if os.path.isfile(fname):
        try:
            temp = numpy.loadtxt(
                fname,
                dtype={'names': ('timestamps', 'rain'),
                       'formats': ('O', 'f4')},
                delimiter=",",
                skiprows=1,
                usecols=(0,1),
                converters={0: lambda x: string_to_date(x),
                            1: numpy.float}
            )
        except:
            raise IOError("Could not read the input file. Check your format")
    else:
        raise IOError("Could not find input file. Check filename and path.")

    # Verbose mode
    verbose = True

    # Make data into a regular time series:
    # data = make_regular_ts(temp)
    data = numpy.copy(temp)

    # Define total number of lines read:
    numtotal = data.shape[0]

    # Define minimum interevent time (MIT), hours:
    mit = 5

    # Initialize last heard tracker & rain event counter:
    lastheard = data['timestamps'][0] - datetime.timedelta(hours=mit+1)
    rainevent = 1

    # Filter rainfalls and create storm event objects:
    for i in range(1, numtotal):
        if data['rain'][i] > 0 and data['rain'][i-1] == 0:
            # This is the start of a rain event!

            # Save the start time for the storm event:
            stormstart = data['timestamps'][i]

            # Check to see if the MIT requirement is met:
            delta_t = (stormstart - lastheard).total_seconds()/3600.0

            if delta_t <= mit:
                # Found a short break in the storm; still in previous event:
                rainevent -= 1
                if verbose:
                    print("Still in event %d: %s, last heard %0.3f hrs" % (
                        rainevent, stormstart, delta_t))

                # Include the starting zero event:
                tprev = data['timestamps'][i-1]
                rprev = data['rain'][i-1]
                exec((
                    "if Event%d.time[-1] != tprev:\n"
                    "    Event%d.time.append(data['timestamps'][i-1])\n"
                    "    Event%d.rain.append(data['rain'][i-1])\n"
                    ) % (rainevent, rainevent, rainevent))

                # Initialize the current rain events rainfall amount:
                eventrain = data['rain'][i]

                # Initialize the iterater:
                j = 0

                while (eventrain > 0):
                    # Save the time and rain amounts for the event:
                    exec("Event%d.time.append(data['timestamps'][i+j])" % (
                        rainevent))
                    exec("Event%d.rain.append(data['rain'][i+j])" % (
                        rainevent))

                    # Increment the iterater & update event rainfall:
                    j += 1
                    eventrain = data['rain'][i+j]

                # Include the ending zero event:
                exec("Event%d.time.append(data['timestamps'][i+j])" % (
                    rainevent))
                exec("Event%d.rain.append(data['rain'][i+j])" % (
                    rainevent))

                # Update lastheard date:
                exec("lastheard = Event%d.time[-1]" % (rainevent))

                # Increment the event couter:
                rainevent += 1

            else:
                if verbose:
                    print("Start rain event %d: %s, last heard %0.3f hrs" % (
                        rainevent, stormstart, delta_t))

                # Initialize event object arrays:
                # Note, set the rainfall rate boolean here
                exec("Event%d = PrecipEvent(is_rate=%s)" % (rainevent, False))

                # Include the starting zero event:
                exec("Event%d.time.append(data['timestamps'][i-1])" % (
                    rainevent))
                exec("Event%d.rain.append(data['rain'][i-1])" % (
                    rainevent))

                # Initialize the current rain events rainfall amount:
                eventrain = data['rain'][i]

                # Initialize the iterater:
                j = 0

                while (eventrain > 0):
                    # Save the time and rain amounts for the event:
                    exec("Event%d.time.append(data['timestamps'][i+j])" % (
                        rainevent))
                    exec("Event%d.rain.append(data['rain'][i+j])" % (
                        rainevent))

                    # Increment the iterater & update event rainfall:
                    j += 1
                    eventrain = data['rain'][i+j]

                # Include the ending zero event:
                exec("Event%d.time.append(data['timestamps'][i+j])" % (
                    rainevent))
                exec("Event%d.rain.append(data['rain'][i+j])" % (
                    rainevent))

                # Update lastheard date:
                exec("lastheard = Event%d.time[-1]" % (rainevent))

                # Increment the event couter:
                rainevent += 1

    all_durations = []
    # Calculate event totals:
    for i in range(1, rainevent):
        exec("Event%d.calc_total_rain()" % (i))
        exec("Event%d.calc_duration()" % (i))
        exec("all_durations.append(Event%d.duration)" % (i))
        if verbose:
            print(
                "%02d %s -- %s  (%6.2f hours); %6.2f inches" % (
                    i,
                    eval("Event%d.time[0]" % (i)),
                    eval("Event%d.time[-1]" % (i)),
                    eval("Event%d.duration" % (i)),
                    eval("Event%d.total_rain" % (i))
                    )
            )

    maxduration = numpy.array(all_durations).max()


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    # IDF ANALYSIS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
    # Define durations (min) for analyzing:
    durations = [5, 15, 30, 60, 120, 180, 720, 1440]
    num_durs = len(durations)

    # Initialize all event IDF durations and rainfalls:
    for i in range(1, rainevent):
        exec("Event%d.IDFdurations = numpy.array(durations)" % (i))
        exec("Event%d.IDFrainfalls = numpy.zeros(num_durs)" % (i))

    for n in range(num_durs):
        curdur = durations[n]/60.0  # current duration in hours

        # Initialize event list:
        exec("all%dMINevents = numpy.zeros(rainevent-1)" % (durations[n]))

        # Iterate over each rain event
        for j in range(1, rainevent):
            # Save the total rain event time (in hours) & event points:
            eventtime = eval("Event%d.duration" % (j))
            eventpoints = eval("Event%d.points" % (j))

            # Initialize a max value at the beginning of the event:
            eventDmax = 0

            # Check the rain event duration:
            if eventtime <= curdur:
                # Rain event was less than the duration, set equal to total:
                exec("Event%d.calc_total_rain()" % (j))
                eventDmax = eval("copy(Event%d.total_rain)" % (j))
                exec("Event%d.IDFrainfalls[%d] = copy(eventDmax)" % (j, n))
            else:
                # The event was longer than duration, search through the event
                # to find the event max.

                # Iterate through the event with a moving window, where the
                # starting index is eventDa.
                all_events = []
                for eventDa in range(eventpoints-2):
                    # Find the ending index that corresponds to the current
                    # duration. Start by setting the end index to one larger
                    # than the start point
                    eventDe = eventDa+1
                    eventDdurn = eval(
                        ("(Event%d.time[eventDe] - "
                         "Event%d.time[eventDa]).total_seconds()/3600.0"
                         ) % (j, j))
                    while eventDdurn <= curdur:
                        # Set a break condition if we've reached the end of the
                        # rainfall time series:
                        if eventDe > eventpoints-1:
                            break

                        # Update event duration (eventDdurn):
                        eventDdurn = eval(
                            ("(Event%d.time[eventDe] - "
                             "Event%d.time[eventDa]).total_seconds()/3600.0"
                             ) % (j, j))
                        eventDe += 1

                    # Calculate the duration rainfall amount:
                    exec("Event%d.calc_total_rain(%d, %d)" % (
                        j, eventDa, eventDe-1))
                    eventDrain = eval("copy(Event%d.total_rain)" % (j))
                    all_events.append(eventDrain)

                # Define the duration (hr) storm as the maximum:
                eventDmax = numpy.array(all_events).max()
                exec("Event%d.IDFrainfalls[%d] = copy(eventDmax)" % (j, n))

            # Save the event total:
            exec("all%dMINevents[%d] = eventDmax" % (durations[n], j-1))


    # ~~~~~~~~~~~~~~~
    # IDF PROBABILITY
    # ~~~~~~~~~~~~~~~
    # Create the intensity-duration matrix (3 x durations)
    #   row 1 = duration (min)
    #   row 2 = max rainfall amount (in)
    #   row 3 = associated rainfall intensity (in/hr)
    idc = numpy.zeros(shape=(3, num_durs))

    for d in range(num_durs):
        # Calculate the maximum rainfall amounts for each duration:
        exec("max%dMINrain = all%dMINevents.max()" % (
            durations[d], durations[d]))

        # Put together the IDC curve matrix:
        idc[0, d] = durations[d]  # duration length (min)
        idc[1, d] = eval("max%dMINrain" % (durations[d]))  # precip (in)
        idc[2, d] = idc[1, d]/(durations[d]/60.0)  # intensity (in/hr)

        # Convert events to integers for histogram to work with reason.
        exec("all%dMINints = [int(1000*i) for i in all%dMINevents]" % (
            durations[d], durations[d]))

        # Determine PDF for each discrete rainfall amount:
        exec("b%dMIN = sorted(list(set(all%dMINints)))" % (
            durations[d], durations[d]))
        exec("my_bins = numpy.bincount(all%dMINints)" % (durations[d]))
        exec("f%dMIN = [my_bins[i] for i in b%dMIN]" % (
            durations[d], durations[d]))
        exec("my%dpdf = [float(i)/(rainevent - 1) for i in f%dMIN]" % (
            durations[d], durations[d]))
        my_bins = numpy.array([])

        # Compute the CPF:
        exec("my%dcpf = numpy.zeros(len(my%dpdf))" % (
            durations[d], durations[d]))
        exec("my%dcpf[0] = my%dpdf[0]" % (durations[d], durations[d]))
        exec(("for k in range(1, len(my%dpdf)):\n"
              "    my%dcpf[k] = my%dcpf[k-1] + my%dpdf[k]\n"
              ) % (durations[d], durations[d], durations[d], durations[d]))


    # ~~~~~~~~~~~~~~~~~
    # COMPUTE IDF CURVE
    # ~~~~~~~~~~~~~~~~~
    # IDF matrix:
    # -------------------------------------------------------------------- #
    #                               F R E Q U E N C Y
    #                    2-yr   5-yr   10-yr   25-yr   50-yr   100-yr
    # D     5-min ....                                               .....
    # U    15-min ....                                               .....
    # R    30-min ....       RAIN INTENSITIES CORRESPONDING          .....
    # A    60-min ....             TO THE RETURN PERIOD              .....
    # T   120-min ....                  PROBABILITY                  .....
    # I   180-min ....                                               .....
    # O   720-min ....                                               .....
    # N  1440-min ....                                               .....
    # -------------------------------------------------------------------- #

    # Define the return periods (myfreqT) and their CDF equivalents:
    myfreqT = [2, 5, 10, 25, 50, 100]
    myfreqs = [0.50, 0.80, 0.90, 0.96, 0.98, 0.99]

    idf = numpy.zeros(shape=(len(durations), len(myfreqs)))

    # Calculate the rainfall intensity (in/hr) for each return period
    # probability, using linear interpolation. Remember to scale down the
    # rainfall.
    for d in range(num_durs):
        for q in range(len(myfreqs)):
            p = myfreqs[q]
            idf[d][q] = eval((
                "(60*1e-3/durations[d])*numpy.interp(p, my%dcpf, b%dMIN)"
                ) % (durations[d], durations[d]))

    # ~~~~~~~~~~~~~~
    # PLOT IDF CURVE
    # ~~~~~~~~~~~~~~
    my_labels = [(str(i) + "-yr") for i in myfreqT]
    durations = numpy.array(durations)
    make_plot(idf, durations, my_labels)
