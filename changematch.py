"""Match git log enties for ethics-relevant changes

Copyright (c) 2019 The University of Texas at Austin. All rights reserved.

Use and redistribution of this file is governed by the license terms in
the LICENSE file found in the project's top-level directory.
"""

import re

COMMIT_MESSAGE_RE = re.compile('\\battack|\\bbreach|\\bbruteforce|\\bbrute force|\\bcrypto|\\bexploit|\\bfirewall|\\bhole|\\bleak|\\bmalicious|\\bman-in-the-middle|\\bmitm|\\bpenetration|\\bprivacy|\\bquarantine|\\bsabotage|\\bsecur|\\bspoof|\\btamper|\\btrojan|\\btrust|\\bunauthorized|\\bvirus', re.IGNORECASE)

# Some keywords from the Data Protection RDF draft
#COMMIT_MESSAGE_RE = re.compile('\\bbreach|\\bconsent|\\bdata protection|\\berasure|\\blawful|\\bpersonal data|\\bprivacy|\\bsecur|\\btransparency|\\btrust', re.IGNORECASE)


def log_entry_matches(log_entry):
    """If given git log entry is of interest, retun true"""
    if 'commit message' in log_entry:
        if COMMIT_MESSAGE_RE.search(log_entry['commit message']) is not None:
            return True
    return False
