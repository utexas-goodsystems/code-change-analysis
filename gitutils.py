"""git log utilities

Copyright (c) 2019 The University of Texas at Austin. All rights reserved.

Use and redistribution of this file is governed by the license terms in
the LICENSE file found in the project's top-level directory.
"""

import sys
import subprocess
import datetime
import tzutils


def get_git_log():
    """"Retrieve the git log in the current repo as a list of commits"""
    git_log_out = subprocess.run(
        ['git', 'log', '--pretty=raw', '--no-color', '--encoding=UTF-8', '-z'],
        check=True,
        stdout=subprocess.PIPE,
        stderr=sys.stderr.fileno(),
        encoding='utf-8',
        errors='ignore',
    ).stdout
    git_log_split = git_log_out.split('\0')
    git_log = []
    for entry in git_log_split:
        header_cmtmsg = tuple(entry.rstrip('\n').split('\n\n', 1))
        headers = header_cmtmsg[0].replace('\n', '\0').replace('\0 ',
                                                               '\n').split('\0')
        log_entry = {}
        if len(header_cmtmsg) >= 2:
            log_entry['commit message'] = header_cmtmsg[1].replace(
                '    ', '', 1).replace('\n    ', '\n')
        for header in headers:
            s = header.split(' ', 1)
            log_entry[s[0]] = s[1]
        if 'committer' in log_entry:
            s = log_entry['committer'].rsplit(' ', 3)
            log_entry['committer.name'] = s[0]
            log_entry['committer.email'] = s[1]
            log_entry['committer.date'] = datetime.datetime.fromtimestamp(
                float(s[2]), tzutils.get_tz_for_offset(s[3]))
        if 'author' in log_entry:
            s = log_entry['author'].rsplit(' ', 3)
            log_entry['author.name'] = s[0]
            log_entry['author.email'] = s[1]
            log_entry['author.date'] = datetime.datetime.fromtimestamp(
                float(s[2]), tzutils.get_tz_for_offset(s[3]))
        git_log.append(log_entry)
    return git_log
