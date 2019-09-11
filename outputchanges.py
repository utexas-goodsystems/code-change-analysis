"""Scan source code change history for ethics-relevant changes, write to stdout
in CSV format, and display a plot.

Copyright (c) 2019 The University of Texas at Austin. All rights reserved.

Use and redistribution of this file is governed by the license terms in
the LICENSE file found in the project's top-level directory.
"""

import sys
import os
import csv
import datetime
import matplotlib.pyplot as pyplot
import matplotlib.ticker as ticker
import numpy as np
import matplotlib.dates as mdates


def plot_timeline(git_log, filtered_log, argv):
    names = [entry['commit'][:7] for entry in filtered_log]
    dates = [entry['author.date'] for entry in filtered_log]

    # Derived from excerpt of Matplotlib timeline example:
    # https://matplotlib.org/gallery/lines_bars_and_markers/timeline.html

    fig, ax = pyplot.subplots(figsize=(8.8, 4), constrained_layout=True)
    levels = np.tile([-5, 5, -3, 3, -1, 1],
                     int(np.ceil(len(dates) / 6)))[:len(dates)]

    ax.set(
        title=os.path.basename(os.getcwd()) +
        ' Possible Security-Relevant Commits')
    markerline, stemline, baseline = ax.stem(
        dates, levels, linefmt='C3-', basefmt='k-', use_line_collection=True)
    pyplot.setp(markerline, mec='k', mfc='w', zorder=3)
    markerline.set_ydata(np.zeros(len(dates)))
    vert = np.array(['top', 'bottom'])[(levels > 0).astype(int)]
    for d, l, r, va in zip(dates, levels, names, vert):
        ax.annotate(
            r,
            xy=(d, l),
            xytext=(-3, np.sign(l) * 3),
            textcoords='offset points',
            va=va,
            ha='right')

    # format xaxis with 4 month intervals
    ax.get_xaxis().set_major_locator(mdates.MonthLocator(interval=4))
    ax.get_xaxis().set_major_formatter(mdates.DateFormatter('%b %Y'))
    pyplot.setp(ax.get_xticklabels(), rotation=30, ha='right')

    ax.get_yaxis().set_visible(False)
    for spine in ['left', 'top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.margins(y=0.1)


def start_of_quarter(dt):
    start_month = (dt.month - 1) // 3 * 3 + 1
    return dt.replace(
        month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)


def start_of_next_quarter(dt):
    start_month = ((dt.month - 1) // 3 + 1) * 3 + 1
    if start_month == 13:
        return dt.replace(
            year=dt.year + 1,
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0)
    else:
        return dt.replace(
            month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)


def plot_histogram(git_log, filtered_log, argv):
    all_dates = [
        mdates.date2num(entry['author.date'].astimezone(datetime.timezone.utc))
        for entry in git_log
    ]
    filtered_dates = [
        mdates.date2num(entry['author.date'].astimezone(datetime.timezone.utc))
        for entry in filtered_log
    ]

    pyplot.style.use('bmh')
    fig, ax = pyplot.subplots(figsize=(8.8, 4), constrained_layout=True)

    ax.set(
        title=os.path.basename(os.getcwd()) +
        ' Possible Security-Relevant Commits')

    all_dates_counts, bins = np.histogram(all_dates, bins=36)
    print('all_dates_counts', all_dates_counts)
    print('bins', bins)
    filtered_dates_counts, _ = np.histogram(filtered_dates, bins=bins)
    print('filtered_dates_counts', filtered_dates_counts)
    scale_factor = max(filtered_dates_counts) / max(all_dates_counts)
    print('scale_factor', scale_factor)
    all_dates_counts_scaled = [x * scale_factor for x in all_dates_counts]
    print('all_dates_counts_scaled', all_dates_counts_scaled)

    pyplot.hist(
        bins[:-1], bins, weights=filtered_dates_counts, histtype='stepfilled')
    pyplot.hist(
        bins[:-1], bins, weights=all_dates_counts_scaled, histtype='step')

    #binvals1, bins1, _ = ax.hist(filtered_dates, bins=bins1, histtype='stepfilled')
    #ax.hist(all_dates, bins=36, weights=all_dates_weights, histtype='step')

    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    pyplot.setp(ax.get_xticklabels(), rotation=30, ha='right')

    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)


def outputchanges(git_log, filtered_log, argv):
    #print('Of ' + str(len(git_log)) + ' entries, ' + str(len(filtered_log)) +
    #      ' match.')

    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=['commit', 'author.date', 'commit message'],
        extrasaction='ignore')
    writer.writeheader()
    for entry in filtered_log:
        writer.writerow(entry)

    #plot_timeline(git_log, filtered_log, argv)
    plot_histogram(git_log, filtered_log, argv)
    pyplot.show()
