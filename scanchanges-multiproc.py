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
import multiprocessing
from multiprocessing.managers import BaseManager
from queue import SimpleQueue
import changematch
import outputchanges
import time


class JobObjectsManager(BaseManager):
    """Shared object manager for a scanchanges cluster job"""

    work_queue = SimpleQueue()
    result_queue = SimpleQueue()

    @classmethod
    def new_server_manager(cls, *args, **kwds):
        cls.register('get_work_queue', callable=lambda: cls.work_queue)
        cls.register('get_result_queue', callable=lambda: cls.result_queue)
        return cls(*args, **kwds)

    @classmethod
    def new_client_stub(cls, *args, **kwds):
        cls.register('get_work_queue')
        cls.register('get_result_queue')
        return cls(*args, **kwds)


def run_leader(address, authkey):
    """Run the leader, which adds work items to the work queue, retreives
    all the results from the result queue, and calls outputchanges on the
    results."""
    shared_objects = JobObjectsManager.new_server_manager(
        address=address, authkey=authkey)
    with shared_objects:  # Starts server, and shuts down on exit
        work_queue = shared_objects.get_work_queue()
        result_queue = shared_objects.get_result_queue()
        git_log = gitutils.get_git_log()
        for log_entry in git_log:
            work_queue.put_nowait(log_entry)
        # A closeable queue would work better here.
        work_queue.put_nowait('END-OF-JOB')
        filtered_log = []
        worker_count = 0
        while True:
            log_entry = result_queue.get()
            if log_entry == 'WORKER-START':
                worker_count += 1
            elif log_entry == 'WORKER-STOP':
                worker_count -= 1
                if worker_count == 0:
                    break
            else:
                filtered_log.append(log_entry)
    outputchanges.outputchanges(git_log, filtered_log, None)


def run_follower(address, authkey):
    """Run a follower, which gets work items from the work queue, calls
    changematch.log_entry_matches on each, and if the result is true,
    puts the work item on the result queue."""
    shared_objects = JobObjectsManager.new_client_stub(
        address=address, authkey=authkey)
    shared_objects.connect()
    work_queue = shared_objects.get_work_queue()
    result_queue = shared_objects.get_result_queue()
    result_queue.put('WORKER-START')
    while True:
        log_entry = work_queue.get()
        if log_entry == 'END-OF-JOB':
            work_queue.put_nowait(log_entry)
            result_queue.put('WORKER-STOP')
            return
        print('Processing', log_entry['commit'])
        if changematch.log_entry_matches(log_entry):
            result_queue.put(log_entry)


def main(argv=None):
    """multiprocessing-based (multiple host) implementation"""
    if len(sys.argv) != 6 or (argv[2] != 'lead' and argv[2] != 'follow'):
        sys.stderr.write(
            'scanchanges: HALT: usage: scanchanges git-dir lead/follow host port authkey\n'
        )
        return 64  # Exit status 64: Command line usage error
    address_host = argv[3]
    address_port = int(argv[4])
    authkey = os.fsencode(argv[5])  # use raw bytes of cmd line argument

    os.chdir(argv[1])

    if argv[2] == 'lead':
        run_leader((address_host, address_port), authkey)
    elif argv[2] == 'follow':
        run_follower((address_host, address_port), authkey)
    else:
        raise AssertionError('Unhandled case: cmd line arg 2')

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
