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
import outputchanges


def main(argv=None):
    if argv is not None:
        os.chdir(argv[1])
    git_log = gitutils.get_git_log()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        filtered_log = list(
            itertools.compress(git_log,
                               executor.map(changematch.log_entry_matches,
                                            git_log)))

    outputchanges.outputchanges(git_log, filtered_log, argv)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
