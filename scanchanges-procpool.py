#!/usr/local/bin/python3
"""Scan source code change history for ethics-relevant changes, write to stdout
in CSV format, and display a plot.

Copyright (c) 2019 The University of Texas at Austin. All rights reserved.

Use and redistribution of this file is governed by the license terms in
the LICENSE file found in the project's top-level directory.
"""

import sys
import os
import gitutils
import concurrent.futures
import itertools
import changematch
import csv
import matplotlib.pyplot as pyplot
import numpy as np
import matplotlib.dates as mdates


def main(argv=None):
    if argv is not None:
        os.chdir(argv[1])
    git_log = gitutils.get_git_log()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        filtered_log = list(itertools.compress(git_log, executor.map(changematch.log_entry_matches, git_log)))

    #print('Of ' + str(len(git_log)) + ' entries, ' + str(len(filtered_log)) +
    #      ' match.')

    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=['commit', 'author.date', 'commit message'],
        extrasaction='ignore')
    writer.writeheader()
    for entry in filtered_log:
        writer.writerow(entry)

    names = [entry['commit'][:7] for entry in filtered_log]

    dates = [entry['author.date'] for entry in filtered_log]

    # Derived from excerpt of Matplotlib timeline example:
    # https://matplotlib.org/gallery/lines_bars_and_markers/timeline.html
    
    fig, ax = pyplot.subplots(figsize=(8.8, 4), constrained_layout=True)
    levels = np.tile([-5, 5, -3, 3, -1, 1],
                        int(np.ceil(len(dates) / 6)))[:len(dates)]

    ax.set(title=os.path.basename(os.getcwd()) + ' Security-Relevant Commits')
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
    pyplot.show()

    # End Matplotlib timeline example excerpt

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
